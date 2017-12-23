#! /usr/bin/env python3
import os
import os.path
import eyed3
import multiprocessing
import argparse
import itertools
import logging
logging.disable(logging.WARNING)

def process_many(filenames):
    answer = set()
    for i in filenames:
        process_one(i, answer)
    return answer

def process_one(fname, answer):
    try:
        tag = eyed3.load(fname).tag
        artist = tag.artist if tag.artist is not None else "Unknown Artist"
        album = tag.album if tag.album is not None else "Unknown Album"
        answer.add((artist, album, os.path.dirname(fname)))
    except AttributeError:
        pass

def partition(inputs, num_buckets):
    buckets = [[] for i in range(num_buckets)]
    for index, value in enumerate(inputs):
        buckets[index % num_buckets].append(value)
    return buckets

def collect_fnames(paths_to_search):
    paths = []
    for input_dir in paths_to_search:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                path = os.path.join(root, file)
                if path[-3:] == "mp3":
                    paths.append(path)
    return paths

def print_all_columns(sorted_albums):
    numcolumns = len(sorted_albums[0])
    column_limits = [0 for i in range(numcolumns)]
    for infotuple in sorted_albums:
        for index, value in enumerate(infotuple):
            if len(value) > column_limits[index]:
                column_limits[index] = len(value)
    prefix = ""
    for limit in column_limits[:-1]:
        prefix += "{:<"
        prefix += str(limit)
        prefix += "}\t"
    prefix += "{}"
    for artist, album, path in sorted_albums:
        print(prefix.format(artist, album, path))

def print_albums(sorted_albums):
    albums = sorted(set([(i[1], i[2])for i in sorted_albums]))
    for album_name, path in albums: 
        print("{}\t{}".format(album_name, path))

def perform_scan(paths_to_search, num_threads):
    partitioned_stuff = [[i] for i in partition(collect_fnames(paths_to_search), num_threads)]
    outputs = [[] for i in range(num_threads)]
    with multiprocessing.Pool(processes=num_threads) as pool:                                                                   
        result = pool.starmap(process_many, partitioned_stuff)
        finalresult = result[0]
        for albumset in result[1:]:
            finaleresult = finalresult.union(albumset)
        sorted_albums = sorted(list(finalresult))
        return sorted_albums
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_threads", type=int, default=multiprocessing.cpu_count())
    parser.add_argument("--paths", type=str, nargs='+', required=True)
    parser.add_argument("--column", type=str)
    args = parser.parse_args()
    print(args.paths)
    if args.column == "album":
        print_albums(sorted_albums)
    else:
        print_all_columns(sorted_albums)

if __name__ == "__main__":
    main()

