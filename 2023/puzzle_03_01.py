#! /usr/bin/env python

import argparse
import re

puzzle_number = 3
number_pattern = re.compile(r"(?:[^0-9.](\d+)|(\d+)[^0-9.])")
symbol_pattern = re.compile(r"([^0-9.])")
maybe_pattern = re.compile(r"(?:[.](\d+)[.]|^(\d+)[.]|[.](\d+)$)")


def main(args):
    """
    Main program entrypoint.
    """
    total = 0
    for part_numbers in parse_row(args.file):
        total += sum(part_numbers)
    print("")
    print(f"TOTAL: {total}")


def parse_row(f):
    """
    Generator produces a tuple of part_numbers, symbols, and maybe_parts.
    """
    prev_maybe_parts = set([])
    prev_symbols = {}
    for line in f:
        line = line.strip()
        print(line)
        symbols = {}
        maybe_parts = []
        part_numbers = [number for number in parse_part_numbers(line)]
        symbols = parse_symbols(line)
        maybe_parts = set([t for t in parse_maybe_parts(line)])
        print(part_numbers)
        print(symbols)
        print(maybe_parts)

        extra_prev_maybe_parts = find_parts(prev_maybe_parts, symbols)
        part_numbers.extend([value for value, _, _ in extra_prev_maybe_parts])

        extra_maybe_parts = find_parts(maybe_parts, prev_symbols)
        part_numbers.extend([value for value, _, _ in extra_maybe_parts])
        maybe_parts -= set(extra_maybe_parts)

        print("-----------")
        print(part_numbers)
        print(maybe_parts)

        prev_symbols = symbols
        prev_maybe_parts = maybe_parts
        yield part_numbers


def find_parts(questionable_parts, symbols):
    """
    Determine if any `questionable_parts` are actually parts.
    """
    parts = []
    for part, pos_start, pos_end in questionable_parts:
        for pos in range(pos_start - 1, pos_end + 1):
            if pos in symbols:
                parts.append((part, pos_start, pos_end))
                break
    return parts


def parse_maybe_parts(s):
    """
    Generator yields (number, start_pos, end_pos) for numbers that *might* be
    part numbers.
    """
    offset = 0
    while s:
        m = maybe_pattern.search(s)
        if not m:
            break
        both, before, after = m.groups()
        if both:
            abs_pos = offset + m.start(1)
            yield (int(both), abs_pos, abs_pos + len(both))
            pos = m.end(1)
            s = s[pos:]
        elif before:
            abs_pos = offset + m.start(2)
            yield (int(before), abs_pos, abs_pos + len(before))
            pos = m.end(2)
            s = s[pos:]
        elif after:
            abs_pos = offset + m.start(3)
            yield (int(after), abs_pos, abs_pos + len(after))
            pos = m.end(3)
            s = s[pos:]
        else:
            raise Exception(f"Input '{s}' matched but produces no groups!")
        offset += pos


def parse_symbols(s):
    """
    Returns a set of positions which contain symbols.
    """
    positions = set()
    for m in symbol_pattern.finditer(s):
        positions.add(m.start())
    return positions


def parse_part_numbers(s):
    """
    Generator parses and produces part numbers from string `s`.
    """
    while s:
        m = number_pattern.search(s)
        if not m:
            break
        before, after = m.groups()
        if before:
            yield int(before)
            pos = m.end(1)
            s = s[pos:]
        elif after:
            yield int(after)
            pos = m.end(2)
            s = s[pos:]
        else:
            raise Exception(f"Input '{s}' matched but produces no groups!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"Advent of Code Puzzle {puzzle_number}")
    parser.add_argument("file", type=argparse.FileType("r"), action="store")
    args = parser.parse_args()
    main(args)
