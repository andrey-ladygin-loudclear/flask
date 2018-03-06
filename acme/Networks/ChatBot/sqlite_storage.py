import sqlite3

timeframe = '2015-05'

class SQLiteStorage():
    conn = sqlite3.connect('{}.db'.format(timeframe))
    c = conn.cursor()

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
