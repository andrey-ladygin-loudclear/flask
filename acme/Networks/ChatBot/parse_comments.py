import bz2
import sqlite3
import json
import tarfile
from datetime import datetime

import os

import shutil

#from acme.Networks.ChatBot.comments_repository import CommentsRepository
#from acme.Networks.ChatBot.sqlite_storage import SQLiteStorage

from comments_repository import CommentsRepository
from sqlite_storage import SQLiteStorage

def parse_comments():
    folders_with_comments = [
        'E:\dataset\\2014',
        'E:\dataset\\2015',
        'E:\dataset\\2016',
        'D:\datasets\\2007',
        'D:\datasets\\2008',
        'D:\datasets\\2009',
        'D:\datasets\\2010',
        'D:\datasets\\2011',
        'D:\datasets\\2012',
        'D:\datasets\\2013',
    ]
    for folder in folders_with_comments:
        read_folder(folder)

def read_folder(dir):
    files = os.listdir(dir)
    for file in files:
        if not file.endswith('bz2'):
            continue
        archive = os.path.join(dir, file)
        read_bzfile(archive, file.replace('.bz2', ''))

def read_bzfile(bzfile, name):
    print('Read Archive', bzfile, 'name', name)
    source_file = bz2.BZ2File(bzfile, "r")
    parse_comment(source_file, name)

def parse_comment(file, db_name):
    check_disk_space()
    total_rows = 0
    parsed_rows = 0
    replaced_rows = 0
    repository = CommentsRepository(SQLiteStorage(db_name))
    repository.create_table()
    for row in file:
        total_rows += 1
        row = json.loads(row)
        comment_id = row['name']
        parent_id = row['parent_id']
        body = format_data(row['body'])
        created_at = row['created_utc']
        score = row['score']
        subreddit = row['subreddit']
        parent_data = repository.find_parent_comment(parent_id)

        if score >= 2 and acceptable(body):
            existing_comment_score = repository.find_existing_score(parent_id)

            if existing_comment_score:
                if score > existing_comment_score:
                    repository.replace_comment(comment_id, parent_id, parent_data, body, subreddit, created_at, score)
                    replaced_rows += 1
            else:
                if parent_data:
                    repository.insert_has_parent(comment_id, parent_id, parent_data, body, subreddit, created_at, score)
                    parsed_rows += 1
                else:
                    repository.insert_no_parent(comment_id, parent_id, body, subreddit, created_at, score)

        if total_rows % 100000 == 0:
            print('Total rows read: {}, Paired rows: {}, Replaced rows: {}, Time: {}'.format(total_rows, parsed_rows, replaced_rows, str(datetime.now())))

def format_data(body):
    return body.replace("\n", "<EOF>").replace("\r", "<EOF>").replace('"', "'")

def acceptable(data, treshold=50):
    if len(data.split(' ')) > treshold or len(data) < 1:
        return False

    if len(data) > 1000:
        return False

    if data == '[deleted]' or data == '[removed]':
        return False

    return True

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def move_file(file, dest):
    shutil.move(file, os.path.join(dest, os.path.basename(file)))

def check_disk_space():
    pass

if __name__ == "__main__":
    #parse_comments()
    read_bzfile('/home/srivoknovski/dataset/reddit/RC_2015-01.bz2', 'RC_2015-01')