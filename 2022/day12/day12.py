#! /usr/bin/env python

import argparse

import numpy as np
from scipy.sparse.csgraph import dijkstra


def main(args):
    """
    The main function entrypoint.
    """
    terrain, start_coords, end_coords = parse_terrain(args.infile)
    plot_terrain(terrain)
    print("")
    print("Start at {}.".format(start_coords))
    print("End at {}.".format(end_coords))
    col_count = get_col_count(terrain)
    connections = create_connections(terrain)
    graph = np.array(connections)
    start_terrain_id = coords_to_id(start_coords[0], start_coords[1], col_count)
    end_terrain_id = coords_to_id(end_coords[0], end_coords[1], col_count)
    dist_matrix, predecesors_fwd = dijkstra(
        graph, indices=start_terrain_id, unweighted=True, return_predecessors=True
    )
    fewest_steps = dist_matrix[end_terrain_id]
    print("Fewest steps: {}".format(fewest_steps))
    lowest_elevation_ids = get_lowest_elevation(terrain)
    dist_matrix, predecesors_fwd = dijkstra(
        graph, indices=lowest_elevation_ids, unweighted=True, return_predecessors=True
    )
    dists = [dist_row[end_terrain_id] for dist_row in dist_matrix]
    dists.sort()
    shortest = dists[0]
    print("Shortest path from any zero-elevation: {}".format(shortest))


def get_col_count(terrain):
    """
    Get the number of columns.
    """
    row0 = terrain[0]
    return len(row0)


def coords_to_id(x, y, col_count):
    return y * col_count + x


def get_lowest_elevation(terrain):
    """
    Get the terrain_ids with the lowest elevations (0).
    """
    zeroes = []
    col_count = get_col_count(terrain)
    for j, row in enumerate(terrain):
        for i, value in enumerate(row):
            if value == 0:
                terrain_id = coords_to_id(i, j, col_count)
                zeroes.append(terrain_id)
    return zeroes


def create_connections(terrain):
    """
    Create a connections matrix from the terrain grid.
    """
    moves = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
    ]
    row0 = terrain[0]
    col_count = len(row0)
    row_count = len(terrain)
    terrain_count = col_count * row_count
    connections = [[0] * terrain_count for _ in range(terrain_count)]
    for j, row in enumerate(terrain):
        for i, height in enumerate(row):
            for movenum, move in enumerate(moves):
                i1 = i + move[0]
                j1 = j + move[1]
                if i1 < 0 or j1 < 0:
                    continue
                if i1 >= col_count or j1 >= row_count:
                    continue
                next_height = terrain[j1][i1]
                if next_height - height > 1:
                    continue
                terrain_id = coords_to_id(i, j, col_count)
                next_terrain_id = coords_to_id(i1, j1, col_count)
                connections[terrain_id][next_terrain_id] = 1
    return connections


def plot_terrain(terrain, pos=None):
    """
    Plot the terrain.
    """
    ord_a = ord("a")
    if pos is None:
        pos = (None, None)
    for j, row in enumerate(terrain):
        chars = [chr(n + ord_a) for n in row]
        if j == pos[1]:
            col = pos[0]
            chars[col] = "@"
        line = "".join(chars)
        print(line)


def parse_terrain(infile):
    """
    Parse the input file and produce a terrain map.
    """
    terrain = []
    ord_a = ord("a")
    start = ord("S") - ord_a
    end = ord("E") - ord_a
    start_coords = None
    end_coords = None
    for rowno, line in enumerate(infile):
        line = line.strip()
        row = [ord(c) - ord_a for c in line]
        terrain.append(row)
        try:
            col = row.index(start)
            start_coords = (col, rowno)
            row[col] = 0
        except ValueError:
            pass
        try:
            col = row.index(end)
            end_coords = (col, rowno)
            row[col] = 25
        except ValueError:
            pass
    return terrain, start_coords, end_coords


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 12")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
