# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from nobunaga import Nobunaga
import yaml

app = Flask(__name__)

config = yaml.load(open('./config.yml', 'r'))
app.config['MYSQL_DATABASE_USER'] = config['db']['username']
app.config['MYSQL_DATABASE_PASSWORD'] = config['db']['password']
app.config['MYSQL_DATABASE_DB'] = config['db']['database']
app.config['MYSQL_DATABASE_HOST'] = config['db']['hostname']

mysql = MySQL()
mysql.init_app(app)

app.config['JSON_AS_ASCII'] = False

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/log/all")
def all():
    nobunaga = Nobunaga(mysql)
    res = nobunaga.all()

    return json_response(res)

@app.route("/log/error")
def error():
    nobunaga = Nobunaga(mysql)
    res = nobunaga.error()

    return json_response(res)

@app.route('/<message>', methods = ['GET'])
def index(message = None):
    nobunaga = Nobunaga(mysql)
    if request.method == 'GET':
        res = nobunaga.answer(message)

    return json_response(res)


def json_response(res):
    response = jsonify(res)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
