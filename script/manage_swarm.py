#!/usr/bin/env python
import os.path
import sys
import docopt
import docker_base.swarm


doc_string = """\
Manage a Docker Swarm

usage: {command} [--help] <command> [<arguments>...]

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    create      Create new Swarm and start it
    status      Print information about a Swarm that has been started
    start       Start Swarm nodes that have been stopped
    stop        Stop Swarm nodes that have been started
    add         Add new Swarm nodes
    remove      Remove Swarm nodes that are running or have been stopped
    network     Manage Swarm networks
    execute     Execture a command on nodes

See '{command} help <command>' for more information on a specific
command.

Once a Swarm is started, use the folowing command to direct your Docker
client to it (replace manager by the hostname of a Swarm manager):
    $ eval $(docker-machine env <manager>)
""".format(
        command = os.path.basename(sys.argv[0]))


create_doc_string = """\
Create a Docker Swarm

usage: {command} create <nr_managers> <nr_workers>

options:
    -h --help       Show this screen

arguments:
    nr_managers     Number of managers in the Swarm
    nr_workers      Number of workers in the Swarm

If creation of the Swarm fails (This machine has been allocated an IP
address, but Docker Machine could not reach it successfully), this
command may help:

$ sudo ifconfig vboxnet0 down && sudo ifconfig vboxnet0 up
""".format(
        command = os.path.basename(sys.argv[0]))


def create_swarm(
        argv):
    arguments = docopt.docopt(create_doc_string, argv=argv)
    nr_managers = arguments["<nr_managers>"]
    nr_workers = arguments["<nr_workers>"]
    assert int(nr_managers) >= 1, nr_managers
    assert int(nr_workers) >= 0, nr_workers
    results = docker_base.swarm.create(nr_managers, nr_workers)

    print(results)


start_nodes_doc_string = """\
Start one or more Docker Swarm nodes

usage: {command} start [<nodes>...]

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to start

If no nodes are passed, the whole Swarm is started
""".format(
        command = os.path.basename(sys.argv[0]))


def start_nodes(
        argv):
    arguments = docopt.docopt(start_nodes_doc_string, argv=argv)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.start_nodes(nodes)

    print(results)


status_doc_string = """\
Status of a Docker Swarm

usage: {command} status

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def status_of_swarm(
        argv):
    arguments = docopt.docopt(status_doc_string, argv=argv)
    results = docker_base.swarm.status()

    print(results)


stop_nodes_doc_string = """\
Stop one or more Docker Swarm nodes

usage: {command} stop [<nodes>...]

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to stop

If no nodes are passed, the whole Swarm is stopped
""".format(
        command = os.path.basename(sys.argv[0]))


def stop_nodes(
        argv):
    arguments = docopt.docopt(stop_nodes_doc_string, argv=argv)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.stop_nodes(nodes)

    print(results)


add_nodes_doc_string = """\
Add one or more Docker Swarm nodes

usage: {command} add (--manager | --worker) <nr_nodes>

options:
    -h --help       Show this screen
    --manager       Add manager nodes
    --worker        Add worker nodes
""".format(
        command = os.path.basename(sys.argv[0]))


def add_nodes(
        argv):
    arguments = docopt.docopt(add_nodes_doc_string, argv=argv)
    manager_node = arguments["--manager"]
    worker_node = arguments["--worker"]
    nr_nodes = arguments["<nr_nodes>"]

    if manager_node:
        results = docker_base.swarm.add_manager_nodes(nr_nodes)
    elif worker_node:
        results = docker_base.swarm.add_worker_nodes(nr_nodes)

    print(results)


remove_nodes_doc_string = """\
Remove one or more Docker Swarm nodes

usage: {command} remove [<nodes>...]

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to remove

If no nodes are passed, the whole Swarm is removed
""".format(
        command = os.path.basename(sys.argv[0]))


def remove_nodes(
        argv):
    arguments = docopt.docopt(remove_nodes_doc_string, argv=argv)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.remove_nodes(nodes)

    print(results)


create_network_doc_string = """\
Create a new overlay network in the Swarm

usage: {command} network create <name>

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def create_network(
        argv):
    arguments = docopt.docopt(create_network_doc_string, argv=argv)
    name = arguments["<name>"]
    results = docker_base.swarm.create_network(name)

    print(results)


manage_network_doc_string = """\
Manage network configuration one the Docker Swarm

usage: {command} network <command> [<arguments>...]

options:
    -h --help       Show this screen

Commands:
    create      Create new overlay network
""".format(
        command = os.path.basename(sys.argv[0]))


def manage_network(
        argv):
    arguments = docopt.docopt(manage_network_doc_string, argv=argv,
        options_first=True)
    command = arguments["<command>"]
    argv = [argv[0]] + [command] + arguments["<arguments>"]
    functions = {
        "create": create_network,
    }
    status = docker_base.call_subcommand(functions[command], argv)


execute_command_doc_string = """\
Execute command on one or more Docker Swarm nodes

usage: {command} execute <command> [<nodes>...]

options:
    -h --help       Show this screen
    <command>       Command to execute
    <nodes>...      Names of nodes to execute command on

If no nodes are passed, the command is executed on all nodes
""".format(
        command = os.path.basename(sys.argv[0]))


def execute_command(
        argv):
    arguments = docopt.docopt(execute_command_doc_string, argv=argv)
    command = arguments["<command>"]
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.execute_command(command, nodes)

    print(results)


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    command = arguments["<command>"]
    argv = [command] + arguments["<arguments>"]
    functions = {
        "create": create_swarm,
        "start": start_nodes,
        "status": status_of_swarm,
        "stop": stop_nodes,
        "add": add_nodes,
        "remove": remove_nodes,
        "network": manage_network,
        "execute": execute_command
    }
    status = docker_base.call_subcommand(functions[command], argv)

    sys.exit(status)
