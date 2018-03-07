import sqlite3
import json
from datetime import datetime

from acme.Networks.ChatBot.comments_repository import CommentsRepository
from acme.Networks.ChatBot.sqlite_storage import SQLiteStorage

def parse_comments():
    folders_with_comments = []
    for file in folders_with_comments:
        parse_comment(file)


def parse_comment(file):
    total_rows = 0
    parsed_rows = 0
    repository = CommentsRepository(SQLiteStorage())
    repository.create_table()

    with open(file) as f:
        for row in f:
            total_rows += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_at = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            parent_data = repository.find_parent_comment(parent_id)

            if score >= 2 and acceptable(body):
                existing_comment_score = repository.find_existing_score(parent_id)
                if existing_comment_score and score > existing_comment_score:
                    repository.replace_comment(comment_id, parent_id, parent_data, body, subreddit, created_at, score)
                else:
                    if parent_data:
                        repository.insert_has_parent(comment_id, parent_id, parent_data, body, subreddit, created_at, score)
                    else:
                        repository.insert_no_parent(comment_id, parent_id, body, subreddit, created_at, score)


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
