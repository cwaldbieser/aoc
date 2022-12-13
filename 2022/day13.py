#! /usr/bin/env python

import argparse
import functools
import json


def main(args):
    """
    The main function entrypoint.
    """
    codes = []
    total = 0
    for n, (left, right) in enumerate(parse_pairs(args.infile)):
        pair_idx = n + 1
        print("=== Pair {} ===".format(pair_idx))
        if validate_pair(left, right):
            total += pair_idx
        codes.append(left)
        codes.append(right)
    print("Total of valid pairs is: {}".format(total))
    print("")
    divider_packets = [
        [[2]],
        [[6]],
    ]
    codes.extend(divider_packets)
    codes.sort(key=functools.cmp_to_key(cmp_pairs))
    indices = []
    for n, code in enumerate(codes):
        idx = n + 1
        if code in divider_packets:
            indices.append(idx)
            print("*", code)
        else:
            print(code)
    print("Decoder key:", functools.reduce(lambda x, y: x * y, indices))


def cmp_pairs(left, right):
    """
    If left < right return -1.
    If left > right return 1.
    If left == right return 0.
    """
    result = validate_pair(left, right)
    if result is None:
        return 0
    if result:
        return -1
    return 1


def get_type(data):
    """
    Get the type of `data`-- 'list' or 'int'.
    """
    if hasattr(data, "append"):
        return "list"
    return "int"


def validate_pair(left, right, indent=""):
    """
    Return True if pair is in the correct order.
    Return False if the pair is in the incorrect order.
    Return None if the order correctness cannot be determined.
    """
    newindent = indent + "  "
    print("{}-Compare {} vs {}".format(indent, left, right))
    ltype = get_type(left)
    rtype = get_type(right)
    if ltype == rtype == "int":
        if left < right:
            return True
        elif left > right:
            return False
        return None
    if ltype == rtype == "list":
        for newleft, newright in zip(left, right):
            result = validate_pair(newleft, newright, indent=newindent)
            if result is None:
                continue
            if result:
                return True
            return False
        leftsize = len(left)
        rightsize = len(right)
        if leftsize < rightsize:
            return True
        elif leftsize > rightsize:
            return False
        return None
    if ltype != rtype:
        if ltype == "list":
            return validate_pair(left, [right], indent=newindent)
        return validate_pair([left], right, indent=newindent)


def parse_pairs(infile):
    """
    Generator parses input file and produces pairs of inputs.
    """
    pair = []
    for line in infile:
        line = line.strip()
        if line == "":
            continue
        obj = json.loads(line)
        pair.append(obj)
        if len(pair) == 2:
            yield (pair[0], pair[1])
            pair = []


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 13")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
