#! /usr/bin/env python3
"""

pip3 install eyed3
brew install libmagic
pip3 install libmagic
pip3 install python-vlc

"""

import argparse
import glob
import os
import pdb
import random
import sqlite3
import subprocess
import time
import xmlrpc.client
from zipfile import ZipFile

import vlc

import freezerdb
import scan
from loop import Looper

FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_PATHS_FILENAME = os.path.join(FREEZER_DIR, "paths.txt")
FREEZER_INDEX_PATH = os.path.join(FREEZER_DIR, "index.txt")
FREEZER_TMP_DIR = "/tmp/freezer"


def init_workspace():
    os.makedirs(FREEZER_DIR, exist_ok=True)
    db = freezerdb.FreezerDB()
    db.init_db()


def add_indexed_path(paths):
    contents = []
    if os.path.exists(FREEZER_PATHS_FILENAME):
        with open(FREEZER_PATHS_FILENAME, 'r') as paths_file:
            contents = [i.strip() for i in paths_file.readlines()]
    for one_path in paths:
        contents.append(one_path)
    contents = list(set(contents))
    contents = sorted(contents)
    for line in contents:
        print(line)
    with open(os.path.join(FREEZER_DIR, FREEZER_PATHS_FILENAME),
              'w') as paths_file:
        for line in contents:
            paths_file.write(line)
            paths_file.write('\n')


def get_freezer_indexed_paths():
    with open(FREEZER_PATHS_FILENAME, 'r') as freezer_paths_file:
        lines = freezer_paths_file.readlines()
    return [i.strip() for i in lines]


def save_scan_results(scanresult):
    if os.path.exists(freezerdb.FREEZER_DB):
        print("remove existing db at {}? [y/n] default is no".format(
            freezerdb.FREEZER_DB))
        i = input()
        if i == 'y':
            os.remove(freezerdb.FREEZER_DB)
        else:
            print("aborting scan")
            return
    init_workspace()
    db = freezerdb.FreezerDB()
    results = sorted(scanresult, key=lambda s: s[0].lower())
    for result in results:
        db.insert_album(result)


class FreezerInstance(object):
    def __init__(self, addr=None):
        assert addr is None or type(addr) is str
        self.addr = addr
        if self.addr is not None:
            self.proxy = get_proxy(addr)
        else:
            self.proxy = None

    def search(self, query):
        if self.proxy is not None:
            return self.proxy.search(query)
        return search(query)

    def zip_album(self, query):
        if self.proxy is not None:
            return self.proxy.zip_album(query)
        return zip_album(query)


def get_proxy(addr):
    proxy = xmlrpc.client.ServerProxy(addr)
    return proxy


def remote_list(ip_addr_str):
    assert (type(ip_addr_str) is str)
    a = xmlrpc.client.ServerProxy(ip_addr_str)
    return a.read_full_index()


def search(searchterm):
    db = freezerdb.FreezerDB()
    ans = []
    for row in db.read_all():
        if "".join(row).lower().count(searchterm.lower()) > 0:
            ans.append(row)
    return ans


def remote_search(query, host):
    a = xmlrpc.client.ServerProxy(host)
    return a.search(query)


def replace_bad_chars(somestr):
    return somestr.replace(":", "_")


