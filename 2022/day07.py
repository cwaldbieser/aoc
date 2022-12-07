#! /usr/bin/env python

import argparse
import itertools
import pprint


def main(args):
    """
    The main function entrypoint.
    """
    filesystem = parse_filesystem(args.infile)
    print("Filesystem representation:")
    pprint.pprint(filesystem)
    print("")
    root_folder = filesystem["/"]
    folder_sizes = []
    calc_folder_sizes_in_tree("/", root_folder, folder_sizes)
    max_size = 100_000
    small_folders = [obj for obj in folder_sizes if obj["size"] <= max_size]
    total = 0
    print("Folders smaller than {} bytes:".format(max_size))
    for obj in small_folders:
        name = obj["name"]
        size = obj["size"]
        print("- folder: {}, Size: {}".format(name, size))
        total += size
    print("Total size of small folders: {}".format(total))
    print("")
    total_filesystem_size = 70_000_000
    update_required_size = 30_000_000
    total_used_space = folder_sizes[-1]["size"]
    available_space = total_filesystem_size - total_used_space
    folder_sizes.sort(key=lambda o: o["size"])
    for obj in folder_sizes:
        if available_space + obj["size"] >= update_required_size:
            print("Total filesystem size: {}".format(total_filesystem_size))
            print("Update required space: {}".format(update_required_size))
            print("Total available space: {}".format(available_space))
            print(
                (
                    "Deleting folder `{}` (size {}) will result in "
                    "a total of {} available space."
                ).format(obj["name"], obj["size"], obj["size"] + available_space)
            )
            break


def calc_folder_sizes_in_tree(name, folder_obj, results):
    """
    Calculate the size of every folder in the tree rooted at `folder`.
    """
    contents = folder_obj["contents"]
    size = 0
    for objname, fsobj in contents.items():
        obj_size = fsobj.get("size")
        if obj_size is not None:
            size += obj_size
        else:
            calc_folder_sizes_in_tree(objname, fsobj, results)
            size += results[-1]["size"]
    result = {"name": name, "size": size}
    results.append(result)


def make_folder_obj():
    """
    Make a folder representation.
    """
    return {"contents": {}}


def make_file_obj(size):
    """
    Make a file representation.
    """
    return {"size": size}


def parse_filesystem(infile):
    """
    Parse the shell commands into a filesystem representation.
    """
    shell_state = {"cwd": []}
    fsinfo = {
        "/": make_folder_obj(),
    }
    infile, lookahead = itertools.tee(infile)
    lookahead = itertools.chain(lookahead, [""])
    next(lookahead)
    for line, nextline in zip(infile, lookahead):
        line = line.strip()
        if line.startswith("$"):
            process_command(infile, lookahead, shell_state, fsinfo, line)
            continue
        print("Something went wrong parsing the shell commands!")
        print("line", line)
        print("shell_state", shell_state)
        print("fsinfo", fsinfo)
    return fsinfo


def process_command(infile, lookahead, shell_state, fsinfo, line):
    """
    Process "shell commands" to construct the filesystem representation.
    """
    parts = line.split()
    command = parts[1]
    if command == "cd":
        process_cd_command(shell_state, fsinfo, parts[2])
        return
    if command == "ls":
        process_ls_comand(shell_state, fsinfo, infile, lookahead)
        return


def get_cwd(shell_state, fsinfo):
    """
    Get the folder representation.
    """
    cwd = shell_state["cwd"]
    folder = fsinfo["/"]
    for key in cwd:
        folder = folder["contents"][key]
    return folder


def process_cd_command(shell_state, fsinfo, destination):
    """
    Simulate the `cd` command.
    """
    folder = get_cwd(shell_state, fsinfo)
    contents = folder["contents"]
    cwd = shell_state["cwd"]
    if destination == "/":
        cwd[:] = []
        return
    if destination == "..":
        cwd[:] = cwd[:-1]
        return
    if destination not in contents:
        contents[destination] = make_folder_obj()
    cwd.append(destination)


def process_ls_comand(shell_state, fsinfo, infile, lookahead):
    """
    Simulate the `ls` command.
    """
    folder = get_cwd(shell_state, fsinfo)
    contents = folder["contents"]
    for line, nextline in zip(infile, lookahead):
        line = line.strip()
        nextline = nextline.strip()
        parts = line.split()
        if parts[0] == "dir":
            name = parts[1]
            contents[name] = make_folder_obj()
        else:
            size = int(parts[0])
            name = parts[1]
            contents[name] = make_file_obj(size)
        if nextline.startswith("$") or nextline == "":
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Advent of Code 2022, day 7")
    parser.add_argument(
        "infile", type=argparse.FileType("r"), action="store", help="The input file."
    )
    args = parser.parse_args()
    main(args)
