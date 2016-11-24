#!/usr/bin/env python
import os.path
import sys
import docopt
import docker_base.service


doc_string = """\
Manage Docker services

usage: {command} [--help] <command> [<arguments>...]

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    create      Create a new service
    remove      Remove one or more created services
    status      Print information about services that have been created

See '{command} help <command>' for more information on a specific
command.
""".format(
        command = os.path.basename(sys.argv[0]))


create_doc_string = """\
Create a Docker service

usage: {command} create
    [--env=<setting>...]
    [--mode=<setting>]
    [--mount=<setting>...]
    [--network=<network_name>]
    [--publish=<port_map>]
    [--replicas=<setting>]
    <name> <image> [-- <command> [<argument>...]]

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def create_service(
        argv):
    arguments = docopt.docopt(create_doc_string, argv=argv)
    replicas = arguments["--replicas"] if "--replicas" in arguments else \
        None
    network_name = arguments["--network"] if "--network" \
        in arguments else None
    port_map = arguments["--publish"] if "--publish" \
        in arguments else None
    environments = arguments["--env"]
    mode = arguments["--mode"] if "--mode" in arguments else None
    mounts = arguments["--mount"]
    name = arguments["<name>"]
    image = arguments["<image>"]
    command = arguments["<command>"] if arguments["<command>"] is not None \
        else ""
    arguments_ = arguments["<argument>"]

    results = docker_base.service.create(name, image,
        command, arguments_, network=network_name, environments=environments,
        mode=mode, mounts=mounts, publish=port_map, replicas=replicas)

    print(results)


remove_service_doc_string = """\
Remove one or more created Docker services

usage: {command} remove <name>...

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def remove_service(
        argv):
    arguments = docopt.docopt(remove_service_doc_string, argv=argv)
    names = arguments["<name>"]
    results = docker_base.service.remove(names)

    print(results)


status_doc_string = """\
Status of a Docker services

usage: {command} status

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def status_of_services(
        argv):
    arguments = docopt.docopt(status_doc_string, argv=argv)
    results = docker_base.service.status()

    print(results)


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    command = arguments["<command>"]
    argv = [command] + arguments["<arguments>"]
    functions = {
        "create": create_service,
        "remove": remove_service,
        "status": status_of_services,
    }
    status = docker_base.call_subcommand(functions[command], argv)

    sys.exit(status)
