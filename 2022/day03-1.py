#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    items = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    priorities = range(1, 53)
    item_priorities = dict(zip(items, priorities))
    infile = args.infile
    total = 0
    for line in infile:
        line = line.strip()
        line_size = len(line)
        half_size = int(line_size / 2)
        bag1 = set(line[:half_size])
        bag2 = set(line[half_size:])
        shared_item = bag1.intersection(bag2).pop()
        total += item_priorities[shared_item]
    print("The total is: {}".format(total))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 3, part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
