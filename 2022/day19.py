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
        print_heading("Blueprint", "=")
        print_blueprint(label, blueprint)
        evaluate_blueprint(blueprint)


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


def evaluate_blueprint(blueprint):
    """
    Evaluate a blueprint.
    """
    max_time = 24
    robots = collections.Counter()
    robots["ore"] = 1
    resources = collections.Counter()
    print_heading("Max. Ratios")
    for minute in range(1, max_time + 1):
        heading = "Minute {}".format(minute)
        print_heading(heading)
        additional_resources = harvest_resources(robots, resources)
        print("")
        invest_resources(minute, blueprint, robots, resources, goal="geode")
        print("")
        resources = resources + additional_resources
        print_heading("Resources", '"')
        for resource_type, qty in resources.items():
            print("- {}: {:4}".format(resource_type, qty))
        print("")
        print_heading("Robots", '"')
        for robot_type, qty in robots.items():
            print("- {}: {:3d}".format(robot_type, qty))
        print("")


def calculate_max_ratios(blueprint):
    """
    Calculate the maximum ratios between resource producing robots.
    """
    max_ratios = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.0))
    resources = ["geode", "obsidian", "clay", "ore"]
    for resource in resources:
        for costs in blueprint.values():
            cost_map = dict((cost_type, qty) for qty, cost_type in costs)
            res_qty = cost_map.get(resource)
            if res_qty is None:
                continue
            ratios = collections.defaultdict(lambda: 0.0)
            for cost_type, qty in cost_map.items():
                if cost_type == resource:
                    continue
                ratios[cost_type] = res_qty / qty
            if len(ratios) > 0:
                max_ratios[resource] = ratios
    return max_ratios


def invest_resources(
    minute,
    blueprint,
    robots,
    resources,
    goal,
    not_achievable=None,
    level=0,
    explain_levels=None,
):
    """
    Choose which resources to invest into which robots.
    """
    if explain_levels is None:
        explain_levels = set({})
    explain = False
    if level in explain_levels:
        explain = True
    if explain:
        print("- Goal: {}, level: {}".format(goal, level))
    if not_achievable is None:
        not_achievable = set({})
    cost = blueprint[goal]
    achievable_now = True
    for qty_required, resource in cost:
        on_hand = resources[resource]
        if on_hand < qty_required:
            achievable_now = False
            if explain:
                print("- Cannot achieve goal of creating {} robot.".format(goal))
                print("- Not enough {} available.".format(resource))
            if goal == resource:
                not_achievable = not_achievable | {goal}
            if resource in not_achievable:
                if explain:
                    print("Cannot achieve goal at this time.")
                continue
            if explain:
                print("- Investing in {} ...".format(resource))
            invest_resources(
                minute,
                blueprint,
                robots,
                resources,
                goal=resource,
                not_achievable=not_achievable | {goal},
                level=level + 1,
            )
    if achievable_now:
        print("- Creating {} robot.  Allocating resources.".format(goal))
        for qty_required, resource in cost:
            resources[resource] -= qty_required
            print(
                "- Used {} {}.  {} units of {} remain.".format(
                    qty_required, resource, resources[resource], resource
                )
            )
        robots[goal] += 1


def harvest_resources(robots, resources):
    """
    Harvest resources and updated `resources`.
    """
    additional_resources = collections.Counter()
    for resource, qty in robots.items():
        additional_resources[resource] += qty
        print("- Robots harvested {} units of {}.".format(qty, resource))
    return additional_resources


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
