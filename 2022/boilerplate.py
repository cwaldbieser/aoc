#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 6 part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
