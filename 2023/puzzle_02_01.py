#! /usr/bin/env python

import argparse

puzzle_number = 2
maximums = (12, 13, 14)


def main(args):
    """
    Main program entrypoint.
    """
    total = 0
    for n, samples in enumerate(parse_lines(args.file)):
        game_number = n + 1
        possible = True
        for r, g, b in samples:
            sample_possible = r <= maximums[0] and g <= maximums[1] and b <= maximums[2]
            if not sample_possible:
                possible = False
                break
        if possible:
            total += game_number
        print(f"Game {game_number:03d}: {possible}")
    print(total)


def parse_lines(f):
    """
    Parse lines of input file into lists of r, g, b tuples.
    """
    for line in f:
        line = line.strip()
        parts = line.split(":")
        data_part = parts[1]
        sample_reps = data_part.split("; ")
        samples = []
        for sample_rep in sample_reps:
            sample_parts = sample_rep.split(", ")
            r, g, b = 0, 0, 0
            for sp in sample_parts:
                components = sp.split()
                count = int(components[0])
                color = components[1]
                if color == "red":
                    r = count
                elif color == "green":
                    g = count
                elif color == "blue":
                    b = count
                else:
                    raise ValueError(f"Invalid color {color}.")
                samples.append((r, g, b))
        yield samples


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"Advent of Code Puzzle {puzzle_number}")
    parser.add_argument("file", type=argparse.FileType("r"), action="store")
    args = parser.parse_args()
    main(args)
