# -*- coding: utf-8 -*-

import re
import os

class Nobunaga(object):
    def __init__(self, driver):
        self.db = driver.connect()

    def learn(self, tokens, word):
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
                            (token.surface, token.part_of_speech, word))

                if cur.fetchone() is None:
                    error = False
                    sql = 'INSERT INTO nobunaga (keyword, type, origin) VALUES (%s, %s, %s)'
                    cur.execute('INSERT INTO nobunaga ('
                                'keyword, type, origin) '
                                'VALUES (%s, %s, %s)',
                                (token.surface, token.part_of_speech, word))

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

        with self.db.cursor() as cur:
            sql = """
            SELECT origin, COUNT(origin) as count
            FROM nobunaga
            WHERE %s
            GROUP BY origin
            ORDER BY count DESC
            """[1:-1] % ' OR '.join(query['string'])
            cur.execute(sql, tuple(query['data']))

            result = cur.fetchone()

        if result is None or result[1] < 3:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        if error:
            if result[1] == len(tokens) - 1:
                return {
                    'error': False,
                    'message': u'よく知っておるな',
                }

            return {
                'error': error,
                'message': u'何が言いたいのだ',
            }

        return {
            'error': False,
            'message': result[0],
        }


