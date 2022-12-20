#! /usr/bin/env python

import argparse
import itertools

shapes = [
    ["####"],
    [
        ".#.",
        "###",
        ".#.",
    ],
    [
        "###",
        "..#",
        "..#",
    ],
    [
        "#",
        "#",
        "#",
        "#",
    ],
    [
        "##",
        "##",
    ],
]


def main(args):
    """
    The main function entrypoint.
    """
    quiet = args.quiet
    max_rocks = args.rocks
    shape_genrator = itertools.cycle(shapes)
    gas_jets = parse_gas_jets(args.infile)
    chamber_width = 7
    start_left_off = 2
    start_bottom_off = 3
    chamber = []
    rock = None
    rock_height = 0
    tallest_rock_top = 0
    rock_count = 0
    for jet in itertools.cycle(gas_jets):
        if rock is None:
            rock = next(shape_genrator)
            rock_height = len(rock)
            rock_left = start_left_off
            rock_bottom = tallest_rock_top + start_bottom_off
            rock_top = rock_bottom + rock_height
            while len(chamber) < rock_top:
                chamber.append("." * chamber_width)
            if not quiet:
                rock_composite = superimpose_rock_on_cavity(
                    rock, rock_left, rock_bottom, chamber_width
                )
                print("= NEW ROCK =")
                plot_object(rock_composite)
                print("")
                print("= CHAMBER =")
                plot_object(chamber)
                print("")
        if jet == "<":
            new_left = rock_left - 1
        elif jet == ">":
            new_left = rock_left + 1
        if not collision(chamber, chamber_width, rock, new_left, rock_bottom):
            rock_left = new_left
        if not quiet:
            rock_composite = superimpose_rock_on_cavity(
                rock, rock_left, rock_bottom, chamber_width
            )
            print("==", "JET PUSHED ROCK:", jet, "==")
            plot_object(rock_composite)
            print("")
        new_bottom = rock_bottom - 1
        if not collision(chamber, chamber_width, rock, rock_left, new_bottom):
            rock_bottom = new_bottom
        else:
            place_rock_in_chamber(chamber, chamber_width, rock, rock_left, rock_bottom)
            if not quiet:
                print("ROCK COMES TO REST AT ({:6d},{:6d}).".format(rock_left, rock_bottom))
                plot_object(chamber)
            rock = None
            rock_top = rock_bottom + rock_height
            if rock_top > tallest_rock_top:
                tallest_rock_top = rock_top
            rock_count += 1
            if rock_count == max_rocks:
                break
    print("Highest rock at {}.".format(tallest_rock_top))


def plot_object(thing):
    """
    Plot an object.
    """
    print("")
    for row in reversed(thing):
        print(row)
    print("")


def place_rock_in_chamber(chamber, chamber_width, rock, rock_left, rock_bottom):
    """
    Place a rock in the chamber.
    """
    rock_height = len(rock)
    rock_top = rock_bottom + rock_height
    section = chamber[rock_bottom:rock_top]
    rock_composite = superimpose_rock_on_cavity(
        rock, rock_left, rock_bottom, chamber_width
    )
    new_section = []
    for chamber_row, rock_row in zip(section, rock_composite):
        new_row = []
        for c0, c1 in zip(chamber_row, rock_row):
            if c0 == "#" or c1 == "#":
                new_row.append("#")
            else:
                new_row.append(".")
        new_section.append("".join(new_row))
    chamber[rock_bottom:rock_top] = new_section


def collision(chamber, chamber_width, rock, rock_left, rock_bottom):
    """
    Returns True if the placement of a rock would collide with another rock in
    the chamber of the chamber's edge.
    """
    if rock_left < 0:
        return True
    if rock_bottom < 0:
        return True
    rock_width = max(len(row) for row in rock)
    if rock_left + rock_width - 1 >= chamber_width:
        return True
    rock_height = len(rock)
    rock_top = rock_bottom + rock_height
    rock_composite = superimpose_rock_on_cavity(
        rock, rock_left, rock_bottom, chamber_width
    )
    section = chamber[rock_bottom:rock_top]
    empty_row = "." * chamber_width
    for chamber_row, rock_row in itertools.zip_longest(
        section, rock_composite, fillvalue=empty_row
    ):
        for c0, c1 in zip(chamber_row, rock_row):
            if c0 == "#" and c1 == "#":
                return True
    return False


def superimpose_rock_on_cavity(rock, rock_left, rock_bottom, chamber_width):
    """
    Superimpose a rock on an empty field the width of the chamber.
    """
    empty_row = "." * chamber_width
    rock_height = len(rock)
    empty_field = [empty_row] * rock_height
    rock_width = len(rock[0])
    rock_right = rock_left + rock_width
    composite = []
    for row, rock_row in zip(empty_field, rock):
        new_row = row[:rock_left] + rock_row + row[rock_right:]
        composite.append(new_row)
    return composite


def parse_gas_jets(infile):
    """
    Parse gas jets.
    """
    data = infile.read().strip()
    for c in data:
        yield c


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 17")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-r", "--rocks", type=int, default=2022, help="The number of rocks to count."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Be less chatty.")
    args = parser.parse_args()
    main(args)
