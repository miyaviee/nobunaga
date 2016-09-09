# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from word import Analysis
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/', methods = ['POST', 'DELETE'])
@app.route('/<message>', methods = ['GET'])
def index(message = None):
    brain = Analysis()
    if request.method == 'GET':
        tokens = brain.parse(message)
        res = brain.answer(tokens)

    if request.method == 'POST':
        message = request.form.get('message')
        tokens = brain.parse(message)
        res = brain.learn(tokens)

    if request.method == 'DELETE':
        message = request.form.get('message')
        tokens = brain.parse(message)
        res = brain.forget(tokens)

    response = jsonify(res)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
