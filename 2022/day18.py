#! /usr/bin/env python

import argparse
import sys


def main(args):
    """
    The main function entrypoint.
    """
    padding = args.padding
    space = set([])
    for coordinate in parse_coordinates(args.infile):
        space.add(coordinate)
    total_exposed = 0
    for x0, y0, z0 in space:
        exposed = 6
        if (x0 - 1, y0, z0) in space:
            exposed -= 1
        if (x0 + 1, y0, z0) in space:
            exposed -= 1
        if (x0, y0 - 1, z0) in space:
            exposed -= 1
        if (x0, y0 + 1, z0) in space:
            exposed -= 1
        if (x0, y0, z0 - 1) in space:
            exposed -= 1
        if (x0, y0, z0 + 1) in space:
            exposed -= 1
        total_exposed += exposed
    print("Total exposed sides:", total_exposed)
    x_max = -sys.maxsize
    y_max = -sys.maxsize
    z_max = -sys.maxsize
    x_min = sys.maxsize
    y_min = sys.maxsize
    z_min = sys.maxsize
    for x0, y0, z0 in space:
        x_max = max(x_max, x0)
        y_max = max(y_max, x0)
        z_max = max(z_max, x0)
        x_min = min(x_min, x0)
        y_min = min(y_min, x0)
        z_min = min(z_min, x0)
    x_max += padding
    y_max += padding
    z_max += padding
    x_min -= padding
    y_min -= padding
    z_min -= padding
    print("x bounds:", x_min, x_max)
    print("y bounds:", y_min, y_max)
    print("z bounds:", z_min, z_max)
    bounds = ((x_min, x_max), (y_min, y_max), (z_min, z_max))
    surface_count = count_surface(space, bounds)
    print("Surface count:", surface_count)


def count_surface(space, bounds):
    """
    Count exposed surfaces, but not inner cavities.
    """
    (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounds
    start = (x_min, y_min, z_min)
    stack = [start]
    surface_count = 0
    steam_space = set([])
    while len(stack) > 0:
        cell = stack.pop()
        # print("Looking at steam cell at pos {}".format(cell))
        for dimension in range(3):
            dimension_min, dimension_max = bounds[dimension]
            start_value = cell[dimension]
            for direction in (-1, 1):
                new_cell = list(cell)
                value = start_value + direction
                if value < dimension_min or value > dimension_max:
                    continue
                new_cell[dimension] = value
                new_cell = tuple(new_cell)
                # print("Considering space at pos {}".format(new_cell))
                if new_cell in space:
                    # Steam can't expand to this space-- a surface was
                    # encountered.
                    surface_count += 1
                    # print(
                    #     "Steam can't expand into this space-- it is blocked by a surface."
                    # )
                    continue
                if new_cell in steam_space:
                    # print("Steam has already expanded into this space.")
                    continue
                # print("Steam expands into this space.")
                steam_space.add(new_cell)
                stack.append(new_cell)
    return surface_count


def parse_coordinates(infile):
    """
    Generator produces coordinates from input file.
    """
    for line in infile:
        line = line.strip()
        parts = line.split(",")
        coordinate = tuple(int(n) for n in parts)
        yield coordinate


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 18")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-p",
        "--padding",
        type=int,
        default=5,
        action="store",
        help="Padding for the bounding cube.",
    )
    args = parser.parse_args()
    main(args)
