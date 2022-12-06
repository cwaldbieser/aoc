#! /usr/bin/env python


import argparse


def main(args):
    """
    The main function.
    """
    infile = args.infile
    count = 0
    for line in infile:
        line = line.strip()
        parts = line.split(",", 2)
        left = parts[0]
        right = parts[1]
        ids_left = parse_ids(left)
        ids_right = parse_ids(right)
        if ids_left.issubset(ids_right) or ids_right.issubset(ids_left):
            count += 1
    print(count)


def parse_ids(range_str):
    """
    Parse ID ranges into sets of IDs.
    """
    parts = range_str.split("-")
    start = int(parts[0])
    stop = int(parts[1])
    id_set = set(range(start, stop + 1))
    return id_set


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 4")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
