#! /usr/bin/env python

import argparse

puzzle_number = 2


def main(args):
    """
    Main program entrypoint.
    """
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"Advent of Code Puzzle {puzzle_number}")
    parser.add_argument("file", type=argparse.FileType("r"), action="store")
    args = parser.parse_args()
    main(args)
