# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from nobunaga import Nobunaga
import yaml

config = yaml.load(open('./config.yml', 'r'))

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = config['db']['username']
app.config['MYSQL_DATABASE_PASSWORD'] = config['db']['password']
app.config['MYSQL_DATABASE_DB'] = config['db']['database']
app.config['MYSQL_DATABASE_HOST'] = config['db']['hostname']
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
        data = message.split('@')
        res = nobunaga.learn(data[0], data[1])

    if request.method == 'DELETE':
        message = request.form.get('message')
        res = nobunaga.forget(message)

    response = jsonify(res)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
