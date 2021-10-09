from flask import Flask, render_template

"""
Задание изображений для редактора ломаной
Редактор ломаной


Визуальное редактирование:
https://yandex.ru/dev/maps/jsapi/doc/2.1/dg/concepts/geoobjects.html#geoobjects__visual_editing



"""

app = Flask(__name__, static_url_path='/static')
pages = "pages"

@app.route('/')
def hello_world():
    return render_template("index.html")



@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()


# @app.before_first_request
# def setup():
#      db.create_all()