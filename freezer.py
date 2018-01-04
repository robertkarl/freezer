#! /usr/bin/env python3

import argparse
import os
import sqlite3
import xmlrpc.client
import xmlrpc.server
from zipfile import ZipFile

import scan
import db

FREEZER_DIR = os.path.expanduser("~/.freezer")
FREEZER_PATHS_FILENAME = os.path.join(FREEZER_DIR, "paths.txt")
FREEZER_INDEX_PATH = os.path.join(FREEZER_DIR, "index.txt")


def init_workspace():
    os.makedirs(FREEZER_DIR, exist_ok=True)
    db.init_db()


def add_indexed_path(paths):
    contents = []
    if os.path.exists(FREEZER_PATHS_FILENAME):
        with open(FREEZER_PATHS_FILENAME, 'r') as paths_file:
            contents = [i.strip() for i in paths_file.readlines()]
    for path_to_add in paths:
        contents.append(path_to_add)
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
    results = sorted(scanresult, key=lambda s: s[0].lower())
    for result in results:
        db.insert_album(result)


def index_generator():
    conn = db.get_connection()
    c = conn.cursor()
    return c.execute("select * from album")


def read_full_index():
    with open(FREEZER_INDEX_PATH, 'r') as index_file:
        return [tuple(i.strip().split("\t")) for i in index_file.readlines()]

def read_artists():
    conn = db.get_connection()
    c = conn.cursor()
    return c.execute("select distinct artist from album")

def read_albums():
    conn = db.get_connection()
    c = conn.cursor()
    return c.execute("select distinct album, artist from album order by artist COLLATE NOCASE")

def read_all():
    conn = db.get_connection()
    c = conn.cursor()
    return c.execute("select * from album order by artist COLLATE NOCASE")

def serve_forever():
    addr = ("127.0.0.1", 8000)
    server = xmlrpc.server.SimpleXMLRPCServer(addr)
    print("serving on", addr)
    server.register_function(read_full_index)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", nargs='+')
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--scan", action="store_true")
    parser.add_argument(
        "--local_list", action="store_true", help="List known local content")
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
    args = parser.parse_args()
    if args.init:
        init_workspace()
    elif args.scan:
        result = scan.perform_scan(get_freezer_indexed_paths(), 8)
        save_scan_results(result)
    elif args.local_list:
        print(read_full_index())
    elif args.show_artists:
        for i in read_artists():
            print(i[0])
    elif args.show_albums:
        for i in read_albums():
            print("{:43}{}".format(i[1], i[0]))
    elif args.show_locations:
        for i in read_all():
            print("{}\t{}\t{}".format(i[1], i[0], i[2]))
    elif args.remote_list:
        print(remote_list(args.remote_list))
    elif args.serve:
        serve_forever()
    elif args.search:
        print(search(args.search))
    elif args.zip_album:
        zip_album(args.zip_album, args.output_dir)
    elif args.add:
        add_indexed_path(args.add)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
