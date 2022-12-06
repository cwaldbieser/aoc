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

reverse_outcome_map = {
    ("R", "W"): "P",
    ("R", "L"): "S",
    ("R", "D"): "R",
    ("P", "W"): "S",
    ("P", "L"): "R",
    ("P", "D"): "P",
    ("S", "W"): "R",
    ("S", "L"): "P",
    ("S", "D"): "S",
}

part_2_outcome_map = {
    "X": "L",
    "Y": "D",
    "Z": "W",
}


def main(args):
    """
    The main function entrypoint.
    """
    part_2 = args.part_2
    total = sum(
        score
        for score in calculate_score(
            parse_input(args.infile, part_2=part_2), part_2=part_2
        )
    )
    print(total)


def parse_input(infile, part_2=False):
    """
    Parse each line of input.
    Yield a tuple (input1, input2).
    """
    for line in infile:
        line = line.strip()
        parts = line.split()
        input1 = opponent_map[parts[0]]
        if not part_2:
            input2 = my_map[parts[1]]
        else:
            input2 = part_2_outcome_map[parts[1]]
        yield input1, input2


def calculate_score(inputs_sequence, part_2=False):
    """
    Calculate scores from a sequence of inputs tuples.
    Produce the scores as a genrator.
    """
    for inputs in inputs_sequence:
        input1, input2 = inputs
        if not part_2:
            outcome = outcomes[(inputs)]
        else:
            outcome = input2
            input2 = reverse_outcome_map[(input1, outcome)]
        shape_score = shape_scores[input2]
        outcome_score = outcome_scores[outcome]
        yield shape_score + outcome_score


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 2")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-2", "--part-2", action="store_true", help="Solve for part 2 of the puzzle."
    )
    args = parser.parse_args()
    main(args)
