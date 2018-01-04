#! /usr/bin/env python3

import argparse
import os
import sqlite3
import xmlrpc.client
import xmlrpc.server
from zipfile import ZipFile

import scan
import freezerdb
from freezerdb import FreezerDB

FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_PATHS_FILENAME = os.path.join(FREEZER_DIR, "paths.txt")
FREEZER_INDEX_PATH = os.path.join(FREEZER_DIR, "index.txt")


def init_workspace():
    os.makedirs(FREEZER_DIR, exist_ok=True)
    db = freezerdb.FreezerDB()
    db.init_db()

def add_indexed_path(path):
    contents = []
    if os.path.exists(FREEZER_PATHS_FILENAME):
        with open(FREEZER_PATHS_FILENAME, 'r') as paths_file:
            contents = [i.strip() for i in paths_file.readlines()]
    contents.append(path)
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


def index_generator():
    db = FreezerDB()
    return db.run_query("select * from album")

def read_artists():
    db = FreezerDB()
    return db.run_query("select distinct artist from album")

def read_albums():
    db = FreezerDB()
    return db.run_query("select distinct album, artist from album order by artist COLLATE NOCASE")

def read_all():
    db = FreezerDB()
    return db.run_query("select * from album order by artist COLLATE NOCASE")

def serve_forever():
    addr = ("127.0.0.1", 8000)
    server = xmlrpc.server.SimpleXMLRPCServer(addr)
    print("serving on", addr)
    server.register_function(read_all)
    server.register_function(zip_album)
    server.register_function(search)
    server.serve_forever()


def get_proxy(addr):
    proxy = xmlrpc.client.ServerProxy(addr)
    return proxy


def remote_list(ip_addr_str):
    assert (type(ip_addr_str) is str)
    a = xmlrpc.client.ServerProxy(ip_addr_str)
    return a.read_full_index()


def search(query):
    result = ''
    with open(FREEZER_INDEX_PATH, 'r') as index_file:
        for line in index_file.readlines():
            if line.lower().count(query.lower()) > 0:
                result += (line)
    return result


def remote_search(query, host):
    a = xmlrpc.client.ServerProxy(host)
    return a.search(query)


def zip_album(album_name, output_dir="/tmp/freezer"):
    assert (type(output_dir) is str)
    album_path = None
    for album_tuple in index_generator():
        if "".join(album_tuple).count(album_name):
            album_path = album_tuple[-1]
            print("found it at {}".format(album_path.strip()))
            break
    outfilename = os.path.join(output_dir, album_name + '.zip')
    zf = ZipFile(outfilename, 'x')
    for root, dirs, files in os.walk(album_path.strip()):
        for filename in files:
            print("{}".format(filename))
            song_path = os.path.join(root, filename)
            zip_output_path = os.path.join(album_name,
                                           os.path.basename(song_path))
            zf.write(song_path, arcname=zip_output_path)
    zf.close()
    with open(outfilename, 'rb') as zipbytes:
        return zipbytes.read()

def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    add = subparsers.add_parser('add')
    add.add_argument("filename", type=str)

    init = subparsers.add_parser('init')

    scan = subparsers.add_parser('scan')

    subparsers.add_parser('serve')

    show = subparsers.add_parser('show')
    show.add_argument(
        "what_to_show", type=str, nargs='?', help="List known local content")

    parser.add_argument(
        "--search",
        type=str,
        help="search for stuff on a given freezer instance")
    parser.add_argument(
        "--freezer_host", type=str, default='http://localhost:8000')
    parser.add_argument(
        "--remote_list",
        type=str,
        help="List the content at the address given")
    parser.add_argument(
        "--remote_search",
        type=str,
        help="List the content at the address given")
    parser.add_argument(
        "--show_artists",
        action="store_true",
        )
    parser.add_argument(
        "--show_albums",
        action="store_true",
        )
    parser.add_argument(
        "--show_locations",
        action="store_true",
        )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve a Python XML RPC server on port 8000")
    parser.add_argument("--zip_album", type=str)
    parser.add_argument("--output_dir", type=str)
    return parser

def main():
    parser = get_args()
    args = parser.parse_args()
    print(args)
    if args.command == "init":
        init_workspace()
    elif args.command == "scan":
        result = scan.perform_scan(get_freezer_indexed_paths(), 8)
        save_scan_results(result)
    elif args.command == "show":
        if args.what_to_show == "all":
            for i in read_all():
                print("{:33}{:43}{}".format(i[0], i[1], i[2]))
        elif args.what_to_show == "albums":
            for i in read_albums():
                print("{:43}{}".format(i[1], i[0]))
        elif args.what_to_show == "artists":
            for i in read_artists():
                print(i[0])
        else:
            parser.print_usage()
    elif args.show_artists:
        for i in read_artists():
            print(i[0])
    elif args.remote_list:
        print(remote_list(args.remote_list))
    elif args.command == "serve":
        serve_forever()
    elif args.search:
        print(search(args.search))
    elif args.zip_album:
        zip_album(args.zip_album, args.output_dir)
    elif args.command == "add":
        add_indexed_path(args.filename)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
