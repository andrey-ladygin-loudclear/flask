import sqlite3

timeframe = '2015-05'

class SQLiteStorage():
    conn = sqlite3.connect('{}.db'.format(timeframe))
    c = conn.cursor()
    transactions = []

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS parent_reply
          (parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT,
           comment TEXT, subreddit TEXT, unix INT, score INT)''')

    def find_parent_comment(self, pid):
        try:
            query = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
            self.c.execute(query)
            result = self.c.fetchone()
            if result is not None:
                return result[0]
        except Exception as e:
            print('find_parent', e)

        return None

    def find_existing_score(self, pid):
        try:
            query = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
            self.c.execute(query)
            result = self.c.fetchone()
            if result is not None:
                return result[0]
        except Exception as e:
            print('find_parent', e)

        return None

    def replace_comment(self, comment_id, parent_id, parent_data, body, subreddit, created_at, score):
        try:
            sql = '''UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id = ?;'''.format(
                comment_id, parent_data, body, subreddit, created_at, score, parent_id
            )
            self.transaction_bldr(sql)
        except Exception as e:
            print('replace_comment', e)

    def insert_has_parent(self, comment_id, parent_id, parent_data, body, subreddit, created_at, score):
        try:
            sql = '''INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score);'''.format(
                parent_id, comment_id, parent_data, body, subreddit, created_at, score
            )
            self.transaction_bldr(sql)
        except Exception as e:
            print('replace_comment', e)

    def insert_no_parent(self, comment_id, parent_id, body, subreddit, created_at, score):
        try:
            sql = '''INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score);'''.format(
                parent_id, comment_id, body, subreddit, created_at, score
            )
            self.transaction_bldr(sql)
        except Exception as e:
            print('replace_comment', e)

    def transaction_bldr(self, sql):
        self.transactions.append(sql)

        if len(self.transactions) > 1000:
            self.c.execute("BEGIN TRANSACTION")
            for s in self.transactions:
                try:
                    self.c.execute(s)
                except:
                    pass
            self.c.execute("COMMIT;")
            self.transactions = []