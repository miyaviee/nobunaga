# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
from urllib.parse import urlparse
import pymysql.cursors
import re
import os

class Analysis(object):
    def __init__(self):
        uri = urlparse(os.environ.get('CLEARDB_DATABASE_URL'))
        self.db = pymysql.connect(host=uri.hostname,
                                  user=uri.username,
                                  password=uri.password,
                                  db=uri.path[1:],
                                  charset='utf8',
                                  cursorclass=pymysql.cursors.DictCursor)

        self.t = Tokenizer()

    def parse(self, word):
        self.word = word
        return self.t.tokenize(word)

    def learn(self, tokens):
        with self.db.cursor() as cur:
            error = True
            for token in tokens:
                if re.search(u'代名詞', token.part_of_speech):
                    return {
                        'error': error,
                        'message': u'何が言いたいのだ',
                    }

                cur.execute('SELECT * '
                            'FROM nobunaga '
                            'WHERE keyword = %s '
                            'AND type = %s '
                            'AND origin = %s',
                            (token.surface, token.part_of_speech, self.word))

                if cur.fetchone() is None:
                    error = False
                    sql = 'INSERT INTO nobunaga (keyword, type, origin) VALUES (%s, %s, %s)'
                    cur.execute('INSERT INTO nobunaga ('
                                'keyword, type, origin) '
                                'VALUES (%s, %s, %s)',
                                (token.surface, token.part_of_speech, self.word))

        self.db.commit()

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
        query = {
            'string': [],
            'data': [],
        }
        error = True
        for token in tokens:
            if re.search(u'代名詞', token.part_of_speech):
                error = False
                continue

            if re.search(u'ナニ|ナン|イツ', token.reading):
                error = False
                continue

            query['string'].append('keyword = %s AND type = %s')
            query['data'].append(token.surface)
            query['data'].append(token.part_of_speech)

        if error:
            return {
                'error': error,
                'message': u'何が言いたいのだ',
            }

        with self.db.cursor() as cur:
            sql = """
            SELECT origin, COUNT(origin) as count
            FROM nobunaga
            WHERE %s
            GROUP BY origin
            """[1:-1] % ' OR '.join(query['string'])
            cur.execute(sql, tuple(query['data']))

            result = cur.fetchone()

        if result is None or result['count'] < 4:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        return {
            'error': False,
            'message': result['origin'],
        }


