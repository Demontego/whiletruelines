import os
import json

from flask import Flask, render_template, request, Response, send_from_directory
import random
import string
import cv2
from geojson import dump

from RoadDetection import RoadDetection
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = RoadDetection(path_model='./best_model_LinkNet34.pth', device=device, img_size=1024)
print('model loaded!')
UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ecw', 'gif', 'ico', 'ilbm', 'jpeg', 'mrsid', 'pcx',
                      'png', 'psd', 'tga', 'tiff', 'webp', 'xbm', 'xps', 'rla', 'rpf', 'pnm', 'rtf', 'tif'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 80 * 1000 * 1000


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

        if file and allowed_file(file.filename):
            local_name = ''.join(random.choice(string.hexdigits) for i in range(33))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], local_name + f'.{file_ext}'))

            image, mask, heatmap,  geojson_data, geojson_show = model.predict(os.path.join(app.config['UPLOAD_FOLDER'], local_name + f'.{file_ext}'))
            os.remove(os.path.abspath('uploads/' + local_name + f'.{file_ext}'))
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name + '_done.jpg'), image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name + '_mask.jpg'), mask)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], local_name + '_heatmap.jpg'), heatmap)
            with open(local_name + '_geoshow.geojson', 'w') as f:
                dump(geojson_show, f)
            with open(local_name + '_geodata.geojson', 'w') as f:
                dump(geojson_data, f)
            result = {
                'name_image': local_name + '_done.jpg',
                'name_mask': local_name + '_mask.jpg',
                'name_heatmap': local_name + '_heatmap.jpg',
                'name_geodata': local_name + '_geodata.geojson',
                'name_geoshow': local_name + '_geoshow.geojson',
            }
            return Response(json.dumps(result), status=201, mimetype='application/json')
    return Response(json.dumps({'status': 'error'}), status=400)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
