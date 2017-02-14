#!/usr/bin/env python
import os.path
import sys
import docopt
import docker_base.swarm


doc_string = """\
Execute command on Docker Swarm nodes

usage:
    {command} <nodes> <command> [<arguments>...]
    {command} [--help]

options:
    -h --help   Show this screen
    --version   Show version
""".format(
        command = os.path.basename(sys.argv[0]))


def execute_on_nodes(
        nodes,
        command,
        arguments):

    results = docker_base.swarm.execute_on_nodes(nodes, command, arguments)

    print(results)


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    nodes = arguments["<nodes>"].split(",")
    command = arguments["<command>"]
    arguments_ = arguments["<arguments>"]

    status = docker_base.call_subcommand(execute_on_nodes, nodes, command,
        arguments_)

    sys.exit(status)