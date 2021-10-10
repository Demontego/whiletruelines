import os
import json

from flask import Flask, render_template, request, redirect, abort, jsonify, Response
from flask_restful import Api, Resource, reqparse, inputs
import certifi
from pymongo import MongoClient
"""
Задание изображений для редактора ломаной
Редактор ломаной


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


MAPS_API_KEY = os.environ.get("MAPS_API_KEY", "")
CONNECTION_STRING = os.environ.get("MONGODB_URI", "")
database = DB("mainbase", "maincollection").get_interface()
app = Flask(__name__, static_url_path='/static', maps_api_key=MAPS_API_KEY)





@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/data', methods=['GET', "POST"])
def dataprocessing():
    if request.method == "GET":
        result = {"data": "ok2"}
        return Response(json.dumps(result), status=201, mimetype='application/json')
        # return jsonify(result)

    elif request.method == "POST":
        jsonchik = request.get_json()
        if jsonchik:
            database.insert(jsonchik)
            for i in jsonchik:
                print(i)
        else:
            print("Empty data")

        # return Response(json.dumps(jsonchik), status=201, mimetype='application/json')
        # database.insert_many(jsonchik)
        return Response(status=200)


    elif request.method == "DELETE":
        return Response(status=200)
    else:
        abort(400)


@app.route('/api/monitor/shallow', methods=['GET'])
def shallow():
    return Response("Healthy", status=200)


@app.route('/api/info', methods=['GET'])
def info():
    return jsonify({
        "Name": "WhileTrue drawer",
        "Version": "1.0.0",
    })


if __name__ == '__main__':
    app.run()


