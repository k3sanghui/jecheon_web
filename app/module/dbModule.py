# file name : dbModule.py
# pwd : /jecheon_app/user_app/module/dbModule.py

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        load_dotenv(os.path.join(base_dir, '.env'))

        self.db = psycopg2.connect(database=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
                                   password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"),
                                   port=os.getenv("DB_PORT"))
        self.cursor = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        data = self.cursor.fetchone()[0]
        return data

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def col(self, query, args={}):
        self.cursor.execute(query, args)
        col = [cn[0] for cn in self.cursor.description]
        return col

    def commit(self):
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
