# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
import re
import os

class Nobunaga(object):
    def __init__(self, driver):
        self.t = Tokenizer()
        self.db = driver.connect()

    def learn(self, word):
        with self.db.cursor() as cur:
            error = True
            tokens = self.t.tokenize(word)
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
                    cur.execute('INSERT INTO nobunaga ('
                                'keyword, type, token_count, origin) '
                                'VALUES (%s, %s, %s, %s)',
                                (token.surface, token.part_of_speech, len(tokens), word))

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

    def answer(self, word):
        query = {
            'string': [],
            'data': [],
        }
        error = True
        tokens = self.t.tokenize(word)
        for token in tokens:
            if re.search(u'代名詞', token.part_of_speech):
                error = False
                if re.search(u'ダレ', token.reading):
                    query['string'].append('type LIKE %s')
                    query['data'].append('%人名%')

                if re.search(u'ドコ', token.reading):
                    query['string'].append('type LIKE %s')
                    query['data'].append('%地域%')
                continue

            if re.search(u'ナニ|ナン|ナゼ|イツ', token.reading):
                error = False
                continue

            query['string'].append('keyword = %s AND type = %s')
            query['data'].append(token.surface)
            query['data'].append(token.part_of_speech)

        with self.db.cursor() as cur:
            sql = """
            SELECT origin, token_count, COUNT(origin) as count
            FROM nobunaga
            WHERE %s
            GROUP BY origin
            ORDER BY count DESC
            """[1:-1] % ' OR '.join(query['string'])
            cur.execute(sql, tuple(query['data']))

            result = cur.fetchone()

        if result is None:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        if error:
            if result[1] == result[2]:
                return {
                    'error': False,
                    'message': u'よく知っておるな',
                }

            return {
                'error': error,
                'message': u'何が言いたいのだ',
            }

        if result[2] < result[1] - 2:
            for token in self.t.tokenize(result[0]):
                if re.search(u'固有名詞', token.part_of_speech):
                    target = token.surface
                    break

            try:
                _var = target
            except:
                return {
                    'error': error,
                    'message': u'何が知りたいのだ',
                }

            return {
                'error': False,
                'message': u'%sのことか？' % target,
            }

        return {
            'error': False,
            'message': result[0],
        }


