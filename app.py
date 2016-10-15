# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from lib.nobunaga import Nobunaga
from janome.tokenizer import Tokenizer
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

tokenizer = Tokenizer()

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/log")
@app.route("/log/<word>")
def log(word = None):
    nobunaga = Nobunaga(mysql)
    res = nobunaga.showlog(word)

    return json_response(res)

@app.route('/<message>', methods = ['GET'])
def index(message = None):
    nobunaga = Nobunaga(mysql, tokenizer)
    tokens = nobunaga.parse(message)
    query = nobunaga.query(tokens)
    result = nobunaga.search(query)

    return json_response(nobunaga.answer(message, query, result))

def json_response(res):
    response = jsonify(res)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
