import sqlite3
import threading
from itertools import zip_longest
from multiprocessing import Pool
from multiprocessing.dummy import Pool as dummy_Pool
from os.path import abspath, dirname, join, isfile, basename

import time
import os
import pandas as pd

from comments_repository import CommentsRepository
from sqlite_storage import SQLiteStorage

start = time.time()

tic = lambda start_time=start: 'at %8.4f seconds' % (time.time() - start_time)
db_folder = 'D:\\7     Network\ChatBot\db'
files_folder = 'D:\\7     Network\ChatBot\set'
db_folder = 'D:\datasets\db'
files_folder = 'C:\set'
log_file = 'process_thread_log.txt'

def get_databases(dir):
    files = os.listdir(dir)
    for file in files:
        if not file.endswith('.db'): continue
        if not isfile(join(files_folder, get_db_name(file)+'.from')):
            yield file
        else:
            print(file, 'are exists in', db_folder)

def make_training_set():
    number_of_threads_per_proccess = 3
    total = len(os.listdir(db_folder))# hack. Can cause some problems
    number = 0

    per_proccess = iterate_by_batch(get_databases(db_folder), number_of_threads_per_proccess, None)
    start_total_time = time.time()
    with Pool(processes=os.cpu_count()) as pool:
        for batch_files in iterate_by_batch(per_proccess, os.cpu_count(), None):
            start_time = time.time()
            files = pool.map(run_threads, batch_files, 1)
            number += len(files)*number_of_threads_per_proccess
            log("Proccessed", number, 'of', total, 'by', tic(start_time))
            #processed += len(files)
            #print('Processed', files, ',', processed, 'of', total)
            #all_files += files
    print('Total time execution', tic(start_total_time))

def run_threads(batch):
    if batch:
        with dummy_Pool(processes=len(batch)) as pool:
            start_time = time.time()
            log(get_name(), 'Run Threads on', batch)
            threads = pool.map(parse_db_to_file, batch, 1)
            log(get_name(), 'Finish Threads on', batch, tic(start_time))
            return threads

def parse_db_to_file(db):
    if not db: return
    start_time = time.time()
    name = get_db_name(db)
    repository = CommentsRepository(SQLiteStorage(name, db_folder))

    limit = 7000
    last_unix = 0
    cur_length = limit
    counter = 0

    from_file = join(files_folder, name+'.from')
    to_file = join(files_folder, name+'.to')

    while cur_length == limit:
        df = repository.get_batch(last_unix, limit)
        cur_length = len(df)

        try:
            last_unix = df.tail(1)['unix'].values[0]
        except:
            continue

        write_to_file(from_file, df['parent'].values)
        write_to_file(to_file, df['comment'].values)

        counter += 1
        if counter % 100 == 0:
            log(get_name(), 'Proccessing rows', counter*limit, tic(start_time))

    log(get_name(), 'Finish parse', 'rows', counter*limit, tic(start_time), name)


def iterate_by_batch(array_list, amount, fillvalue=None):
    args = [iter(array_list)] * amount
    return zip_longest(*args, fillvalue=fillvalue)


def write_to_file(file, data):
    with open(file, 'a', encoding='utf8') as f:
        for content in data:
            f.write(content+'\n')


def log(*args):
    print(*args)
    try:
        with open(log_file, 'a', encoding='utf8') as f:
            for content in args:
                f.write(str(content)+' ')
            f.write('\n')
    except Exception as e:
        print('ERROR save logs to file', str(e))


def get_name():
    return "Proc {}, {}: ".format(os.getpid(), threading.current_thread().name)


def get_db_name(file):
    return file.replace('.db', '')


if __name__ == '__main__':
    make_training_set()
    # t = time.time()
    #
    # f = iterate_by_batch(get_databases(db_folder), 4, None)
    #
    # for i in iterate_by_batch(f, 4):
    #     print(i)
    #     time.sleep(0.1)
    # print(tic(t))