# -*- coding: utf-8 -*-

from lib.base import Base, re

class Nobunaga(Base):
    def answer(self, word, query, result):
        if result is None:
            return {
                'error': True,
                'message': u'うっ！頭が・・・思い出せぬ・・・',
            }

        if result[2] < 2 and not re.search(u'ついて', word):
            for token in self.t.tokenize(word):
                if not re.search(u'固有名詞', token.part_of_speech):
                    continue

                return {
                    'error': True,
                    'message': u'%sは知っておるが・・・' % token.surface
                }

            return {
                'error': True,
                'message': u'何といえばよいか・・・',
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

