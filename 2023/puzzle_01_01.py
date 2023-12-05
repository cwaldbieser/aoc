#! /usr/bin/env python

import argparse
import re


def main(args):
    """
    Advent of Code 2023, puzzle 01
    """
    pattern = re.compile(r"(\d)")
    total = 0
    for line in args.file:
        m = pattern.search(line)
        d0 = m.group()
        lst = list(line)
        lst.reverse()
        rline = "".join(lst)
        m = pattern.search(rline)
        d1 = m.group()
        n = int(f"{d0}{d1}")
        print(f"line: {line}, number: {n}")
        total += n
    print(f"The total is {total}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code Puzzle 01")
    parser.add_argument("file", type=argparse.FileType("r"), action="store")
    args = parser.parse_args()
    main(args)
