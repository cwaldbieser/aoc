#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    top_n = args.top_n
    elf = 1
    calories = 0
    leaderboard = []
    infile = args.infile
    for line in infile:
        line = line.strip()
        if line == "":
            print(elf, end=",")
            print(calories)
            leaderboard.append((calories, elf))
            leaderboard.sort(reverse=True)
            leaderboard = leaderboard[:top_n]
            elf += 1
            calories = 0
            continue
        calories += int(line)
    if calories > 0:
        print(elf, end=",")
        print(calories)
        leaderboard.append((calories, elf))
        leaderboard.sort(reverse=True)
        leaderboard = leaderboard[:top_n]
        elf += 1
        calories = 0
    print("The following elves are the top {} calorie carriers:".format(top_n))
    for calories, elf in leaderboard:
        print("Elf {} with {} calories.".format(elf, calories))
    calories_sum = sum(calories for calories, _ in leaderboard)
    print("The sum of their calories is {}.".format(calories_sum))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 1 part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-n",
        "--top-n",
        type=int,
        action="store",
        default=1,
        help="Show the top N elves carrying supplies with the most calories.",
    )
    args = parser.parse_args()
    main(args)
