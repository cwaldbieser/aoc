#! /usr/bin/env python

import argparse
import itertools

instruction_map = {
    "addx": ["noop", "addx"],
    "noop": ["noop"],
}


def main(args):
    """
    The main function entrypoint.
    """
    crt_cols = 40
    crt = init_crt(cols=crt_cols)
    sample_cycles = itertools.count(args.start_cycle, args.interval)
    sample_total = 0
    instructions = parse_input(args.infile)
    registers = {"X": 1}
    sample_cycle = next(sample_cycles)
    for t0, (instruction, argument) in enumerate(instructions):
        t = t0 + 1
        print(
            "t: {:5d}, instr: {}, arg: {:7d}, regX: {:7d}".format(
                t, instruction, argument, registers["X"]
            ),
            end="",
        )
        if t == sample_cycle:
            signal_strength = registers["X"] * t
            sample_total += signal_strength
            sample_cycle = next(sample_cycles)
            print(" * signal strength: {:10d}".format(signal_strength))
        else:
            print("")
        scancol = t0 % crt_cols
        pixels = get_pixels(registers["X"])
        if scancol in pixels:
            plot_pixel(crt, t0)
        if instruction == "addx":
            registers["X"] += argument
    print("")
    print("Total signal strength: {}".format(sample_total))
    print("")
    plot_crt(crt)


def plot_pixel(crt, t):
    """
    Plot a pixel on the CRT.
    """
    row0 = crt[0]
    row_size = len(row0)
    row_num = t // row_size
    row_pos = t - row_num * row_size
    row = crt[row_num]
    row[row_pos] = "#"


def get_pixels(x):
    """
    Get the 3 pixels.
    """
    return set([x-1, x, x+1])


def plot_crt(crt):
    """
    Plot the CRT.
    """
    for row in crt:
        print("".join(row))


def init_crt(cols=40, rows=6):
    """
    Return an initialized CRT representation.
    """
    crt = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            row.append(".")
        crt.append(row)
    return crt



def parse_input(infile):
    """
    Generator produces instructions from each line of input.
    """
    for line in infile:
        line = line.strip()
        parts = line.split()
        instruction = parts[0]
        argument = 0
        if len(parts) > 1:
            argument = int(parts[1])
        instr_cycles = instruction_map[instruction]
        for instr_code in instr_cycles:
            yield instr_code, argument


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 10")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "--start-cycle",
        type=int,
        default=20,
        help="The starting CPU cycle at which to sample signal strength.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=40,
        help="The CPU cycle interval at which to sample signal strength.",
    )
    args = parser.parse_args()
    main(args)
