#! /usr/bin/env python

import argparse
import collections


def main(args):
    """
    The main function entrypoint.
    """
    blueprints = parse_blueprints(args.infile)
    blueprints = dict(blueprints)
    max_time = 24
    for label, blueprint in blueprints.items():
        print_heading("Blueprint", "=")
        print_blueprint(label, blueprint)
        robots = collections.Counter()
        robots["ore"] = 1
        resources = collections.Counter()
        res_caps = calc_resource_caps(blueprint)
        results = evaluate_blueprint(
            time=1,
            max_time=max_time,
            blueprint=blueprint,
            robots=robots,
            resources=resources,
            resource_caps=res_caps,
        )
        print(results)
        for _, resources in results:
            print(resources)


def calc_resource_caps(blueprint):
    """
    Calculate the resource caps from the blueprint.
    Since you can only produce a single robot each turn, the highest cost for a
    resource in the blueprint is also the most that can be spent with that
    resource in a single turn.  Accumulating extra resources is pointless.
    """
    caps = collections.Counter()
    capped_resources = set(("ore", "clay", "obsidian"))
    for costs in blueprint.values():
        cost_map = collections.Counter(dict(costs))
        for restype in capped_resources:
            caps[restype] = max(caps[restype], cost_map[restype])
    return caps


def memoize(f):

    cache = {}

    def _inner(**kwds):
        key = (
            kwds["time"],
            tuple(kwds["robots"].items()),
            tuple(kwds["resources"].items()),
        )
        result = cache.get(key)
        if result is None:
            result = f(**kwds)
            cache[key] = result
            print("Stored key:", key)
        return result

    return _inner


@memoize
def evaluate_blueprint(time, max_time, blueprint, robots, resources, resource_caps):
    """
    Evaluate a blueprint.
    """
    # print(
    #     "DEBUG time:",
    #     time,
    #     "max_time:",
    #     max_time,
    #     "robots:",
    #     robots,
    #     "resources:",
    #     resources,
    # )
    if time == max_time:
        return [(robots, resources)]
    # Choices:
    # - Only harvest.
    # - Produce a robot of some type.
    results = []

    # Harvest
    new_allocations = harvest_resources(robots, resources)

    # Choose which resource (or no resource) to produce.
    choices = ["geode", "obsidian", "clay", "ore", None]
    for restype in choices:
        if restype is None:
            new_robots = collections.Counter(robots)
            new_resources = collections.Counter(resources) + new_allocations
        else:
            cap = resource_caps[restype]
            if cap != 0 and robots[restype] == cap:
                # We've maxed out this resource production.
                continue
            costs = blueprint[restype]
            can_produce = True
            for qty, res in costs:
                if resources[res] < qty:
                    can_produce = False
                    break
            if not can_produce:
                continue
            # print("Building robot of type {}.".format(restype))
            new_robots = robots + collections.Counter({restype: 1})
            res_adjustment = collections.Counter(dict((res, qty) for qty, res in costs))
            # print("res_adjustment:", res_adjustment)
            new_resources = resources - res_adjustment + new_allocations
            # print("new_resources:", new_resources)
        future_results = evaluate_blueprint(
            time=time + 1,
            max_time=max_time,
            blueprint=blueprint,
            robots=new_robots,
            resources=new_resources,
            resource_caps=resource_caps,
        )
        results.extend(future_results)
    return results


def harvest_resources(robots, resources):
    """
    Harvest resources and updated `resources`.
    """
    additional_resources = collections.Counter()
    for resource, qty in robots.items():
        additional_resources[resource] += qty
        # print("- Robots harvested {} units of {}.".format(qty, resource))
    return additional_resources


def print_heading(heading, symbol="-"):
    """
    Print a heading.
    """
    print(heading)
    print(symbol * len(heading))
    print("")


def print_blueprint(label, blueprint):
    """
    Print a blueprint.
    """
    print("{}: ".format(label))
    for resource in ["geode", "obsidian", "clay", "ore"]:
        cost = blueprint.get(resource)
        if cost is None:
            continue
        print("+ {} robot".format(resource))
        for qty, res_type in cost:
            print("  - {:2d} {}".format(qty, res_type))
    print("")


def print_counters(title, counters):
    """
    Counters.
    """
    print_heading(title, '"')
    for thing, qty in counters.items():
        print("- {}: {:4}".format(thing, qty))
    print("")


def parse_blueprints(infile):
    """
    Generator yields blueprints from input file.
    """
    resource_order = {"geode": 0, "obsidian": 1, "clay": 2, "ore": 3}
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
                resource = nextword.replace(".", "")
                resources.add((qty, resource))
                ordered_costs = list(resources)
                ordered_costs.sort(key=lambda x: resource_order[x[1]])
            conversions[robot_type] = ordered_costs
        yield label, conversions


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 19")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
