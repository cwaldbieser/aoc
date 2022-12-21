#! /usr/bin/env python

import argparse
import collections


def main(args):
    """
    The main function entrypoint.
    """
    blueprints = parse_blueprints(args.infile)
    blueprints = dict(blueprints)
    for label, blueprint in blueprints.items():
        print(label, blueprint)
    max_time = 24
    robots = {
        "ore": 1,
    }
    resources = collections.Counter()
    for minute in range(max_time):
        print("= Minute {} =".format(minute))
        harvest_resources(robots, resources)
        print("")
    print("= Resources =")
    print(resources)


def harvest_resources(robots, resources):
    """
    Harvest resources and updated `resources`.
    """
    for resource, qty in robots.items():
        resources[resource] += qty
        print("Robots harvested {} units of {}.".format(qty, resource))


def parse_blueprints(infile):
    """
    Generator yields blueprints from input file.
    """
    for line in infile:
        line = line.strip()
        parts = line.split(": ")
        label = parts[0]
        costs = parts[1]
        parts = costs.split(". ")
        conversions = {}
        for coststr in parts:
            cost_parts = coststr.split(" robot costs ")
            robot_type = cost_parts[0].split()[-1]
            resource_parts = cost_parts[1].split()
            resources = set([])
            for word, nextword in zip(resource_parts, resource_parts[1:]):
                try:
                    qty = int(word)
                except ValueError:
                    continue
                resources.add((qty, nextword))
            conversions[robot_type] = resources
        yield label, conversions


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 19")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
