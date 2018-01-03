#! /usr/bin/env python3
import argparse
import os
import scan
import xmlrpc.server
import xmlrpc.client

FREEZER_DIR=os.path.expanduser("~/.freezer")
FREEZER_PATHS_FILENAME=os.path.join(FREEZER_DIR, "paths.txt")
FREEZER_INDEX_PATH=os.path.join(FREEZER_DIR, "index.txt")

def init_workspace():
    os.makedirs(FREEZER_DIR, exist_ok=True)

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
    with open(os.path.join(FREEZER_DIR,FREEZER_PATHS_FILENAME), 'w') as paths_file:
        for line in contents:
            paths_file.write(line)
            paths_file.write('\n')

def get_freezer_indexed_paths():
    with open(os.path.join(FREEZER_DIR,FREEZER_PATHS_FILENAME), 'r') as freezer_paths_file:
        lines = freezer_paths_file.readlines()
    return [i.strip() for i in lines]

def save_scan_results(scanresult):
    results = sorted(scanresult, key=lambda s: s[0].lower())
    with open(FREEZER_INDEX_PATH, 'w') as index_file:
        for line in results:
            index_file.write("\t".join(line))
            index_file.write("\n")

def read_full_index():
    with open(FREEZER_INDEX_PATH, 'r') as index_file:
        return ''.join(index_file.readlines())

def serve_forever():
    addr = ("127.0.0.1", 8000)
    server = xmlrpc.server.SimpleXMLRPCServer(addr)
    print("serving on", addr)
    server.register_function(read_full_index)
    server.serve_forever()

def remote_list(ip_addr_str):
    assert(type(ip_addr_str) is str)
    a = xmlrpc.client.ServerProxy(ip_addr_str)
    return a.read_full_index()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", nargs='+')
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--local_list", action="store_true", help="List known local content")
    parser.add_argument("--remote_list", type=str, help="List the content at the address given")
    parser.add_argument("--serve", action="store_true", help="Serve a Python XML RPC server on port 8000")
    args = parser.parse_args()
    if args.init:
        init_workspace()
    elif args.scan:
        result = scan.perform_scan(get_freezer_indexed_paths(), 8)
        save_scan_results(result)
    elif args.local_list:
        print(read_full_index())
    elif args.remote_list:
        print(remote_list(args.remote_list))
    elif args.serve:
        serve_forever()
    elif args.add:
        add_indexed_path(args.add)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
