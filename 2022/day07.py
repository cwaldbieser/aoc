#! /usr/bin/env python

import argparse
import itertools


def main(args):
    """
    The main function entrypoint.
    """
    filesystem = parse_filesystem(args.infile)
    print(filesystem)


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
    import pprint
    pprint.pprint(fsinfo)


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
        print("line", line)
        print("nextline", nextline)
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
