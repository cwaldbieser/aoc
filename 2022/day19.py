#! /usr/bin/env python

import argparse
import collections


def main(args):
    """
    The main function entrypoint.
    """
    max_time = args.max_time
    max_blueprints = args.max_blueprints
    no_quality = args.no_quality
    blueprints = parse_blueprints(args.infile)
    blueprints = dict(blueprints)
    total_quality = 0
    geode_product = 1
    for bpnum, (label, blueprint) in enumerate(blueprints.items()):
        if max_blueprints is not None and bpnum == max_blueprints:
            break
        bid = int(label.split()[-1])
        print_heading("Blueprint", "=")
        print_blueprint(label, blueprint)
        robots = [1, 0, 0, 0]
        resources = [0, 0, 0, 0]
        res_caps = calc_resource_caps(blueprint)
        res_caps_tuple = (
            res_caps["ore"],
            res_caps["clay"],
            res_caps["obsidian"],
            res_caps["geode"],
        )
        optimized_blueprint = blueprint_to_tuple(blueprint)
        cache = {}
        try:
            robots, resources = evaluate_blueprint(
                cache=cache,
                blueprint_id=bid,
                time=1,
                max_time=max_time,
                blueprint=optimized_blueprint,
                robots=robots,
                resources=resources,
                resource_caps=res_caps_tuple,
                earlier_optimization=0b000,
            )
        except KeyboardInterrupt:
            print("Cache size:", len(cache))
            raise
        geodes = resources[3]
        print_counter("Robots", robots)
        print_counter("Resources", resources)
        quality = bid * geodes
        total_quality += quality
        geode_product *= geodes
        if not no_quality:
            print("Blueprint quality:", quality)
        print("")
    if not no_quality:
        print("Total quality:", total_quality)
    print("Geode product:", geode_product)


def blueprint_to_tuple(blueprint):
    """
    Convert blueprint format.
    Original format: b[robot_type] -> [(qty, resource_type), ...]
    New format:
        (
            (o1, c, o2, g),
            (o1, c, o2, g),
            (o1, c, o2, g),
            (o1, c, o2, g),
        )
    """
    robot_recipies = []
    for robot_type in ("ore", "clay", "obsidian", "geode"):
        resources_map = dict((rtype, qty) for qty, rtype in blueprint[robot_type])
        resources = []
        for resource_type in ("ore", "clay", "obsidian", "geode"):
            resources.append(resources_map.get(resource_type, 0))
        robot_recipies.append(tuple(resources))
    robot_recipies = tuple(robot_recipies)
    return robot_recipies


def print_counter(title, counter):
    """
    Print a counter.
    """
    print(title)
    print("-" * len(title))
    print("")
    keys = ["ore", "clay", "obsidian", "geode"]
    for key, qty in zip(keys, counter):
        print("- {:10}: {:3d}".format(key, qty))
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


def evaluate_blueprint(
    cache,
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
    cache_key = (time, tuple(robots), tuple(resources), earlier_optimization)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Harvest
    new_allocations = harvest_resources(robots, resources)

    if time == max_time:
        rval = (robots, list(a + b for a, b in zip(resources, new_allocations)))
        # print("Max time reached.  Returning:", rval)
        if len(cache) == 35_776_709:
            cache.clear()
        cache[cache_key] = rval
        return rval

    # Choices:
    # - Wait.
    # - Produce a robot of some type.
    winner = [0, 0, 0, 0], [0, 0, 0, 0]

    # Choose which resource (or no resource) to produce.
    choices = [3, 2, 1, 0, None]
    # No point in producing anything other than geode robots in the 2nd last
    # round.
    if time == max_time - 1:
        choices = [3, None]
    if time == max_time - 2:
        choices = [3, 2, 0, None]
    # Determine which paths are possible.
    possible_lst = [False, False, False, False]
    for restype in choices[:-1]:
        possible_lst[restype] = True
        costs = blueprint[restype]
        for res_idx, qty in enumerate(costs):
            if resources[res_idx] < qty:
                possible_lst[restype] = False
                break
    # Try each path ...
    for restype in choices:
        # print("Path is:", restype)
        if restype is None:
            new_robots = list(robots)
            new_resources = list(a + b for a, b in zip(resources, new_allocations))
        else:
            cap = resource_caps[restype]
            if cap != 0 and robots[restype] == cap:
                # We've maxed out this resource production.
                continue
            costs = blueprint[restype]
            can_produce = possible_lst[restype]
            if not can_produce:
                continue
            if restype == 0 and (earlier_optimization & 0x001) != 0:
                continue
            if restype == 1 and (earlier_optimization & 0x010) != 0:
                continue
            if restype == 2 and (earlier_optimization & 0x100) != 0:
                continue
            # print("Building robot of type {}.".format(restype))
            new_robots = list(robots)
            new_robots[restype] += 1
            new_resources = list(
                a - b + c for a, b, c in zip(resources, costs, new_allocations)
            )
        # Throw away extra resources
        tmp_resources = []
        for qty, cap in zip(new_resources, resource_caps):
            if cap != 0:
                max_qty = cap * (max_time - time)
            else:
                max_qty = qty
            tmp_resources.append(min(max_qty, qty))
        new_resources = tmp_resources
        # Get results from the future.
        bitmap = 0b000
        if restype is None:
            if possible_lst[0]:
                bitmap |= 0b001
            if possible_lst[1]:
                bitmap |= 0b010
            if possible_lst[2]:
                bitmap |= 0b100
        future_results = evaluate_blueprint(
            cache=cache,
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
        if b1[3] >= a1[3]:
            winner = future_results
        # If you can build a geode robot, do it.
        # No reason to try other paths.
        if restype == 3:
            break
    if len(cache) == 35_776_709:
        cache.clear()
    cache[cache_key] = winner
    return winner


def harvest_resources(robots, resources):
    """
    Harvest resources and updated `resources`.
    """
    additional_resources = [0, 0, 0, 0]
    for resource_index, qty in enumerate(robots):
        additional_resources[resource_index] += qty
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
    parser.add_argument("-t", "--max-time", type=int, default=24, help="Maximum time.")
    parser.add_argument("-b", "--max-blueprints", type=int, help="Max. blueprints.")
    parser.add_argument(
        "--no-quality", action="store_true", help="Don't show quality levels."
    )
    args = parser.parse_args()
    main(args)
