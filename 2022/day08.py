#! /usr/bin/env python

import argparse
import pprint


def main(args):
    """
    The main function entrypoint.
    """
    grid = parse_grid(args.infile)
    pprint.pprint(grid)
    grid_size = get_grid_size(grid)
    print("Grid size is {}x{}".format(*grid_size))
    total = 0
    for row, column, _ in itergrid(grid):
        if is_visible(grid, row, column):
            total += 1
            print("Tree at {}x{} is visible.".format(row, column))
    print("")
    print("{} trees are visible.".format(total))


def itergrid(grid):
    """
    Generator iterates over grid coordinates.
    Produces values (row, column, value).
    """
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            yield (x, y, value)


def is_visible(grid, x, y):
    """
    Determine if the value at (x, y) in the grid is visible.
    """
    considered_value = grid_get(grid, x, y)
    visible = True
    grid_rows, grid_cols = get_grid_size(grid)
    visible_east = True
    visible_west = True
    visible_north = True
    visible_south = True
    for x0 in range(0, x):
        value = grid_get(grid, x0, y)
        if value >= considered_value:
            visible_east = False
            break
    for x0 in range(x+1, grid_rows):
        value = grid_get(grid, x0, y)
        if value >= considered_value:
            visible_west = False
            break
    for y0 in range(0, y):
        value = grid_get(grid, x, y0)
        if value >= considered_value:
            visible_north = False
            break
    for y0 in range(y+1, grid_cols):
        value = grid_get(grid, x, y0)
        if value >= considered_value:
            visible_south = False
            break
    visible = visible_east or visible_west or visible_north or visible_south
    return visible


def get_grid_size(grid):
    """
    Return the grid dimensions as a tuple (rows, columns).
    """
    columns = len(grid)
    rows = len(grid[0])
    return rows, columns


def grid_get(grid, x, y):
    """
    Get the value of the grid at row `x`, column `y`.
    """
    row = grid[y]
    value = row[x]
    return value


def parse_grid(infile):
    """
    Parse the input file into a grid of integers.
    """
    grid = []
    for line in infile:
        line = line.strip()
        row = [int(c) for c in line]
        grid.append(row)
    return grid


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 8")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
