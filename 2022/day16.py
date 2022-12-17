#! /usr/bin/env python

"""
Advent of Code 2022, day 16, part 1.

pressure_released == time_remaining * flow rate

From your current node:

    time_remaining = current_time_remaining - distance to node - 1

(The -1 is the time to open the valve).

So at any given node, calculate:

    (current_time_remaining - dist_to_node - 1) * flow_rate

The greatest value should be the next node.

"""

import argparse
import functools
import heapq as heap
import itertools
import sys
from collections import defaultdict


def main(args):
    """
    The main function entrypoint.
    """
    valves = list(parse_valves(args.infile))
    flow_rate_map = {}
    for label, flow_rate, connections in valves:
        print("Valve {}, flow rate: {}".format(label, flow_rate))
        for connection in connections:
            print("  - Connects to {}".format(connection))
        flow_rate_map[label] = flow_rate
    valve_labels, valve_map, adj_matrix = create_adj_matrix(valves)
    print("")
    print("====================")
    print("= Adjacency Matrix =")
    print("====================")
    plot_matrix(adj_matrix)
    distance_matrix = create_distance_matrix(adj_matrix)
    print("===================")
    print("= Distance Matrix =")
    print("===================")
    plot_matrix(distance_matrix)
    open_valve_ids = set([])
    current_valve_id = 0
    ttonv = None  # Time to open next valve.
    next_valve_id = None
    pressure_released = 0
    print("")
    print("================")
    print("Pressure Release")
    print("================")
    print("")
    for minute in range(1, 31):
        print("== Minute: {} ==".format(minute))
        t = 31 - minute
        for valve_id in open_valve_ids:
            label = valve_labels[valve_id]
            pressure = flow_rate_map[label]
            pressure_released += pressure
            print("  - Valve {} is open releasing {} pressure.".format(label, pressure))
        if ttonv is None:
            print("  - Determining next valve to move to ...")
            ttonv, next_valve_id = determine_next_valve(
                current_valve_id,
                t,
                valve_labels,
                valve_map,
                distance_matrix,
                flow_rate_map,
                open_valve_ids,
            )
            if ttonv is not None:
                print(
                    "  - Time to open valve {} (id={}): {}".format(
                        valve_labels[next_valve_id], next_valve_id, ttonv
                    )
                )
            else:
                print("  - No more valves to open.")
        if ttonv is not None and ttonv > 0:
            print("  - Time to open next valve is: ", ttonv)
            ttonv -= 1
            continue
        if ttonv == 0:
            print(
                "  - Opened valve {} (id={}).".format(
                    valve_labels[next_valve_id], next_valve_id
                )
            )
            current_valve_id = next_valve_id
            open_valve_ids.add(current_valve_id)
            next_valve_id = None
            ttonv = None
            continue
    print("Pressure released: {}".format(pressure_released))


def plot_matrix(matrix):
    """
    Plot a matrix for debugging.
    """
    scale = itertools.cycle(range(0, 9))
    print("  ", end="")
    for i in range(len(matrix)):
        print(" {}".format(next(scale)), end="")
    print("")
    scale = itertools.cycle(range(0, 9))
    for n, row in zip(scale, matrix):
        row_rep = []
        for i in row:
            if i == sys.maxsize:
                rep = "."
            else:
                rep = str(i)
            row_rep.append(rep)
        print("{}  {}".format(n, " ".join(row_rep)))
    print("")


def create_distance_matrix(adj_matrix):
    """
    Create a distance matrix D such that D[node0][node1] gives the distance
    between node0 and node1.
    """
    dmatrix = []
    valve_count = len(adj_matrix)
    for valve_id in range(valve_count):
        _, node_costs = dijkstra(adj_matrix, valve_id)
        row = [node_costs[i] for i in range(valve_count)]
        dmatrix.append(row)
    return dmatrix


def determine_next_valve(
    curr_valve_id,
    t,
    valve_labels,
    valve_map,
    dist_matrix,
    flow_rate_map,
    open_valve_ids,
):
    """
    Determine the "time to open next valve" (`ttonv`) and the next valve.
    If there is no next valve that should be opened, both values will be set to None.
    Returns (ttonv, valve_label)
    """
    scores = []
    max_dist = max(functools.reduce(lambda x, y: x + y, dist_matrix))
    dists = dist_matrix[curr_valve_id]
    debug_info = []
    for valve_id in range(len(valve_labels)):
        dist = dists[valve_id]
        label = valve_labels[valve_id]
        flow_rate = flow_rate_map[label]
        if valve_id == curr_valve_id:
            print(
                "DEBUG: valve_id {} is curr_valve_id, setting to zero.".format(valve_id)
            )
            score = (0, 0)
        elif valve_id in open_valve_ids:
            print(
                "DEBUG: valve_id {} in open_valve_ids, setting to zero.".format(
                    valve_id
                )
            )
            score = (0, 0)
        elif flow_rate == 0:
            print(
                "DEBUG: valve_id {} has zero flow rate, setting to zero.".format(
                    valve_id
                )
            )
            score = (0, 0)
        else:
            if (30 - flow_rate) > (t - dist - 1):
                size_order = 0
            else:
                size_order = 1
            score = (size_order, max_dist - dist)
        data = (valve_labels[valve_id], valve_id, t, dist, flow_rate, score)
        debug_info.append(data)
        scores.append((score, valve_id))
    print(" - DEBUG INFO:")
    print("  label   id    t  dist  flow_rate  score")
    print("  -----  ---  ---  ----  ---------  -----")
    for label, valve_id, t, dist, flow_rate, score in debug_info:
        print(
            "  {:4}  {:3d}  {:3d}  {:4d}  {:9d}  {}".format(
                label, valve_id, t, dist, flow_rate, score
            )
        )
    print("")
    scores.sort()
    top_score, valve_id = scores[-1]
    if top_score == (0, 0):
        return None, None
    return dists[valve_id], valve_id


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


def dijkstra(adj_matrix, starting_node):
    """
    Dijkstra's shortest path algorithm.
    Given `G`, a graph and a `starting_node`, return a
    (`parents_map`, `node_costs`).
    G should be an adjacentcy matrix such that G[node0][node1] produces the
    distance from node0 to node1.
    """
    visited = set()
    parents_map = {}
    pq = []
    node_costs = defaultdict(lambda: float("inf"))
    node_costs[starting_node] = 0
    heap.heappush(pq, (0, starting_node))

    while pq:
        # go greedily by always extending the shorter cost nodes first
        _, node = heap.heappop(pq)
        visited.add(node)

        for adj_node, weight in enumerate(adj_matrix[node]):
            if adj_node in visited:
                continue

            newCost = node_costs[node] + weight
            if node_costs[adj_node] > newCost:
                parents_map[adj_node] = node
                node_costs[adj_node] = newCost
                heap.heappush(pq, (newCost, adj_node))

    return parents_map, node_costs


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 16")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
