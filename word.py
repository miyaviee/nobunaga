from janome.tokenizer import Tokenizer
from pymongo import MongoClient
import re
import sys

class Analysis(object):

    def __init__(self):
        self.db = MongoClient('mongodb://heroku_12x9l8h7:9n1fpsesiu2crg1pjo8gunep7p@ds019856.mlab.com:19856/heroku_12x9l8h7').heroku_12x9l8h7
        self.t = Tokenizer()

    def parse(self, word):
        tmp = ''
        parsed = []
        for token in self.t.tokenize(word):
            if re.search(u'代名詞', token.part_of_speech):
                if re.search(u'ダレ', token.reading):
                    if re.search(token.surface + u'(が|は)', word):
                        parsed.append({'type': 'person', 'value': 'search'})
                        continue

                    if re.search(token.surface + u'(を|に)', word):
                        parsed.append({'type': 'person', 'value': 'search'})
                        continue

                if re.search(u'ドコ', token.reading):
                    parsed.append({'type': 'place', 'value': 'search'})
                    continue

                if re.search(u'ソコ', token.reading):
                    parsed.append({'type': 'place', 'value': 'search'})
                    continue


            if re.search(u'固有名詞', token.part_of_speech):
                if re.search(u'人名', token.part_of_speech):
                    tmp += token.surface
                    if re.search(u'人名,名', token.part_of_speech):
                        parsed.append({'type': 'person', 'value': tmp})
                    continue

                if re.search(u'地域', token.part_of_speech):
                    parsed.append({'type': 'place', 'value': token.surface})
                    continue

                parsed.append({'type': 'place', 'value': token.surface})
                continue

            if re.search(u'名詞', token.part_of_speech):
                if re.search(u'ナニ', token.reading):
                    tmp = 'search'
                    continue

                if re.search(u'ナン', token.reading):
                    tmp = 'search'
                    continue

                if re.search(u'名詞,接尾', token.part_of_speech):
                    if token.reading == 'ネン':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                        parsed.append({'type': 'year', 'value': tmp})

                    if token.reading == 'ツキ':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                        parsed.append({'type': 'month', 'value': tmp})

                    if token.reading == '日':
                        if re.search(u'^\d+$', tmp):
                            tmp += token.surface
                        parsed.append({'type': 'day', 'value': tmp})

                tmp = token.surface
                continue

            if re.search(u'動詞', token.part_of_speech):
                parsed.append({'type': 'verb', 'value': token.base_form})
                break

            tmp = ''

        return parsed

    def learn(self, parsed):
        data = {}
        if len(parsed) == 2:
            parsed.insert(0, {'type': 'person', 'value': '織田信長'})

        res = {'err': False}

        try:
            data['subject'] = parsed[0]['value']
            data['subject_type'] = parsed[0]['type']
            data['object'] = parsed[1]['value']
            data['object_type'] = parsed[1]['type']
            data[parsed[2]['type']] = parsed[2]['value']

            self.db.word.insert_one(data)
        except IndexError:
            res['message'] = '何が言いたいのだ'
            return res

        res['message'] = '思い出したぞ・・・'
        return res

    def answer(self, parsed):
        query = {}
        if len(parsed) == 2:
            parsed.insert(0, {'type': 'person', 'value': '織田信長'})

        res = {'err': False}

        try:
            if parsed[0]['value'] != '織田信長':
                parsed[0], parsed[1] = parsed[1], parsed[0]

            if parsed[0]['value'] != 'search':
                query['subject'] = parsed[0]['value']
            else:
                key = 'subject'

            query['subject_type'] = parsed[0]['type']

            if parsed[1]['value'] != 'search':
                query['object'] = parsed[1]['value']
            else:
                key = 'object'

            query['object_type'] = parsed[1]['type']

            if parsed[2]['value'] != 'search':
                query[parsed[2]['type']] = parsed[2]['value']
            else:
                key = parsed[2]['type']
        except IndexError:
            res['message'] = '何が言いたいのだ'
            return res

        data = self.db.word.find_one(query)
        if data is None:
            res['err'] = True
            res['message'] = 'うっ！頭が・・・思い出せぬ・・・'
            return res

        try:
            _var = key
        except NameError:
            res['message'] = 'よく知っておるな'
            return res

        res['message'] = 'それは・・・%sだ' % data[key]
        return res

    def forget(self, parsed):
        res = {'err': False}
        return res
