import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS merkle_trees (
                id INTEGER PRIMARY KEY,
                merkle_root TEXT NOT NULL,
                transaction_hashes TEXT NOT NULL
            )
        """
        )

    def insert_merkle_tree(self, merkle_root, transaction_hashes):
        transaction_hashes_str = ",".join(transaction_hashes)
        self.cursor.execute(
            """
            INSERT INTO merkle_trees (merkle_root, transaction_hashes)
            VALUES (?, ?)
        """,
            (merkle_root, transaction_hashes_str),
        )
        self.conn.commit()

    def get_merkle_trees(self):
        self.cursor.execute("SELECT * FROM merkle_trees")
        return self.cursor.fetchall()

    def get_merkle_tree(self, merkle_root):
        self.cursor.execute(
            "SELECT * FROM merkle_trees WHERE merkle_root = ?", (merkle_root,)
        )
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()
