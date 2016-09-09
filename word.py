# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
from pymongo import MongoClient
import re
import os

class Analysis(object):
    def __init__(self):
        if os.environ.get('MONGODB_URI'):
            self.db = MongoClient(os.environ.get('MONGODB_URI')).heroku_8n89r7k9
        else:
            self.db = MongoClient().test
        self.t = Tokenizer()

    def parse(self, word):
        self.word = word
        return self.t.tokenize(word)

    def learn(self, tokens):
        error = True
        for token in tokens:
            if re.search(u'代名詞', token.part_of_speech):
                return {
                    'error': error,
                    'message': u'何が言いたいのだ',
                }

            data = {
                'keyword': token.surface,
                'type': token.part_of_speech,
                'origin': self.word,
            }

            result = self.db.word.find_one(data)
            if result is None:
                error = False
                self.db.word.insert_one(data)

        if error:
            return {
                'error': error,
                'message': u'知っておるわ',
            }

        return {
            'error': False,
            'message': u'思い出したぞ・・・',
        }

    def answer(self, tokens):
        query = []
        error = True
        for token in tokens:
            if re.search(u'代名詞', token.part_of_speech):
                error = False
                continue

            if re.search(u'ナニ|ナン|イツ', token.reading):
                error = False
                continue

            data = {
                'keyword': token.surface,
                'type': token.part_of_speech,
            }

            query.append(data)

        if error:
            return {
                'error': error,
                'message': u'何が言いたいのだ',
            }

        results = self.db.word.aggregate([
            {'$match': {'$or': query}},
            {'$group': {'_id': '$origin', 'count': {'$sum': 1}}},
            {'$sort': {'count': 1}}
        ])

        try:
            result = results.next()
        except:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        return {
            'error': False,
            'message': result['_id'],
        }


