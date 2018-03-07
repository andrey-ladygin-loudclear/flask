class CommentsRepository:
    storage = None

    def __init__(self, storage):
        self.storage = storage

    def create_table(self):
        self.storage.create_table()

    def find_parent_comment(self, pid):
        self.storage.find_parent_comment(pid)

    def find_existing_score(self, pid):
        self.storage.find_existing_score(pid)

    def replace_comment(self, comment_id, parent_id, parent_data, body, subreddit, created_at, score):
        self.storage.replace_comment(comment_id, parent_id, parent_data, body, subreddit, created_at, score)

    def insert_has_parent(self, comment_id, parent_id, parent_data, body, subreddit, created_at, score):
        self.storage.insert_has_parent(comment_id, parent_id, parent_data, body, subreddit, created_at, score)

    def insert_no_parent(self, comment_id, parent_id, body, subreddit, created_at, score):
        self.storage.insert_no_parent(comment_id, parent_id, body, subreddit, created_at, score)