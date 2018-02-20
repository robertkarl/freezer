import os
import sqlite3

FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_DB = os.path.join(FREEZER_DIR, "albums.db")


class FreezerDB(object):

    ALBUM_CREATE_QUERY = "Create table album (artist text, album text, location text)"

    def __init__(self, connection=None):
        self.conn = connection
        if connection is None:
             self.conn = sqlite3.connect(FREEZER_DB)

    def init_db(self):
        c = self.conn.cursor()
        c.execute(FreezerDB.ALBUM_CREATE_QUERY)

    def insert_album(self, album_info):
        assert type(album_info) is tuple
        c = self.conn.cursor()
        c.execute("insert into album values (?, ?, ?)", album_info)
        self.conn.commit()

    def run_query(self, *query_str):
        c = self.conn.cursor()
        ans = []
        for row in c.execute(*query_str):
            ans.append(row)
        return ans

    def read_artists(self):
        return self.run_query("select distinct artist from album")

    def read_albums(self):
        return self.run_query(
            "select distinct album, artist from album order by artist COLLATE NOCASE"
        )

    def read_all(self):
        return self.run_query(
            "select * from album order by artist COLLATE NOCASE")

    def index_generator(self):
        return self.run_query("select * from album")
