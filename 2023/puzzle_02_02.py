#! /usr/bin/env python

import argparse

puzzle_number = 2


def main(args):
    """
    Main program entrypoint.
    """
    total = 0
    for n, samples in enumerate(parse_lines(args.file)):
        game_number = n + 1
        max_r, max_b, max_g = 0, 0, 0
        for r, g, b in samples:
            max_r = max(r, max_r)
            max_g = max(g, max_g)
            max_b = max(b, max_b)
        power = max_r * max_g * max_b
        print(f"Game {game_number:03d}: power: {power: 10d}")
        total += power
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
