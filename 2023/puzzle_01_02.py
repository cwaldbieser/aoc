#! /usr/bin/env python

import argparse
import re


def find_overlapping_iter(pattern, s):
    """
    Generator produces all matches found by applying `pattern` to `s`,
    inlcuding overlapping ones.
    """
    while s:
        m = pattern.search(s)
        if not m:
            break
        yield m.group()
        pos = m.start() + 1
        s = s[pos:]


def main(args):
    """
    Advent of Code 2023, puzzle 01
    """
    pattern = re.compile(r"(\d|one|two|three|four|five|six|seven|eight|nine)")
    digit_map = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
    }
    total = 0
    for line in args.file:
        line = line.strip()
        digits = [digit_map.get(m, m) for m in find_overlapping_iter(pattern, line)]
        d0 = digits[0]
        d1 = digits[-1]
        n = int(f"{d0}{d1}")
        print(f"line: {line}, number: {n}")
        total += n
    print(f"The total is {total}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code Puzzle 01")
    parser.add_argument("file", type=argparse.FileType("r"), action="store")
    args = parser.parse_args()
    main(args)
