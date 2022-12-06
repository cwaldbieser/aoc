#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    code_length = args.code_length
    data = args.infile.read()
    for pos in range(len(data)):
        endpos = pos + code_length
        code = set(data[pos:endpos])
        if len(code) == code_length:
            print(pos + code_length)
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 6 part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-c",
        "--code-length",
        type=int,
        action="store",
        default=4,
        help="The length of the unique code.")
    args = parser.parse_args()
    main(args)
