import os
import json

from flask import Flask, render_template, request, abort, jsonify, Response, send_from_directory, send_file
from flask_restful import Api, Resource, reqparse, inputs
import certifi
import io
import random
import string
import cv2
from RoadDetection import RoadDetection
import torch

"""
данные в монго
{
  'name': rand_name,
  'driveIn_id': resp.get('id', 'upload_error'), // кто он в папке web
  'driveOut_id': resp.get('id', 'upload_error'), // кто он в папке fromNN
  'status': 'wait',
  'coord': [],
  'tag': 'img'
}
"""
"""
Задание изображений для редактора ломаной
Редактор ломаной

http://datalytics.ru/all/rabotaem-s-api-google-drive-s-pomoschyu-python/

Визуальное редактирование:
https://yandex.ru/dev/maps/jsapi/doc/2.1/dg/concepts/geoobjects.html#geoobjects__visual_editing
"""
device = 'gpu' if torch.cuda.is_available() else 'cpu'
model = RoadDetection(path_model='./best_model_LinkNet34.pth', device=device)



MAPS_API_KEY = os.environ.get("MAPS_API_KEY", "54db9319-2b11-4398-92dc-4e58cbedace4")
UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ecw', 'gif', 'ico', 'ilbm', 'jpeg', 'mrsid', 'pcx',
                      'png', 'psd', 'tga', 'tiff', 'webp', 'xbm', 'xps', 'rla', 'rpf', 'pnm', 'rtf', 'tif'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 80 * 1000 * 1000

# TODO функция чекер статуса по id

# TODO возвращать картинку в запросе


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS




@app.route('/api/upload_file', methods=['POST'])
def upload_file():
    """Interface for NN module. Upload files on google drive and update status of task"""
    if request.method == 'POST':
        file = request.files['file']
        file_ext = file.filename.split('.')[-1]
        jsonchik = request.get_json() if request.get_json() is not None else {}

        if file and allowed_file(file.filename):
            local_name = ''.join(random.choice(string.hexdigits) for i in range(33))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], local_name + f'.{file_ext}'))

            image, mask, heatmap = model.predict(os.path.join(app.config['UPLOAD_FOLDER'], local_name + f'.{file_ext}'))
            os.remove(os.path.abspath('uploads/' + local_name + f'.{file_ext}'))
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name+'_done.jpg'), image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name+'_mask.jpg'), mask)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name+'_heatmap.jpg'), heatmap)
            result = {
                'name_image': local_name+'_done.jpg',
                'name_mask': local_name+'_mask.jpg',
                'name_heatmap': local_name+'_heatmap.jpg',
            }
            return Response(json.dumps(result), status=201, mimetype='application/json')
    return Response(json.dumps({'status': 'error'}), status=400)


@app.route('/old')
def indexold():
    return render_template("maps.html", maps_api_key=MAPS_API_KEY)


@app.route('/')
def index():
    return render_template("index.html", maps_api_key=MAPS_API_KEY)


@app.route('/api/data', methods=['GET', "POST"])
def dataprocessing():
    """старая, для обмена координатами на карту"""
    if request.method == "GET":
        result = [{'name': i['name'], 'coord': i['coord']} for i in database.find()]
        return Response(json.dumps(result), status=201, mimetype='application/json')
    elif request.method == "POST":
        jsonchik = request.get_json()
        if jsonchik:
            database.insert(jsonchik)
            for i in jsonchik:
                print(i)
        else:
            print("Empty data")
        return Response(status=200)
    elif request.method == "DELETE":
        return Response(status=200)
    else:
        abort(400)


@app.route('/api/get_status_file/<name>', methods=['GET'])
def get_status_file(name=None):
    """
    For UI, check status of processing
    """
    if name:
        res = database.find_one({"name": name})
        if res:
            res['_id'] = str(res['_id'])
            return Response(json.dumps(res), status=200)
    return Response(json.dumps({'status': 'error'}), status=400)


@app.route('/api/set_status_file/<name>', methods=['GET', 'POST'])
def set_status_file(name=None):
    """
    For NN-module, set successful status of processing
    """
    if request.method == "GET":
        if name:
            res = database.update_one({'name': name}, {'$set': {'status': 'done'}}).matched_count
            if res:
                return Response(json.dumps({'status': 'ok'}), status=400)
    if request.method == "POST":
        jsonchik = request.get_json()
        if jsonchik:
            res = database.update_one({'name': jsonchik.get('name')},
                                      {'$set': {'status': 'done', 'coord': jsonchik.get('coord')}}).matched_count
            if res:
                return Response(json.dumps({'status': 'ok'}), status=400)
    return Response(json.dumps({'status': 'error'}), status=400)


@app.route('/api/get_queue', methods=['GET'])
def get_queue():
    """
    Return list of objects with status 'wait'
    """
    resp = []
    for i in database.find({'status': 'wait'}):
        i['_id'] = str(i['_id'])
        resp.append(i)
    return Response(json.dumps(resp), status=200)


if __name__ == '__main__':
    app.run()
