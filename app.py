# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from word import Analysis
from pymongo import MongoClient

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods = ['GET', 'POST', 'DELETE'])
@app.route('/<message>', methods = ['GET'])
def index(message = None):
    brain = Analysis()
    if request.method == 'GET':
        parsed = brain.parse(message)
        res = brain.answer(parsed)

    if request.method == 'POST':
        message = request.form.get('message')
        parsed = brain.parse(message)
        res = brain.learn(parsed)

    if request.method == 'DELETE':
        message = request.form.get('message')
        parsed = brain.parse(message)
        res = brain.forget(parsed)

    return jsonify(res)

if __name__ == '__main__':
    app.run()
