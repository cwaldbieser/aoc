#! /usr/bin/env python

import argparse
import sys

g_flow_rates = []


def main(args):
    """
    The main function entrypoint.
    """
    max_time = 30
    valves = list(parse_valves(args.infile))
    flow_rate_map = {}
    global g_flow_rates
    for label, flow_rate, connections in valves:
        print("Valve {}, flow rate: {}".format(label, flow_rate))
        for connection in connections:
            print("  - Connects to {}".format(connection))
        flow_rate_map[label] = flow_rate
        g_flow_rates.append(flow_rate)
    valve_labels, valve_map, adj_matrix = create_adj_matrix(valves)
    curr_valve_id = valve_map["AA"]
    open_valve_ids = 0x00
    for valve_id, label in enumerate(valve_labels):
        print("{}: {}".format(label, valve_id))
    for valve_id, flow_rate in enumerate(g_flow_rates):
        if flow_rate == 0:
            open_valve_ids = open_valve_ids | (0x01 << valve_id)
    print("open valves:", bin(open_valve_ids))
    time = 1

    def get_label(vid):
        label = valve_labels[abs(vid)]
        if vid < 0:
            label += "*"
        return label

    pressure, path, open_valve_ids = calc_path_and_pressure(
        adj_matrix=adj_matrix,
        max_time=max_time,
        time=time,
        curr_valve_id=curr_valve_id,
        open_valve_ids=open_valve_ids,
    )
    labels = [get_label(vid) for vid in path]
    print("Max. pressure:", pressure)
    print("Path:", labels)
    print("open valves:", bin(open_valve_ids))


def memoize(f):

    cache = {}
    arg_names = ["time", "curr_valve_id", "open_valve_ids"]

    def _inner(**kwds):
        key = tuple(kwds[arg_name] for arg_name in arg_names)
        result = cache.get(key)
        if result is None:
            result = f(**kwds)
            cache[key] = result
        return result

    return _inner


@memoize
def calc_path_and_pressure(adj_matrix, max_time, time, curr_valve_id, open_valve_ids):
    """
    Calculate the pressure released.
    """
    global g_flow_rates
    valve_count = len(adj_matrix)

    # Maximum time
    if time == max_time:
        return 0, (curr_valve_id,), open_valve_ids
    # If all valves open, stay still.
    full_set = (0x01 << (valve_count + 1)) - 1
    if open_valve_ids == full_set:
        return (
            0,
            tuple([curr_valve_id] * (max_time - time)),
            open_valve_ids,
        )

    results = []
    # Path where we open this valve.
    current_closed = (open_valve_ids & (0x01 << curr_valve_id)) == 0x00
    if current_closed:
        new_open_ids = open_valve_ids | (0x01 << curr_valve_id)
        pressure = g_flow_rates[curr_valve_id] * (max_time - time)
        future_pressure, future_path, future_open_ids = calc_path_and_pressure(
            adj_matrix=adj_matrix,
            max_time=max_time,
            time=time + 1,
            curr_valve_id=curr_valve_id,
            open_valve_ids=new_open_ids,
        )
        results.append(
            (
                (
                    pressure + future_pressure,
                    future_path,
                    future_open_ids,
                ),
                True,
            )
        )

    # Travel to adjacent valves.
    row = adj_matrix[curr_valve_id]
    for valve_id, adj_flag in enumerate(row):
        if valve_id == curr_valve_id:
            continue
        adj_flag = bool(adj_flag == 1)
        if adj_flag:
            result = calc_path_and_pressure(
                adj_matrix=adj_matrix,
                max_time=max_time,
                time=time + 1,
                curr_valve_id=valve_id,
                open_valve_ids=open_valve_ids,
            )
            results.append((result, False))
    # Pick the result with the maximum pressure.
    max_result = ((-1, None, None), False)
    for result, opened_valve in results:
        future_pressure, _, _ = result
        if future_pressure > max_result[0][0]:
            max_result = (result, opened_valve)
    (future_pressure, future_path, future_open_ids), opened_valve = max_result
    if opened_valve:
        valve_id = -curr_valve_id
    else:
        valve_id = curr_valve_id
    return future_pressure, (valve_id,) + future_path, future_open_ids


def create_adj_matrix(valves):
    """
    Create an adjacentcy matrix between valves.
    Because the matrix will have numeric indices, map each valve to a number.
    Returns (valve_labels, valve_map, adjacency_matrix)
    """
    valve_map = {}
    valve_labels = []
    for n, (label, _, _) in enumerate(valves):
        valve_map[label] = n
        valve_labels.append(label)
    node_count = len(valves)
    adj_matrix = [[sys.maxsize] * node_count for _ in range(node_count)]
    for label0, _, connections in valves:
        idx0 = valve_map[label0]
        for label1 in connections:
            idx1 = valve_map[label1]
            adj_matrix[idx0][idx1] = 1
    adj_matrix = [tuple(row) for row in adj_matrix]
    adj_matrix = tuple(adj_matrix)
    return valve_labels, valve_map, adj_matrix


def parse_valves(infile):
    """
    Generator parses valves, flow rates, and connections from `infile`.
    Produces (label, flow_rate, connections_list).
    """
    for line in infile:
        line = line.strip()
        parts = line.split()
        label = parts[1]
        rate_str = parts[4]
        flow_rate = int(rate_str.split("=")[1].rstrip(";"))
        connections = [c.rstrip(",") for c in parts[9:]]
        yield (label, flow_rate, connections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 16")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    parser.add_argument(
        "-c",
        "--cutoff",
        type=int,
        action="store",
        default=10,
        help="Experimental cutoff.",
    )
    args = parser.parse_args()
    main(args)
