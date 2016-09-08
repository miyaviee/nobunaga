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
        word = re.sub(u'(織田)?信長は', '', word)
        parsed = {'word': word}
        for token in self.t.tokenize(word):
            if re.search(u'終助詞|記号', token.part_of_speech):
                continue

            if re.search(u'代名詞|副詞|連体詞|副助詞', token.part_of_speech):
                if 'word' in parsed:
                    del parsed['word']
                continue

            if re.search(u'ナニ|ナン', token.reading):
                if 'word' in parsed:
                    del parsed['word']
                continue

            parsed[token.surface] = token.part_of_speech

        return parsed

    def learn(self, parsed):
        res = {'error': False}
        if 'word' not in parsed:
            res['message'] = u'何が言いたいのだ'
            return res

        know = self.db.word.find_one(parsed)
        if know is not None:
            res['message'] = u'知っておるわ'
            return res

        self.db.word.insert_one(parsed)

        res['message'] = u'思い出したぞ・・・'
        return res

    def answer(self, parsed):
        res = {'error': False}

        if 'word' in parsed:
            res['message'] = u'何が言いたいのだ'
            return res

        data = self.db.word.find_one(parsed)
        if data is None:

            res['error'] = True
            res['message'] = u'うっ！頭が・・・思い出せぬ・・・'
            return res

        del data['_id']

        value = []
        for v in data.keys():
            if v not in parsed.keys():
                value.append(v)

        if len(value) == 0:
            res['message'] = 'よく知っておるな'
            return res

        if len(value) == 2:
            value.remove('word')
            word = ''.join(value)
            if word.isdigit() or not word:
                res['message'] = data['word']
                return res

            res['message'] = u'それは・・・%sだ' % word
            return res

        res['message'] = data['word']
        return res

    def forget(self, parsed):
        res = {'error': False}
        return res
