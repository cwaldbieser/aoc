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
    total_quality = 0
    for label, blueprint in blueprints.items():
        bid = int(label.split()[-1])
        print_heading("Blueprint", "=")
        print_blueprint(label, blueprint)
        robots = collections.Counter()
        robots["ore"] = 1
        resources = collections.Counter()
        res_caps = calc_resource_caps(blueprint)
        robots, resources = evaluate_blueprint(
            blueprint_id=bid,
            time=1,
            max_time=max_time,
            blueprint=blueprint,
            robots=robots,
            resources=resources,
            resource_caps=res_caps,
        )
        geodes = resources["geode"]
        print_counter("Robots", robots)
        print_counter("Resources", resources)
        quality = bid * geodes
        total_quality += quality
        print("Blueprint quality:", quality)
        print("")
    print("Total quality:", total_quality)


def print_counter(title, counter):
    """
    Print a counter.
    """
    print(title)
    print("-" * len(title))
    print("")
    for key in sorted(counter.keys()):
        print("- {:10}: {:3d}".format(key, counter[key]))
    print("")


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
    info = {"blueprint_id": None}
    stats = collections.Counter()

    def _inner(**kwds):

        bid = kwds["blueprint_id"]
        blueprint_id = info["blueprint_id"]
        if bid != blueprint_id:
            print("Cache hits:", stats["hits"])
            print("Cache misses:", stats["misses"])
            info["blueprint_id"] = bid
            cache.clear()

        robots = kwds["robots"]
        resources = kwds["resources"]
        robot_key = (
            robots["geode"],
            robots["obsidian"],
            robots["clay"],
            robots["ore"],
        )
        res_key = (
            resources["geode"],
            resources["obsidian"],
            resources["clay"],
            resources["ore"],
        )
        key = (kwds["time"], robot_key, res_key)
        result = cache.get(key)
        if result is None:
            stats["misses"] += 1
            result = f(**kwds)
            if len(cache) > 18_000_000:
                print("Cache hits:", stats["hits"])
                print("Cache misses:", stats["misses"])
                cache.clear()
                print("Cache cleared.")
            cache[key] = result
            # print("Stored key:", key)
        else:
            stats["hits"] += 1
        return result

    return _inner


@memoize
def evaluate_blueprint(
    blueprint_id, time, max_time, blueprint, robots, resources, resource_caps
):
    """
    Evaluate a blueprint.
    """
    if time == max_time:
        new_allocations = harvest_resources(robots, resources)
        return (robots, resources + new_allocations)

    # Choices:
    # - Only harvest.
    # - Produce a robot of some type.
    winner = collections.Counter(), collections.Counter()

    # Harvest
    new_allocations = harvest_resources(robots, resources)

    # Choose which resource (or no resource) to produce.
    choices = ["geode", "obsidian", "clay", "ore", None]
    # No point in producing anything other than geode robots in the 2nd last
    # round.
    if time == max_time - 1:
        choices = ["geode", None]
    if time == max_time - 2:
        choices = ["geode", "obsidian", "ore", None]
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
        # Throw away extra resources
        tmp_resources = collections.Counter()
        for restype, qty in new_resources.items():
            cap = resource_caps[restype]
            if cap != 0:
                max_qty = resource_caps[restype] * (max_time - time)
            else:
                max_qty = qty
            tmp_resources[restype] = min(max_qty, qty)
        new_resources = tmp_resources
        # Get results from the future.
        future_results = evaluate_blueprint(
            blueprint_id=blueprint_id,
            time=time + 1,
            max_time=max_time,
            blueprint=blueprint,
            robots=new_robots,
            resources=new_resources,
            resource_caps=resource_caps,
        )
        a0, a1 = winner
        b0, b1 = future_results
        if b1["geode"] >= a1["geode"]:
            winner = future_results
        # If you can build a geode robot, do it.
        # No reason to try other paths.
        if restype == "geode":
            break
    return winner


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
