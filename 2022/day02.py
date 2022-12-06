#! /usr/bin/env python

import argparse

opponent_map = {"A": "R", "B": "P", "C": "S"}

my_map = {
    "X": "R",
    "Y": "P",
    "Z": "S",
}

shape_scores = {
    "R": 1,
    "P": 2,
    "S": 3,
}

outcome_scores = {
    "W": 6,
    "L": 0,
    "D": 3,
}

outcomes = {
    ("R", "R"): "D",
    ("R", "P"): "W",
    ("R", "S"): "L",
    ("P", "R"): "L",
    ("P", "P"): "D",
    ("P", "S"): "W",
    ("S", "R"): "W",
    ("S", "P"): "L",
    ("S", "S"): "D",
}


def main(args):
    """
    The main function entrypoint.
    """
    total = sum(score for score in calculate_score(parse_input(args.infile)))
    print(total)


def parse_input(infile):
    """
    Parse each line of input.
    Yield opponent_selection, your_selection.
    """
    for line in infile:
        line = line.strip()
        parts = line.split()
        opponent_selection = opponent_map[parts[0]]
        my_selection = my_map[parts[1]]
        yield opponent_selection, my_selection


def calculate_score(selections_seq):
    """
    Calculate the score from the selections tuple.
    """
    for selections in selections_seq:
        _, me = selections
        outcome = outcomes[(selections)]
        shape_score = shape_scores[me]
        outcome_score = outcome_scores[outcome]
        yield shape_score + outcome_score


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 2, part 1")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
