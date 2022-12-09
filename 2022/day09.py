#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    hpos = (0, 0)
    tpos = (0, 0)
    visited = set([])
    for direction, count in parse_input(args.infile):
        hpos, tpos, tvisited = update_positions(hpos, tpos, direction, count)
        visited = visited.union(tvisited)
    visited_list = list(visited)
    visited_list.sort()
    for pos in visited_list:
        print("Tail visited {}.".format(pos))
    print("")
    print("Total unique positions visited by tail: {}".format(len(visited)))


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


def update_positions(hpos, tpos, direction, count):
    """
    Given Head position, Tail position, direction, and count, update the
    positions of Head and Tail, and track the positions that Tail visited.
    """
    dirmove_map = {
        "R": (1, 0),
        "L": (-1, 0),
        "U": (0, -1),
        "D": (0, 1),
    }
    move = dirmove_map[direction]
    visited = []
    for _ in range(count):
        hpos = adjust_pos(hpos, move)
        tpos = update_tail_pos(hpos, tpos)
        visited.append(tpos)
    return hpos, tpos, visited


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
    args = parser.parse_args()
    main(args)
