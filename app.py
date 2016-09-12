# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from urllib.parse import urlparse
from nobunaga import Nobunaga
import os

mysql = MySQL()
uri = urlparse(os.environ.get('CLEARDB_DATABASE_URL'))
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = uri.username
app.config['MYSQL_DATABASE_PASSWORD'] = uri.password
app.config['MYSQL_DATABASE_DB'] = uri.path[1:]
app.config['MYSQL_DATABASE_HOST'] = uri.hostname
mysql.init_app(app)

app.config['JSON_AS_ASCII'] = False

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/', methods = ['POST', 'DELETE'])
@app.route('/<message>', methods = ['GET'])
def index(message = None):
    nobunaga = Nobunaga(mysql)
    if request.method == 'GET':
        res = nobunaga.answer(message)

    if request.method == 'POST':
        message = request.form.get('message')
        res = nobunaga.learn(message)

    if request.method == 'DELETE':
        message = request.form.get('message')
        res = nobunaga.forget(message)

    response = jsonify(res)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
