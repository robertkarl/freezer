import sqlite3
import os
from freezer import read_full_index
FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_DB = os.path.join(FREEZER_DIR, "albums.db")

conn = None


def get_connection():
    global conn
    if conn is None:
        conn = sqlite3.connect(FREEZER_DB)
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("Create table album (artist text, album text, location text)")
    for artist, album, path in read_full_index():
        print("inserting", album)
        c.execute("insert into album values (?, ?, ?)", (artist, album, path))


def query_db():
    conn = get_connection()
    c = conn.cursor()
    ans = []
    for row in c.execute("select * from album"):
        print(row)
        ans.append(row)
    return ans


def insert_albums(artist_album_pairs):
    conn = sqlite3.connect(FREEZER_DB)
    c = conn.cursor()
    for arg in artist_album_pairs:
        assert type(arg) is tuple
    c = get_cursor()
    for artist, album in artist_album_pairs:
        c.execute("insert into album values (?, ?, ?)", (artist, album))
