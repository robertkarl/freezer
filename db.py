import sqlite3
import os
FREEZER_DIR=os.path.expanduser("~/.freezer")
FREEZER_DB=os.path.join(FREEZER_DIR, "albums.db")

cursor = None
def get_cursor():
    global cursor
    if cursor is None:
        conn = sqlite3.connect(FREEZER_DB)
        cursor = conn.cursor()
    return cursor

def init_db():
    c = get_cursor()
    c.execute("Create table album (artist text, album text, location text)")

def insert_albums(artist_album_pairs):
    conn = sqlite3.connect(FREEZER_DB)
    c = conn.cursor()
    for arg in artist_album_pairs:
        assert type(arg) is tuple
    c = get_cursor()
    for artist, album in artist_album_pairs:
        c.execute("insert into album values (?, ?)", (artist, album))
