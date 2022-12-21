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
    gas_jets = list(parse_gas_jets(args.infile))
    chamber_width = 7
    start_left_off = 2
    start_bottom_off = 3
    chamber = []
    rock = None
    rock_height = 0
    tallest_rock_top = 0
    rock_count = 0
    height_map = {}
    for jet_num, jet in itertools.cycle(enumerate(gas_jets)):
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
                print(
                    "ROCK {} COMES TO REST AT ({:6d},{:6d}).".format(
                        rock_count + 1, rock_left, rock_bottom
                    )
                )
                plot_object(chamber)
            rock = None
            rock_top = rock_bottom + rock_height
            if rock_top > tallest_rock_top:
                tallest_rock_top = rock_top
            rock_count += 1
            height_map[tallest_rock_top] = rock_count
            if rock_count == max_rocks:
                break
    print("Highest rock at {}.".format(tallest_rock_top))
    jet_cycle_size = len(gas_jets)
    print("Jet cycle size:", jet_cycle_size)
    # plot_object(chamber, segment_size=jet_cycle_size)
    cycle_size = find_cycle(chamber)
    cycle_start = find_first_cycle(chamber, cycle_size)
    print("Cycle start:", cycle_start)
    print("Cycle size:", cycle_size)
    rock_cycle_start = height_map[cycle_start]
    rock_cycle_end = height_map[cycle_start + cycle_size]
    rock_cycle_size = rock_cycle_end - rock_cycle_start
    print("Rock number associated with cycle start:", rock_cycle_start)
    print("Rock number associated with cycle end:", rock_cycle_end)
    print("Size of cycle in rocks:", rock_cycle_size)
    # print("- Rock cycle table -")
    cycle_offset_map = {}
    for n in range(cycle_size):
        height = n + cycle_start
        rockno = height_map.get(height)
        if rockno is not None:
            rock_offset = rockno - rock_cycle_start
            # print("Cycle offset {:8d}: rock offset {:8d}".format(n, rock_offset))
            cycle_offset_map[rock_offset] = n
    many_rocks = args.many_rocks
    if many_rocks is not None:
        print("Extrapolating for {} rocks ...".format(many_rocks))
        max_rocks = many_rocks
    leading_rocks = rock_cycle_start
    full_cycles = (max_rocks - leading_rocks) // rock_cycle_size
    print("Full cycles required:", full_cycles)
    trailing_rocks = max_rocks - (leading_rocks + rock_cycle_size * full_cycles)
    print("Trailing rocks:", trailing_rocks)
    trailing_height = cycle_offset_map[trailing_rocks]
    total_height = cycle_start + cycle_size * full_cycles + trailing_height
    print("Total height:", total_height)
    # print("")
    # print("- Rock cycle DEBUG table -")
    # for height in range(len(chamber)):
    #     rockno = height_map.get(height)
    #     if rockno is not None:
    #         print("Height {:8d}: rock number {:8d}".format(height, rockno))


def find_first_cycle(chamber, cycle_size):
    """
    Find the first cycle.
    """
    segment = chamber[cycle_size:]
    start_idx0 = None
    count = 0
    for rownum, (row, rowahead) in enumerate(zip(chamber, segment)):
        if row == rowahead:
            if start_idx0 is None:
                start_idx0 = rownum
            count += 1
            if count == cycle_size:
                return start_idx0
        else:
            start_idx0 = None
            count = 0
    return None


def find_cycle(chamber):
    """ "
    Analyze the chamber.
    """
    chamber_size = len(chamber)
    sample_idx = chamber_size - 10
    sample = chamber[sample_idx]
    idx0 = sample_idx
    start_match = None
    for idx1 in range(idx0 - 1, 0, -1):
        row = chamber[idx1]
        if row == sample:
            idx0 -= 1
            if idx0 == start_match:
                print("Found cycle from {} to {}.".format(start_match, sample_idx))
                cycle_size = sample_idx - start_match
                return cycle_size
            sample = chamber[idx0]
            if start_match is None:
                start_match = idx1
        else:
            idx0 = sample_idx
            sample = chamber[idx0]
            start_match = None
    return None


def plot_object(thing, segment_size=None):
    """
    Plot an object.
    """
    print("")
    for n, row in enumerate(reversed(thing)):
        if segment_size is not None:
            if n % segment_size == 0:
                print("-------")
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
    parser.add_argument(
        "-m",
        "--many-rocks",
        type=int,
        help="Calculate the height for MANY_ROCKS by extrapolating from the input.",
    )
    args = parser.parse_args()
    main(args)
