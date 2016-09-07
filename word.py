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
        tmp = ''
        parsed = {}
        for token in self.t.tokenize(word):
            if re.search(u'代名詞', token.part_of_speech):
                if re.search(u'ダレ', token.reading):
                    if re.search(token.surface + u'(が|に)', word):
                        parsed['subject_type'] = 'person'
                        continue

                    if re.search(token.surface + u'(を|は)', word):
                        parsed['object_type'] = 'person'
                        continue

                if re.search(u'ドコ', token.reading):
                    parsed['object_type'] = 'place'
                    continue

                if re.search(u'ソコ', token.reading):
                    parsed['object_type'] = 'place'
                    continue


            if re.search(u'固有名詞', token.part_of_speech):
                if re.search(u'人名', token.part_of_speech):
                    tmp += token.surface
                    if re.search(token.surface + u'(が|に)', word):
                        if 'subject' in parsed:
                            parsed['object'] = tmp
                            parsed['object_type'] = 'person'
                            continue

                        parsed['subject'] = tmp
                        parsed['subject_type'] = 'person'

                    if re.search(token.surface + u'(を|は)', word):
                        parsed['object'] = tmp
                        parsed['object_type'] = 'person'
                    continue

                if re.search(u'地域', token.part_of_speech):
                    if re.search(token.surface + u'(に|で|へ)', word):
                        parsed['object'] = tmp
                        parsed['object_type'] = 'place'
                    continue

                parsed['object'] = tmp
                parsed['object_type'] = 'place'
                continue

            if re.search(u'名詞', token.part_of_speech):
                if re.search(u'ナニ', token.reading):
                    if re.search(token.surface + u'(で)', token.part_of_speech):
                        parsed['object_type'] = 'etc'
                        tmp = ''
                    continue

                if re.search(u'ナン', token.reading):
                    if re.search(token.surface + u'(で)', token.part_of_speech):
                        parsed['object_type'] = 'etc'
                        tmp = ''
                    continue

                if re.search(u'名詞,接尾', token.part_of_speech):
                    if token.reading == 'ネン':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                            parsed['object'] = tmp
                        parsed['object_type'] = 'year'

                    if token.reading == 'ツキ':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                            parsed['object'] = tmp
                        parsed['object_type'] = 'month'

                    if token.reading == '日':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                            parsed['object'] = tmp
                        parsed['object_type'] = 'day'

                tmp = token.surface
                continue

            if re.search(u'動詞', token.part_of_speech):
                parsed['verb'] = token.base_form
                break

            tmp = ''

        if 'subject_type' not in parsed:
            parsed['subject'] = '織田信長'
            parsed['subject_type'] = 'person'

        if 'object_type' not in parsed:
            parsed['object'] = '織田信長'
            parsed['object_type'] = 'person'

        return parsed

    def learn(self, parsed):
        data = {}
        res = {'error': False}

        if 'subject' not in parsed or 'object' not in parsed or 'verb' not in parsed:
            res['message'] = u'何が言いたいのだ'
            return res

        if re.search(u'信長', parsed['subject']):
            parsed['subject'] = '織田信長'

        if re.search(u'信長', parsed['object']):
            parsed['object'] = '織田信長'

        know = self.db.word.find_one(parsed)
        if know is not None:
            res['message'] = u'知っておるわ'
            return res

        self.db.word.insert_one(parsed)

        res['message'] = u'思い出したぞ・・・'
        return res

    def answer(self, parsed):
        res = {'error': False}

        if 'subject_type' not in parsed and 'object_type' not in parsed:
            res['message'] = u'何が言いたいのだ'
            return res

        if 'subject' not in parsed:
            key = 'subject'

        if 'object' not in parsed:
            key = 'object'

        if 'verb' not in parsed:
            key = 'verb'

        data = self.db.word.find_one(parsed)
        if data is None:
            res['error'] = True
            res['message'] = u'うっ！頭が・・・思い出せぬ・・・'
            return res

        try:
            _var = key
        except NameError:
            res['message'] = u'よく知っておるな'
            return res

        res['message'] = u'それは・・・%sだ' % data[key]
        return res

    def forget(self, parsed):
        res = {'error': False}
        return res
