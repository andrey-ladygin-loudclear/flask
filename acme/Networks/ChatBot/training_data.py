import sqlite3
from os.path import abspath, dirname, join, isfile, basename
import pandas as pd


#from acme.Networks.ChatBot.comments_repository import CommentsRepository
#from acme.Networks.ChatBot.sqlite_storage import SQLiteStorage

from comments_repository import CommentsRepository
from sqlite_storage import SQLiteStorage


def get_databases():
    return [
        '/home/srivoknovski/Python/flask/acme/Networks/ChatBot/db2/RC_2015-01111'
    ]

def make_training_set():
    for db in get_databases():
        path = dirname(db)
        name = basename(db)
        repository = CommentsRepository(SQLiteStorage(name, path))

        limit = 5000
        last_unix = 0
        cur_length = limit
        counter = 0
        test_done = False

        while cur_length == limit:
            df = repository.get_batch(last_unix, limit)
            last_unix = df.tail(1)['unix'].values[0]
            cur_length = len(df)
            if not test_done:
                write_to_file("set/test.from", df['parent'].values)
                write_to_file("set/test.to", df['comment'].values)
                test_done = True
            else:
                write_to_file("set/train.from", df['parent'].values)
                write_to_file("set/train.to", df['comment'].values)

            counter += 1
            if counter % 20 == 0:
                print(counter*limit, "rows completer so far")


def write_to_file(file, data):
    with open(file, 'a', encoding='utf8') as f:
        for content in data:
            f.write(content+'\n')


if __name__ == '__main__':
    make_training_set()