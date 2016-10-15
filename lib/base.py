# -*- coding: utf-8 -*-

import re
import os
import datetime

class Base(object):
    def __init__(self, driver, tokenizer):
        self.t = tokenizer
        self.db = driver.connect()

    def parse(self, word):
        return self.t.tokenize(word)

    def query(self, tokens):
        string = []
        data = []

        for token in tokens:
            if not re.search(u'名詞|動詞,自立', token.part_of_speech):
                continue

            string.append('keyword = %s AND type = %s')
            data.append(token.surface)
            data.append(token.part_of_speech)

        return {
            'string': string,
            'data': data,
        }

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

            return cur.fetchone()

    def logging(self, error, word, message):
        level = 'info'
        if error:
            level = 'error'

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

