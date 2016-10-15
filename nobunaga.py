# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
import re
import os
import datetime

class Nobunaga(object):
    def __init__(self, driver):
        self.t = Tokenizer()
        self.db = driver.connect()

    def parse(self, word):
        return self.t.tokenize(word)

    def create_query(self, tokens):
        query = {
            'string': [],
            'data': [],
        }

        for token in tokens:
            if not re.search(u'名詞', token.part_of_speech):
                continue

            query['string'].append('keyword = %s AND type = %s')
            query['data'].append(token.surface)
            query['data'].append(token.part_of_speech)

        return query

    def search(self, query):
        with self.db.cursor() as cur:
            sql = """
            SELECT answer, token_count, COUNT(answer) as count
            FROM nobunaga
            WHERE %s
            GROUP BY answer
            ORDER BY count DESC
            """[1:-1] % ' OR '.join(query['string'])
            cur.execute(sql, tuple(query['data']))

            result = cur.fetchone()

        return result

    def answer(self, word, query, result):
        if result is None:
            message = u'うっ！頭が・・・思い出せぬ・・・'
            self.logging('error', word, message)
            return {
                'error': True,
                'message': message,
            }

        if result[2] < 2:
            for token in self.parse(result[0]):
                if re.search(u'固有名詞', token.part_of_speech):
                    target = token.surface
                    break

            try:
                _var = target
            except:
                message = u'何のことだ？'
                self.logging('info', word, message)
                return {
                    'error': True,
                    'message': message,
                }

        message = result[0]
        self.logging('info', word, message)
        return {
            'error': False,
            'message': message,
            'debug': {
                'token_count': result[1],
                'hit_count': result[2],
                'query': query,
            },
        }

    def logging(self, level, word, message):
        date = datetime.datetime.today()
        with self.db.cursor() as cur:
            sql = """
            INSERT INTO log
            VALUES (%s)
            """[1:-1]
            cur.execute(sql, '%s, %s, %s, %s' % (date.strftime('%Y/%m/%d %H:%M:%S'), level, word, message))

        self.db.commit()

    def showlog(self, word):
        if word is None:
            word = ''

        with self.db.cursor() as cur:
            sql = """
            SELECT *
            FROM log
            WHERE line LIKE %s
            ORDER BY line DESC
            """[1:-1]

            cur.execute(sql, '%' + word + '%')

            results = cur.fetchall()

        return list(map(lambda r: r[0], results))

