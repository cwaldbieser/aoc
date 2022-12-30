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
            earlier_optimization=0b000,
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
        earlier_optimization = kwds["earlier_optimization"]
        key = (kwds["time"], robot_key, res_key, earlier_optimization)
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
    blueprint_id,
    time,
    max_time,
    blueprint,
    robots,
    resources,
    resource_caps,
    earlier_optimization,
):
    """
    Evaluate a blueprint.
    """
    # print(
    #     "time:",
    #     time,
    #     ", max_time:",
    #     max_time,
    #     ", robots:",
    #     robots,
    #     ", resources:",
    #     resources,
    #     ", earlier_optimization:",
    #     earlier_optimization,
    # )
    # Harvest
    new_allocations = harvest_resources(robots, resources)

    if time == max_time:
        rval = (robots, resources + new_allocations)
        # print("Max time reached.  Returning:", rval)
        return rval

    # Choices:
    # - Wait.
    # - Produce a robot of some type.
    winner = collections.Counter(), collections.Counter()

    # Choose which resource (or no resource) to produce.
    choices = ["geode", "obsidian", "clay", "ore", None]
    # No point in producing anything other than geode robots in the 2nd last
    # round.
    if time == max_time - 1:
        choices = ["geode", None]
    if time == max_time - 2:
        choices = ["geode", "obsidian", "ore", None]
    # print("Path choices are:", choices)
    # Determine which paths are possible.
    possible_map = {}
    for restype in choices[:-1]:
        possible_map[restype] = True
        costs = blueprint[restype]
        for qty, res in costs:
            if resources[res] < qty:
                possible_map[restype] = False
                break
    # print("Possible paths are:", possible_map)
    # Try each path ...
    for restype in choices:
        # print("Path is:", restype)
        if restype is None:
            new_robots = collections.Counter(robots)
            new_resources = collections.Counter(resources) + new_allocations
        else:
            cap = resource_caps[restype]
            if cap != 0 and robots[restype] == cap:
                # We've maxed out this resource production.
                continue
            costs = blueprint[restype]
            can_produce = possible_map[restype]
            if not can_produce:
                continue
            if restype == "ore" and (earlier_optimization & 0x001) != 0:
                continue
            if restype == "clay" and (earlier_optimization & 0x010) != 0:
                continue
            if restype == "obsidian" and (earlier_optimization & 0x100) != 0:
                continue
            # print("Building robot of type {}.".format(restype))
            new_robots = robots + collections.Counter({restype: 1})
            res_adjustment = collections.Counter(dict((res, qty) for qty, res in costs))
            # print("res_adjustment:", res_adjustment)
            new_resources = resources - res_adjustment + new_allocations
        # print("new_resources:", new_resources)
        # Throw away extra resources
        tmp_resources = collections.Counter()
        for res, qty in new_resources.items():
            cap = resource_caps[res]
            if cap != 0:
                max_qty = resource_caps[res] * (max_time - time)
            else:
                max_qty = qty
            tmp_resources[res] = min(max_qty, qty)
        new_resources = tmp_resources
        # print("new_resources after extra trimming:", new_resources)
        # Get results from the future.
        bitmap = 0b000
        if restype is None:
            if possible_map.get("ore", False):
                bitmap |= 0b001
            if possible_map.get("clay", False):
                bitmap |= 0b010
            if possible_map.get("obsidian", False):
                bitmap |= 0b100
        # print("Earlier optimization bitmap:", earlier_optimization)
        future_results = evaluate_blueprint(
            blueprint_id=blueprint_id,
            time=time + 1,
            max_time=max_time,
            blueprint=blueprint,
            robots=new_robots,
            resources=new_resources,
            resource_caps=resource_caps,
            earlier_optimization=bitmap,
        )
        a0, a1 = winner
        b0, b1 = future_results
        if b1["geode"] >= a1["geode"]:
            winner = future_results
        # If you can build a geode robot, do it.
        # No reason to try other paths.
        if restype == "geode":
            break
    # print("Geode winner:", winner)
    # print("")
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
