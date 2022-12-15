#! /usr/bin/env python

import argparse
import sys


def main(args):
    """
    The main function entrypoint.
    """
    segments = parse_segments(args.infile)
    segments = list(segments)
    grid, grid_off = construct_grid(segments)
    plot_grid(grid)
    n = 0
    while simulate_sand(grid, grid_off):
        n += 1
        print("== {} ==".format(n))
        plot_grid(grid)
    print("")
    print("Dropped {} units of sand.".format(n))
    grid, grid_off = construct_grid(segments, floor=True, hpad=160)
    n = 0
    while simulate_sand(grid, grid_off):
        n += 1
        print("== {} ==".format(n))
        plot_grid(grid)
    print("")
    print("Dropped {} units of sand.".format(n + 1))


def simulate_sand(grid, grid_off):
    """
    Simulate 1 unit of sand dropping from (500, 0).
    Return True if the sand comes to rest in the grid, or False if the sand
    falls into the infinite abyss.
    """
    sand = (500, -1)
    grid_bottom = len(grid) - 1
    more_sand = True
    while True:
        x, y = sand
        if y == grid_bottom:
            more_sand = False
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
    if sand == (500, 0):
        more_sand = False
        grid_set(grid, grid_off, sand, "+")
    if more_sand:
        grid_set(grid, grid_off, sand, "+")
    return more_sand


def construct_grid(segments, floor=False, hpad=0):
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
    bound_left -= hpad
    bound_right += hpad
    if floor:
        bound_down += 2
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
    if floor:
        floor_row = grid[-1]
        for i in range(len(floor_row)):
            floor_row[i] = "#"
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


def plot_grid(grid, max_width=121):
    """
    Plot the grid.
    """
    grid_width = len(grid[0])
    start = 0
    end = grid_width
    if grid_width > max_width:
        start = (grid_width - max_width) // 2
        end = start + max_width
    for row in grid:
        print("".join(row[start:end]))


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
