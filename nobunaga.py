# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
import re
import os

class Nobunaga(object):
    def __init__(self, driver):
        self.t = Tokenizer()
        self.db = driver.connect()

    def learn(self, word, answer):
        with self.db.cursor() as cur:
            cur.execute('SELECT * '
                        'FROM nobunaga '
                        'WHERE answer = %s ',
                        answer)

            results = cur.fetchall()

            tokens = self.t.tokenize(word)
            for token in tokens:
                exist = False
                for result in results:
                    if token.surface == result[0] and token.part_of_speech == result[1]:
                        exist = True
                        break

                if exist:
                    continue

                cur.execute('INSERT INTO nobunaga ('
                            'keyword, type, token_count, answer) '
                            'VALUES (%s, %s, %s, %s)',
                            (token.surface, token.part_of_speech, len(tokens), answer))

            self.db.commit()

        return {
            'error': False,
            'message': u'思い出したぞ',
        }

    def answer(self, word):
        query = {
            'string': [],
            'data': [],
        }
        tokens = self.t.tokenize(word)
        for token in tokens:
            if re.search(u'記号', token.part_of_speech):
                continue

            query['string'].append('keyword = %s AND type = %s')
            query['data'].append(token.surface)
            query['data'].append(token.part_of_speech)

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

        if result is None:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        diff_count = result[1] - result[2]

        if diff_count < 0 or 2 < diff_count:
            return result
            for token in self.t.tokenize(result[0]):
                if re.search(u'固有名詞', token.part_of_speech):
                    target = token.surface
                    break

            try:
                _var = target
            except:
                return {
                    'error': True,
                    'message': u'何が知りたいのだ？',
                }

            return {
                'error': True,
                'message': u'%sのことか？' % target,
            }

        if diff_count == 1 and result[1] == 2:
            return {
                'error': True,
                'message': u'知らぬな',
            }

        return {
            'error': False,
            'message': result[0],
            'debug': {
                'token_count': result[1],
                'hit_count': result[2],
                'query': query,
            },
        }

