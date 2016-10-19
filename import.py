# -*- coding: utf-8 -*-
import csv
import pymysql
import yaml
import re
from janome.tokenizer import Tokenizer

def save(con, t, word, answer):
    with con.cursor() as cur:
        cur.execute('SELECT * '
                    'FROM nobunaga '
                    'WHERE answer = %s ',
                    answer)

        results = cur.fetchall()

        tokens = t.tokenize(word)
        for token in tokens:
            if not re.search(u'名詞|動詞,自立', token.part_of_speech):
                continue

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
                        (token.reading, token.part_of_speech, len(tokens), answer))

            con.commit()

    return True

def db_reset(con):
    with con.cursor() as cur:
        cur.execute('DELETE FROM nobunaga')
        con.commit()

def csv_open(con, filename):
    reader = csv.reader(open(filename, 'r'))
    tokenizer = Tokenizer()
    for row in reader:
        save(con, tokenizer, row[0], row[1])


if __name__ == "__main__":
    config = yaml.load(open('./config.yml', 'r'))

    con = pymysql.connect(user = config['db']['username'],
                          passwd = config['db']['password'],
                          host = config['db']['hostname'],
                          db = config['db']['database'],
                          charset = 'utf8')

    db_reset(con)
    csv_open(con, 'data/data.csv')

    con.close()

