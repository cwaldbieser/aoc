#! /usr/bin/env python

import argparse
import sys


def main(args):
    """
    The main function entrypoint.
    """
    inspect_row = args.inspect_row
    grid_left = sys.maxsize
    grid_top = sys.maxsize
    grid_right = -sys.maxsize
    grid_bottom = -sys.maxsize
    sensor_readings = []
    for sensor, beacon in parse_sensor_data(args.infile):
        sx, sy = sensor
        bx, by = beacon
        grid_left = min(sx, bx, grid_left)
        grid_top = min(sy, by, grid_top)
        grid_right = max(sx, bx, grid_right)
        grid_bottom = max(sy, by, grid_bottom)
        dist = calc_manhatten_dist(sensor, beacon)
        sensor_readings.append((sensor, beacon, dist))
        print(
            "Sensor: {}, closest beacon: {}, distance: {}".format(sensor, beacon, dist)
        )
    print(
        "Grid bounds: ({}, {}) - ({}, {})".format(
            grid_left, grid_top, grid_right, grid_bottom
        )
    )
    empty_count = calc_empty_row_spots(inspect_row, sensor_readings)
    print(
        "No beacon could be in at least {} positions for row {}.".format(
            empty_count, inspect_row
        )
    )


def calc_empty_row_spots(inspect_row, sensor_readings):
    """
    Calculate the number of positions in `inspect_row` where there could be no
    distress beacon.
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
        if by == inspect_row:
            beacon_positions.add(bx)
    empty_positions -= beacon_positions
    return len(empty_positions)


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
        default=10,
        help="Inspect the row at INSPECT_ROW",
    )
    args = parser.parse_args()
    main(args)
