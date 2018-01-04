import sqlite3
import os
FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_DB = os.path.join(FREEZER_DIR, "albums.db")

class FreezerDB(object):

    def __init__(self):
        self.conn = sqlite3.connect(FREEZER_DB)

    def init_db(self):
        c = self.conn.cursor()
        c.execute("Create table album (artist text, album text, location text)")


    def insert_album(self, album_info):
        assert type(album_info) is tuple
        c = self.conn.cursor()
        c.execute("insert into album values (?, ?, ?)", album_info)
        self.conn.commit()

    def query_db(self):
        c = self.conn.cursor()
        ans = []
        for row in c.execute("select * from album"):
            print(row)
            ans.append(row)
        return ans


    def insert_albums(self, artist_album_pairs):
        for arg in artist_album_pairs:
            assert type(arg) is tuple
        c = self.conn.cursor()
        for artist, album in artist_album_pairs:
            c.execute("insert into album values (?, ?, ?)", (artist, album))

    def run_query(self, query_str):
        c = self.conn.cursor()
        ans = []
        for row in c.execute(query_str):
            ans.append(row)
        return ans