def zip_album(query):
    """ Retrieve an album based on query then write matching songs into a zip file.
    Stores the zip file in FREEZER_TMP_DIR and returns the filename.

    # TODO: fix the network zip file functionality (this function used to return the bytes)
    """
    assert type(query) is str
    db = freezerdb.FreezerDB()
    album_path = None
    album_name = None
    artist_name = None
    for album_tuple in db.read_all():
        if "".join(album_tuple).lower().count(query.lower()):
            album_path = album_tuple[-1]
            album_name = album_tuple[1]
            artist_name = album_tuple[0]
            break
    output_dir = FREEZER_TMP_DIR
    arist_name = replace_bad_chars(artist_name)
    album_name = replace_bad_chars(album_name)
    artist_album_str = "{} - {}".format(artist_name, album_name)
    outfilename = os.path.join(output_dir, artist_album_str + '.zip')
    if not os.path.exists(outfilename):
        os.makedirs(output_dir, exist_ok=True)
        zf = ZipFile(outfilename, 'w')
        for root, dirs, files in os.walk(album_path.strip()):
            for filename in files:
                song_path = os.path.join(root, filename)
                zip_output_path = os.path.join(artist_album_str,
                                               os.path.basename(song_path))
                zip_output_path.replace(":", "_")
                zf.write(song_path, arcname=zip_output_path)
        zf.close()
    assert os.path.exists(outfilename)
    print("outfilename  is {}".format(outfilename))
    with open(outfilename, 'rb') as zipbytes:
        return (outfilename, zipbytes.read())


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote_host", default=None)
    subparsers = parser.add_subparsers(dest='command')

    add = subparsers.add_parser('add')
    add.add_argument("filenames", type=str, nargs='+')

    show = subparsers.add_parser('show')
    show.add_argument(
        "what_to_show",
        type=str,
        choices=('all', 'albums', 'artists'),
        help="List known local content")

    search = subparsers.add_parser('search')
    search.add_argument("query", type=str, nargs='?')

    subparsers.add_parser('init')
    subparsers.add_parser('scan')

    zip_parser = subparsers.add_parser('archive')
    zip_parser.add_argument("album_to_zip")

    zip_parser = subparsers.add_parser('play')
    zip_parser.add_argument("album_to_zip")

    subparsers.add_parser('play_random_album')

    return parser


class loop_handler:
    def __init__(self, player):
        self.player = player
        theplayer = self.player.get_media_player
        self.looper = Looper(self)

    def handle(self, s):
        if s == ' ':
            if self.player.is_playing:
                print('pause')
                self.player.pause()
            else:
                print('play')
                self.player.play()
        elif s == 'n':
            print('next')
            self.player.next()
        elif s == 'p':
            print('previous')
            self.player.previous()
        elif s == '?':
            print(self.player)

    def go(self):
        self.looper.go()


def play_album(thefreezer, args):
    outfname, _ = thefreezer.zip_album(args.album_to_zip)
    # -o forces overwrite lol
    subprocess.run(["unzip", "-qq", "-o", outfname, "-d", FREEZER_TMP_DIR])
    filelist = sorted(glob.glob(outfname[:-4] + "/*.mp3"))
    print(os.path.basename(outfname)[:-4])
    for f in filelist:
        print(os.path.basename(f))
    media_list = vlc.MediaList(filelist)
    player = vlc.MediaListPlayer()
    player.set_media_list(media_list)
    player.play()
    # Dump user into a PDB session. Songs can be controlled from there in
    # lieu of a real interface of some kind.
    l = loop_handler(player)
    l.go()


def play_random_album(db, thefreezer, args):
    albums = [i for i in db.read_albums()]
    album = random.choice(albums)
    args.album_to_zip = album[0]
    play_album(thefreezer, args)


def main():
    parser = get_args()
    args = parser.parse_args()
    thefreezer = FreezerInstance(args.remote_host)
    db = freezerdb.FreezerDB()
    if args.command == "init":
        init_workspace()
    elif args.command == "scan":
        result = scan.perform_scan(get_freezer_indexed_paths(), 8)
        save_scan_results(result)
    elif args.command == "show":
        if args.what_to_show == "all":
            for i in db.read_all():
                print("{:33}{:43}{}".format(i[0], i[1], i[2]))
        elif args.what_to_show == "albums":
            for i in db.read_albums():
                print("{:43}{}".format(i[1], i[0]))
        elif args.what_to_show == "artists":
            for i in db.read_artists():
                print(i[0])
        else:
            parser.print_usage()
    elif args.command == "archive":
        # In a remote freezer situation, "album_name" is actually the remote file path
        outpath, zipbytes = thefreezer.zip_album(args.album_to_zip)
        outf = open(outpath, 'wb')
        outf.write(zipbytes.data)
        print(outpath)
    elif args.command == "play":
        play_album(thefreezer, args)
    elif args.command == "play_random_album":
        play_random_album(db, thefreezer, args)
    elif args.command == "search_path":
        add_indexed_path(args.filenames)
    elif args.command == "play":
        add_indexed_path(args.filenames)
    elif args.command == "search":
        for i in thefreezer.search(args.query):
            print("{:33}{:43}{}".format(i[0], i[1], i[2]))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
