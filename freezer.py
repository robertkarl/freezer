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
import sqlite3
import subprocess
import time
import xmlrpc.client
import xmlrpc.server
from zipfile import ZipFile

import vlc

import scan
import freezerdb
from freezerdb import FreezerDB

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
    with open(os.path.join(FREEZER_DIR, FREEZER_PATHS_FILENAME),
              'r') as freezer_paths_file:
        lines = freezer_paths_file.readlines()
    return [i.strip() for i in lines]


def save_scan_results(scanresult):
    if os.path.exists(freezerdb.FREEZER_DB):
        os.remove(freezerdb.FREEZER_DB)
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


def serve_forever():
    addr = ("0.0.0.0", 8000)
    server = xmlrpc.server.SimpleXMLRPCServer(addr)
    print("serving on", addr)
    frzr = FreezerInstance()
    db = FreezerDB()
    server.register_function(db.index_generator, "read_all")
    server.register_function(frzr.zip_album)
    server.register_function(frzr.search, name="search")
    server.serve_forever()


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


def zip_album(query):
    """ Retrieve an album based on query then write matching songs into a zip file.
    Stores the zip file in FREEZER_TMP_DIR and returns the filename.

    # TODO: fix the network zip file functionality (this function used to return the bytes)
    """
    assert type(query) is str
    db = FreezerDB()
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
    artist_album_str = "{} - {}".format(artist_name, album_name)
    outfilename = os.path.join(
        output_dir, artist_album_str + '.zip')
    if not os.path.exists(outfilename):
        os.makedirs(output_dir, exist_ok=True)
        zf = ZipFile(outfilename, 'w')
        for root, dirs, files in os.walk(album_path.strip()):
            for filename in files:
                song_path = os.path.join(root, filename)
                zip_output_path = os.path.join(artist_album_str,
                                               os.path.basename(song_path))
                zf.write(song_path, arcname=zip_output_path)
        zf.close()
    assert os.path.exists(outfilename)
    return outfilename


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
    subparsers.add_parser('serve')

    zip_parser = subparsers.add_parser('archive')
    zip_parser.add_argument("album_to_zip")

    zip_parser = subparsers.add_parser('play')
    zip_parser.add_argument("album_to_zip")

    return parser


def main():
    parser = get_args()
    args = parser.parse_args()
    thefreezer = FreezerInstance(args.remote_host)
    db = FreezerDB()
    if args.command == "init":
        init_workspace()
    elif args.command == "scan":
        result = scan.perform_scan(get_freezer_indexed_paths(), 8)
        save_scan_results(result)
    elif args.command == "show":
        if args.what_to_show == "all":
            for i in db.index_generator():
                print("{:33}{:43}{}".format(i[0], i[1], i[2]))
        elif args.what_to_show == "albums":
            for i in db.read_albums():
                print("{:43}{}".format(i[1], i[0]))
        elif args.what_to_show == "artists":
            for i in db.read_artists():
                print(i[0])
        else:
            parser.print_usage()
    elif args.command == "serve":
        serve_forever()
    elif args.command == "archive":
        album_name, zipbytes = thefreezer.zip_album(args.album_to_zip)
        outpath = os.path.join(os.getcwd(), album_name + ".zip")
        outf = open(outpath, 'wb')
        outf.write(zipbytes)
        print(outpath)
    elif args.command == "play":
        outfname = thefreezer.zip_album(args.album_to_zip)
        # -o forces overwrite lol
        subprocess.run(["unzip", "-qq", "-o", outfname, "-d", FREEZER_TMP_DIR])
        filelist = sorted(glob.glob(outfname[:-4] + "/*.mp3"))
        for f in filelist:
            print(os.path.basename(f))
        media_list = vlc.MediaList(filelist)
        player = vlc.MediaListPlayer()
        player.set_media_list(media_list)
        player.play()
        # Dump user into a PDB session. Songs can be controlled from there in
        # lieu of a real interface of some kind.
        import pdb
        pdb.set_trace()
    elif args.command == "add":
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
