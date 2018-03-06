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

    def replace_comment(self, pid):
        self.storage.replace_comment(pid)

    def insert_has_parent(self, pid):
        self.storage.insert_has_parent(pid)

    def insert_no_parent(self, pid):
        self.storage.insert_no_parent(pid)