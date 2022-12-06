#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    elf = 1
    calories = 0
    max_calories = 0
    elf_with_max = 1
    infile = args.infile
    for line in infile:
        line = line.strip()
        if line == "":
            print(elf, end=",")
            print(calories)
            if calories > max_calories:
                max_calories = calories
                elf_with_max = elf
            elf += 1
            calories = 0
            continue
        calories += int(line)
    if calories > 0:
        print(elf, end=",")
        print(calories)
        if calories > max_calories:
            max_calories = calories
            elf_with_max = elf
        elf += 1
        calories = 0
    print(
        "Elf number {} has the supplies with the most calories ({}).".format(
            elf_with_max, max_calories
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 6 part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
