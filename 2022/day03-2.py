#! /usr/bin/env python

import argparse
import itertools


def main(args):
    """
    The main function entrypoint.
    """
    items = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    priorities = range(1, 53)
    item_priorities = dict(zip(items, priorities))
    infile = args.infile
    total = 0
    for group in groupby3(infile):
        sack1, sack2, sack3 = group
        badge_item = sack1.intersection(sack2).intersection(sack3).pop()
        badge_priority = item_priorities[badge_item]
        total += badge_priority
    print("The total of the badge item priorities is: {}".format(total))


def groupby3(infile):
    """
    Generator yields 3-tuples that contain sets of the items represented by
    parsing every 3 lines.
    """
    cycle = itertools.cycle([0, 1, 2])
    group = []
    for n, line in zip(cycle, infile):
        group.append(set(line.strip()))
        if n == 2:
            yield group
            group = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 3 part 2")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
