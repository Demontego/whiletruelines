import os
import json
import time

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, abort, jsonify, Response, url_for, send_from_directory
from flask_restful import Api, Resource, reqparse, inputs
import certifi
from pymongo import MongoClient
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
import pprint
import io
import random
import string

"""
Задание изображений для редактора ломаной
Редактор ломаной

http://datalytics.ru/all/rabotaem-s-api-google-drive-s-pomoschyu-python/

Визуальное редактирование:
https://yandex.ru/dev/maps/jsapi/doc/2.1/dg/concepts/geoobjects.html#geoobjects__visual_editing
"""


class DB():
    def __init__(self, base, collection):
        self._dbname = self.open_connection(base)
        self._cnt = self.get_database(collection)

    def open_connection(self, base):
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
        return client[base]

    def get_database(self, collection):
        return self._dbname[collection]

    def get_interface(self):
        return self._cnt


class GD():
    scopes = ['https://www.googleapis.com/auth/drive']
    _service_account_file = 'client_secrets.json'

    def __init__(self):
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(r)
        credentials = service_account.Credentials.from_service_account_file(self._service_account_file,
                                                                            scopes=self.scopes)
        SERVICE = build('drive', 'v3', credentials=credentials)
        results = SERVICE.files().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        if results:
            print("Google Drive authorization completed")
        else:
            print("ERROR while Google Drive authorization completed")
        self._service = SERVICE

    def upload_file(self, filename, rand_name):
        folder_id = '1ijJFhCeSRPv6eMXmlhDecba1xeezGdVw'
        name = rand_name + '.' + filename.split('.')[-1]
        file_path = "uploads/" + filename
        file_metadata = {
            'name': name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        r = self._service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # pp.pprint(r)
        return r


MAPS_API_KEY = os.environ.get("MAPS_API_KEY", "54db9319-2b11-4398-92dc-4e58cbedace4")
CONNECTION_STRING = os.environ.get("MONGODB_URI",
                                   "mongodb+srv://myasnikov-rs:Otukjdf123@cluster0.5iplt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = set(
    ['txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ecw', 'gif', 'ico', 'ilbm', 'jpeg', 'mrsid', 'pcx', 'png', 'psd',
     'tga', 'tiff', 'webp', 'xbm', 'xps', 'rla', 'rpf', 'pnm', 'rtf'])
# print("--VARS--")
# os.environ.get("MAPS_API_KEY", "NONE")
# os.environ.get("MONGODB_URI", "NONE")
# print("----")

database = DB("mainbase", "maincollection").get_interface()
google_drive = GD()
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# TODO Приянть картинку и отправить на гугл диск, в ответе направить id загрузки

# TODO API для нейронки, чтобы по id изменить статус на done

# TODO функция чекер статуса по id

# TODO возвращать картинку в запросе


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        if file and allowed_file(filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            rand_name = ''.join(random.choice(string.hexdigits) for i in range(33))
            resp = google_drive.upload_file(filename, rand_name)
            os.remove(os.path.abspath('uploads/' + filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            result = {
                'name': rand_name,
                'drive_id': resp.get('id', 'upload_error'),
                'status': 'wait',
                'coord': [],
                'tag': 'img'
            }
            database.insert(result)
            return Response(json.dumps({'name': rand_name}), status=201, mimetype='application/json')
    if request.method == 'GET':
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''


@app.route('/')
def index():
    return render_template("index.html", maps_api_key=MAPS_API_KEY)


@app.route('/api/data', methods=['GET', "POST"])
def dataprocessing():
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


@app.route('/api/status_file/<name>', methods=['GET'])
def status_file(name=None):
    if name:
        res = database.find_one({"name": name})
        if res:
            res['_id'] = str(res['_id'])
            return Response(json.dumps(res), status=401)
    return Response(json.dumps({'status': 'error'}), status=401)


@app.route('/api/monitor/shallow', methods=['GET'])
def shallow():
    return Response("Healthy", status=200)


@app.route('/api/info', methods=['GET'])
def info():
    return jsonify({
        "Name": "WhileTrue drawer",
        "Version": "1.0.0",
    })


@app.route('/api/monitor/shallow', methods=['GET'])
def upload_files():
    return Response("Healthy", status=200)


if __name__ == '__main__':
    app.run()
