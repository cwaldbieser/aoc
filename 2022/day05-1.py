#! /usr/bin/env python

import argparse
import pprint
import sys


def main(args):
    """
    The main entry point.
    """
    infile = args.infile
    stacks = parse_stacks(infile)
    if args.debug:
        print("Initial stacks:")
        pprint.pprint(stacks)
        print("")
    process_instructions(stacks, infile, args.debug)
    print_tops(stacks)
    pprint.pprint(stacks)


def print_tops(stacks):
    """
    Print the tops of the stacks.
    """
    tops = []
    for stack in stacks:
        tops.append(stack[-1])
    code = "".join(tops)
    code = code.replace(" ", "")
    print(code)


def process_instructions(stacks, infile, debug=False):
    """
    Apply instructions to stacks.
    """
    for line in infile:
        line = line.strip()
        words = line.split()
        crate_count = int(words[1])
        source_pos = int(words[3])
        dest_pos = int(words[5])
        apply_movement_to_stacks(stacks, crate_count, source_pos, dest_pos)
        if debug:
            print(line)
            pprint.pprint(stacks)
            print("")


def apply_movement_to_stacks(stacks, crate_count, source_pos, dest_pos):
    """
    Apply a single instruction to the stacks.
    """
    try:
        source_stack = stacks[source_pos - 1]
        dest_stack = stacks[dest_pos - 1]
    except IndexError:
        pprint.pprint(stacks)
        print("crate_count", crate_count)
        print("source_pos", source_pos)
        print("dest_pos", dest_pos)
        sys.exit(1)
    for _ in range(crate_count):
        dest_stack.append(source_stack.pop())


def parse_stacks(infile):
    """
    Parse the stack information from the beginning of `infile` until the first blank line.

    Returns a list of stacks.
    """
    stacks = []
    for line in infile:
        line = line.rstrip("\n")
        line_size = len(line)
        if line == "":
            break
        max_n = int((line_size + 1) / 4)
        if len(stacks) == 0:
            stacks = [[] for i in range(max_n)]
        for n in range(1, max_n + 1):
            crate = line[pos(n)]
            if crate != " ":
                stacks[n - 1].insert(0, crate)
    return stacks


def pos(n):
    return 1 + (n - 1) * 4


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 5")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Turn on debugging messages.")
    args = parser.parse_args()
    main(args)
