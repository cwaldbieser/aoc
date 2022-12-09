#! /usr/bin/env python

import argparse
import itertools


def main(args):
    """
    The main function entrypoint.
    """
    n = args.n
    knots = [(0, 0)] * n
    visited = set([])
    plot_knots("start", knots)
    for direction, count in parse_input(args.infile):
        knots, tvisited = update_positions(knots, direction, count)
        visited = visited.union(tvisited)
        plot_knots("{} {}".format(direction, count), knots)
    visited_list = list(visited)
    visited_list.sort()
    for pos in visited_list:
        print("Tail visited {}.".format(pos))
    print("")
    print("Total unique positions visited by tail: {}".format(len(visited)))


def plot_knots(title, knots, gridsize=(21, 26), start=(11, 15)):
    """
    Plot knots
    """
    hcycle = itertools.cycle(range(10))
    vcycle = itertools.cycle(range(10))
    print("==== {} ====".format(title))
    print("")
    rknots = list(enumerate(knots))
    rknots.reverse()
    g_rows, g_cols = gridsize
    startx, starty = start
    print("  ", end="")
    for marker, _ in zip(hcycle, range(g_cols)):
        print(marker, end="")
    print("")
    for marker, row in zip(vcycle, range(g_rows)):
        y = row - starty
        print("{} ".format(marker), end="")
        for col in range(g_cols):
            x = col - startx
            value = "."
            pos = (x, y)
            for knot_number, knot in rknots:
                if pos == knot:
                    value = knot_number
                    if value == 0:
                        value = "H"
            print(value, end="")
        print("")
    print("")


def parse_input(infile):
    """
    Generator parses each line of the input file into (direction, position).
    """
    for line in infile:
        line = line.strip()
        parts = line.split()
        direction = parts[0]
        count = int(parts[1])
        yield direction, count


def update_positions(knots, direction, count):
    """
    Given knot positions, direction, and count, update the
    positions of the knots, and track the positions that Tail visited.
    """
    knots = knots[:]
    dirmove_map = {
        "R": (1, 0),
        "L": (-1, 0),
        "U": (0, -1),
        "D": (0, 1),
    }
    move = dirmove_map[direction]
    visited = []
    knot_count = len(knots)
    knot0 = knots[0]
    for _ in range(count):
        knot0 = adjust_pos(knot0, move)
        knots[0] = knot0
        for i in range(len(knots) - 1):
            knot = knots[i]
            nextknot = knots[i + 1]
            nextknot = update_tail_pos(knot, nextknot)
            knots[i + 1] = nextknot
            if i == knot_count - 2:
                visited.append(nextknot)
    return knots, visited


def update_tail_pos(hpos, tpos):
    """
    Calculate the new tail position based on the head position.
    """
    xoff = hpos[0] - tpos[0]
    yoff = hpos[1] - tpos[1]
    dx = 0
    dy = 0
    if abs(xoff) > 1 and yoff != 0:
        dx = sign(xoff)
        dy = sign(yoff)
    elif xoff != 0 and abs(yoff) > 1:
        dx = sign(xoff)
        dy = sign(yoff)
    elif abs(xoff) > 1 and yoff == 0:
        dx = sign(xoff)
    elif xoff == 0 and abs(yoff) > 1:
        dy = sign(yoff)
    tpos = adjust_pos(tpos, (dx, dy))
    return tpos


def sign(x):
    """
    Return 1 or -1 for positive and negative x.
    Zero raises an exception.
    """
    x = int(x)
    return x // abs(x)


def adjust_pos(pos, move):
    """
    Adjust pos by move.
    Return the new pos.
    """
    newpos = (pos[0] + move[0], pos[1] + move[1])
    return newpos


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 9")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-n", type=int, default=2, help="The number of knots in the rope."
    )
    args = parser.parse_args()
    main(args)
