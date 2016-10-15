# -*- coding: utf-8 -*-

from lib.base import Base, re

class Nobunaga(Base):
    def answer(self, word, query, result):
        if result is None:
            message = u'うっ！頭が・・・思い出せぬ・・・'
            self.logging('error', word, message)
            return {
                'error': True,
                'message': message,
            }

        if result[2] < 2:
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
