#!/usr/bin/env python
import os.path
import sys
import docopt
import docker_base.swarm


doc_string = """\
Manage Docker services

usage:
    {command} <driver> <host_prefix> <command> [<arguments>...]
    {command} (-h | --help)

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    remove      Remove one or more created services
    status      Print information about services that have been created

See '{command} help <command>' for more information on a specific
command.
""".format(
        command = os.path.basename(sys.argv[0]))


remove_service_doc_string = """\
Remove one or more created Docker services

usage: {command} remove <name>...

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def remove_services(
        argv):
    arguments = docopt.docopt(remove_service_doc_string, argv=argv)
    names = arguments["<name>"]
    results = docker_base.swarm.remove_services(names)

    print(results)


status_doc_string = """\
Show status of Docker services

usage:
    status [<services>...]
    status (-h | --help)

options:
    -h --help       Show this screen
    <services>...   Names of services to inspect

If no services are passed, all services are inspected
"""


def status_of_services(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(status_doc_string, argv=command_arguments)
    services = arguments["<services>"]
    results = docker_base.swarm.status_of_services(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        services)

    print(results)


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    command = arguments.pop("<command>")
    command_arguments = arguments.pop("<arguments>")
    if command_arguments is None:
        command_arguments = {}
    global_arguments = arguments
    functions = {
        "status": status_of_services,
        "remove": remove_services,
    }
    status = docker_base.call_subcommand(functions[command],
        command_arguments, global_arguments)
