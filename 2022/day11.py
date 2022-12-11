#! /usr/bin/env python

import argparse


def main(args):
    """
    The main function entrypoint.
    """
    monkeys = configure_monkeys(args.infile)
    inspections = [0] * len(monkeys)
    print("")
    print_monkey_items(monkeys)
    for round in range(20):
        print("== Round {} ==".format(round + 1))
        for n, monkey in enumerate(monkeys):
            print("Monkey {}".format(n))
            items = monkey["items"]
            monkey["items"] = []
            for item in items:
                print("  Monkey inspects an item with worry level of {}.".format(item))
                inspections[n] += 1
                operation = monkey["operation"]
                new_worry = operation(item)
                print("    Worry level changed to {}.".format(new_worry))
                new_worry = new_worry // 3
                print(
                    (
                        "    Monkey gets bored with item.  "
                        "Worry level is divided by 3 to {}."
                    ).format(new_worry)
                )
                test = monkey["test"]
                target = test(new_worry)
                monkeys[target]["items"].append(new_worry)
                print(
                    "    Item with worry level {} is thrown to monkey {}.".format(
                        new_worry, target
                    )
                )
        print("")
        print_monkey_items(monkeys)
        print("")
    for n, count in enumerate(inspections):
        print("Monkey {} inspected {} itmes.".format(n, count))
    inspections.sort()
    parts = inspections[-2:]
    second = parts[0]
    most = parts[1]
    monkey_business = most * second
    print("Monkey business score: {} x {} == {}".format(most, second, monkey_business))


def print_monkey_items(monkeys):
    """
    Print the items the monkeys are holding.
    """
    for n, monkey in enumerate(monkeys):
        print("Monkey {}: {}".format(n, ", ".join([str(n) for n in monkey["items"]])))
    print("")


def configure_monkeys(infile):
    """
    Parse monkey configuration.
    Returns a list of monkeys.
    """
    monkeys = []
    for line in infile:
        if line.startswith("Monkey"):
            monkey = parse_monkey(infile)
            monkeys.append(monkey)
    return monkeys


def parse_monkey(infile):
    """
    Parse a monkey configuration and create a monkey.
    """
    starting_items_prefix = "Starting items: "
    operation_prefix = "Operation: "
    test_prefix = "Test: "
    monkey = {}
    for line in infile:
        line = line.strip()
        if line.startswith(starting_items_prefix):
            prefix_size = len(starting_items_prefix)
            value = line[prefix_size:].replace(" ", "")
            items = [int(item) for item in value.split(",")]
            monkey["items"] = items
            continue
        if line.startswith(operation_prefix):
            prefix_size = len(operation_prefix)
            value = line[prefix_size:]
            monkey["operation"] = make_operation(value)
            continue
        if line.startswith(test_prefix):
            prefix_size = len(test_prefix)
            value = line[prefix_size:]
            predicate = parse_predicate(value)
            targets = parse_targets(infile)
            monkey["test"] = make_test(predicate, targets)
            return monkey
        raise Exception("Unexpected line: {}".format(line))


def make_operation(formula_text):
    """
    Create and return a function that transforms a number based on
    `formula_text`.
    """

    def _transform(n):
        """
        A transformation function.
        """
        locs = {"old": n, "new": None}
        exec(formula_text, None, locs)
        return locs["new"]

    return _transform


def make_test(predicate, targets):
    """
    Create a function that returns the correct target depending on the result
    returned by predicate.
    """
    return lambda n: targets[predicate(n)]


def parse_predicate(text):
    """
    Parse predicate test into a callable p(n) that takes an integer and returns
    a boolean.
    """
    parts = text.split()
    n = int(parts[-1])
    return lambda x: x % n == 0


def parse_targets(infile):
    """
    Parse the true/false targets of the test.
    """
    true_prefix = "If true:"
    false_prefix = "If false:"
    targets = {}
    for line in infile:
        line = line.strip()
        if line == "":
            return targets
        if line.startswith(true_prefix):
            parts = line.split()
            n = int(parts[-1])
            targets[True] = n
            continue
        if line.startswith(false_prefix):
            parts = line.split()
            n = int(parts[-1])
            targets[False] = n
            continue
    return targets


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 11")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
