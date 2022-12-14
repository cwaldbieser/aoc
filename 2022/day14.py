#! /usr/bin/env python

import argparse
import sys


def main(args):
    """
    The main function entrypoint.
    """
    segments = parse_segments(args.infile)
    # print("== Segments ==")
    # for segment in segments:
    #     print(segment)
    grid, grid_off = construct_grid(segments)
    plot_grid(grid)
    n = 0
    while simulate_sand(grid, grid_off):
        n += 1
        print("== {} ==".format(n))
        plot_grid(grid)
    print("")
    print("Dropped {} units of sand.".format(n))


def simulate_sand(grid, grid_off):
    """
    Simulate 1 unit of sand dropping from (500, 0).
    Return True if the sand comes to rest in the grid, or False if the sand
    falls into the infinite abyss.
    """
    sand = (500, 0)
    grid_bottom = len(grid) - 1
    in_grid = True
    while True:
        x, y = sand
        if y == grid_bottom:
            in_grid = False
            break
        y += 1
        if grid_get(grid, grid_off, (x, y)) == ".":
            sand = (x, y)
            continue
        x, y = sand
        y += 1
        x -= 1
        if grid_get(grid, grid_off, (x, y)) == ".":
            sand = (x, y)
            continue
        x, y = sand
        y += 1
        x += 1
        if grid_get(grid, grid_off, (x, y)) == ".":
            sand = (x, y)
            continue
        break
    if in_grid:
        grid_set(grid, grid_off, sand, "+")
    return in_grid


def construct_grid(segments):
    """
    Construct a grid from the segments.
    """
    segments = list(segments)
    bound_left = sys.maxsize
    bound_right = 0
    bound_up = sys.maxsize
    bound_down = 0
    for segment in segments:
        for x, y in segment:
            bound_left = min(bound_left, x)
            bound_right = max(bound_right, x)
            bound_up = min(bound_up, y)
            bound_down = max(bound_down, y)
    bound_right = max(bound_right, 500)  # Sand start
    bound_up = min(bound_up, 0)  # Sand start
    grid_width = bound_right - bound_left + 1
    grid_height = bound_down - bound_up + 1
    grid = [["."] * grid_width for _ in range(grid_height)]
    grid_off = (bound_left, bound_up)
    for segment in segments:
        it = iter(segment)
        x0, y0 = next(it)
        for x1, y1 in it:
            if x1 == x0:
                j0 = min(y0, y1)
                j1 = max(y0, y1)
                for y in range(j0, j1 + 1):
                    grid_set(grid, grid_off, (x0, y), "#")
            elif y1 == y0:
                i0 = min(x0, x1)
                i1 = max(x0, x1)
                for x in range(i0, i1 + 1):
                    grid_set(grid, grid_off, (x, y0), "#")
            else:
                raise Exception("Segment does not form a straight line!")
            x0, y0 = x1, y1
    grid_set(grid, grid_off, (500, 0), "+")
    return grid, grid_off


def grid_set(grid, grid_off, coords, value):
    """
    Set the grid cell to `value` given the grid, its coordinate offsets, and
    the cell coordinate.
    """
    xoff, yoff = grid_off
    x, y = coords
    i = x - xoff
    j = y - yoff
    grid[j][i] = value


def grid_get(grid, grid_off, coords):
    """
    Get the value at for a grid cell given the grid, its coordinate offsets,
    and the cell coordinate.
    """
    xoff, yoff = grid_off
    x, y = coords
    i = x - xoff
    j = y - yoff
    return grid[j][i]


def plot_grid(grid):
    """
    Plot the grid.
    """
    for row in grid:
        print("".join(row))


def parse_segments(infile):
    """
    Generator yields segments.
    A segment is a list of node coordinates.
    The coordinates can be imagined as being connected by straight lines in a
    Cartesian plane.
    """
    for line in infile:
        line = line.strip()
        parts = line.split(" -> ")
        segment = [parse_coord(cs) for cs in parts]
        yield segment


def parse_coord(cs):
    """
    Parse a coordinate (x, y) from a string representation.
    """
    parts = cs.split(",")
    return int(parts[0]), int(parts[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 14")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
