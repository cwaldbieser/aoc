#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    search_max = args.search_max
    inspect_row = args.inspect_row
    sensor_readings = []
    for sensor, beacon in parse_sensor_data(args.infile):
        sx, sy = sensor
        bx, by = beacon
        dist = calc_manhatten_dist(sensor, beacon)
        sensor_readings.append((sensor, beacon, dist))
        print(
            "Sensor: {}, closest beacon: {}, distance: {}".format(sensor, beacon, dist)
        )
    empty = calc_empty_row_spots(inspect_row, sensor_readings)
    empty_count = len(empty)
    print(
        "No beacon could be in at least {} positions for row {}.".format(
            empty_count, inspect_row
        )
    )
    for row in range(0, search_max + 1):
        covered, combined = is_row_empty(row, sensor_readings)
        if len(combined) > 1:
            print("Row {} is interesting.".format(row))
            ex = combined[0][1]
            for rstart, rend in combined[1:]:
                for x in range(ex + 1, rstart):
                    tuning_freq = x * 4_000_000 + row
                    print(
                        "  - Coords ({}, {}) tuning frequency: {}".format(
                            x, row, tuning_freq
                        )
                    )
            continue
        coverage = combined[0]
        cstart, cend = coverage
        if cstart > 0 or cend < search_max:
            print("Row {} is interesting.".format(row))
            print(combined)


def is_row_empty(row, sensor_readings):
    """
    Return True if the row is empty; False otherwise.
    """
    covered_ranges = []
    for sensor, beacon, dist in sensor_readings:
        sx, sy = sensor
        bx, by = beacon
        dist_to_row = abs(sy - row)
        if dist_to_row > dist:
            continue
        hdist = dist - dist_to_row
        rstart = sx - hdist
        rend = sx + hdist
        covered_ranges.append((rstart, rend))
    covered_ranges.sort()
    combined_ranges = []
    start = covered_ranges[0][0]
    end = covered_ranges[0][1]
    for rstart, rend in covered_ranges[1:]:
        if rstart <= end + 1:
            end = max(rend, end)
            continue
        combined_ranges.append((start, end))
        start = rstart
        end = rend
    combined_ranges.append((start, end))
    return covered_ranges, combined_ranges


def calc_empty_row_spots(inspect_row, sensor_readings, include_beacons=False):
    """
    Calculate the number of positions in `inspect_row` where there could be no
    distress beacon.
    Returns a set of the empty positions.
    """
    beacon_positions = set([])
    empty_positions = set([])
    for sensor, beacon, dist in sensor_readings:
        sx, sy = sensor
        bx, by = beacon
        dist_to_row = abs(sy - inspect_row)
        if dist_to_row > dist:
            continue
        hdist = dist - dist_to_row
        rstart = sx - hdist
        rend = sx + hdist + 1
        for x in range(rstart, rend):
            empty_positions.add(x)
        if not include_beacons:
            if by == inspect_row:
                beacon_positions.add(bx)
    if not include_beacons:
        empty_positions -= beacon_positions
    return empty_positions


def calc_manhatten_dist(sensor, beacon):
    """
    Calculate the Manhatten distance between the sensor and the beacon.
    """
    sx, sy = sensor
    bx, by = beacon
    xdist = abs(sx - bx)
    ydist = abs(sy - by)
    dist = xdist + ydist
    return dist


def parse_sensor_data(infile):
    """
    Generator produces sensor and nearest beacon coordinates from input file.
    """
    for line in infile:
        line = line.strip()
        parts = line.split(":")
        sensor = parse_coords(parts[0])
        beacon = parse_coords(parts[1])
        yield sensor, beacon


def parse_coords(coord_str):
    """
    Parse coordinates from string.
    """
    parts = coord_str.split()
    x = None
    y = None
    for part in parts:
        if part.startswith("x="):
            x = int(part[2:].rstrip(","))
            continue
        if part.startswith("y="):
            y = int(part[2:].rstrip(":"))
            continue
    return (x, y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 15")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "--inspect-row",
        type=int,
        action="store",
        default=2_000_000,
        help="Inspect the row at INSPECT_ROW",
    )
    parser.add_argument(
        "--search-max",
        type=int,
        default=4_000_000,
        action="store",
        help="The maximum x or y coordinate to search.",
    )
    args = parser.parse_args()
    main(args)
