#!/usr/bin/env python
import os.path
import sys
import docopt
import docker_base.swarm


doc_string = """\
Manage a Docker Swarm

usage:
    {command} <driver> <host_prefix> <command> [<arguments>...]
    {command} (-h | --help)

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    create      Create new Swarm and start it
    status      Print information about a Swarm that has been started
    start       Start Swarm nodes that have been stopped
    stop        Stop Swarm nodes that have been started, leave Swarm
    pause       Pause running Swarm nodes
    resume      Resume paused Swarm nodes
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

usage:
    create <nr_managers> <nr_workers>
    create (-h | --help)

options:
    -h --help       Show this screen

arguments:
    nr_managers     Number of managers in the Swarm
    nr_workers      Number of workers in the Swarm

If creation of the Swarm fails (This machine has been allocated an IP
address, but Docker Machine could not reach it successfully), this
command may help:

$ sudo ifconfig vboxnet0 down && sudo ifconfig vboxnet0 up
"""


def create_swarm(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(create_doc_string, argv=command_arguments)
    nr_managers = arguments["<nr_managers>"]
    nr_workers = arguments["<nr_workers>"]
    assert int(nr_managers) >= 1, nr_managers
    assert int(nr_workers) >= 0, nr_workers
    results = docker_base.swarm.create(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nr_managers, nr_workers)


start_nodes_doc_string = """\
Start one or more Docker Swarm nodes

usage:
    start [<nodes>...]
    start (-h | --help)

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to start

If no nodes are passed, the whole Swarm is started
"""


def start_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(start_nodes_doc_string, argv=command_arguments)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.start_nodes(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nodes)


status_doc_string = """\
Show status of a Docker Swarm

usage:
    status
    status (-h | --help)

options:
    -h --help       Show this screen
"""


def status_of_swarm(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(status_doc_string, argv=command_arguments)
    results = docker_base.swarm.status_of_swarm(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"])


stop_nodes_doc_string = """\
Stop one or more Docker Swarm nodes

usage:
    stop [<nodes>...]
    stop (-h | --help)

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to stop

If no nodes are passed, the whole Swarm is stopped
"""


def stop_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(stop_nodes_doc_string, argv=command_arguments)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.stop_nodes(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nodes)


pause_nodes_doc_string = """\
Pause one or more Docker Swarm nodes

usage:
    pause [<nodes>...]
    pause (-h | --help)

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to pause

If no nodes are passed, the whole Swarm is paused
"""


def pause_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(pause_nodes_doc_string, argv=command_arguments)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.pause_nodes(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nodes)


resume_nodes_doc_string = """\
Resume one or more paused Docker Swarm nodes

usage:
    resume [<nodes>...]
    resume (-h | --help)

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to resume

If no nodes are passed, the whole Swarm is resumed
"""


def resume_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(resume_nodes_doc_string, argv=command_arguments)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.resume_nodes(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nodes)


add_nodes_doc_string = """\
Add one or more Docker Swarm nodes

usage:
    add (--manager | --worker) <nr_nodes>
    add (-h | --help)

options:
    -h --help       Show this screen
    --manager       Add manager nodes
    --worker        Add worker nodes
"""


def add_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(add_nodes_doc_string, argv=command_arguments)
    manager_node = arguments["--manager"]
    worker_node = arguments["--worker"]
    nr_nodes = arguments["<nr_nodes>"]

    if manager_node:
        results = docker_base.swarm.add_manager_nodes(
            global_arguments["<driver>"],
            global_arguments["<host_prefix>"],
            nr_nodes)
    elif worker_node:
        results = docker_base.swarm.add_worker_nodes(
            global_arguments["<driver>"],
            global_arguments["<host_prefix>"],
            nr_nodes)


remove_nodes_doc_string = """\
Remove one or more Docker Swarm nodes

usage:
    remove [<nodes>...]
    remove (-h | --help)

options:
    -h --help       Show this screen
    <nodes>...      Names of nodes to remove

If no nodes are passed, the whole Swarm is removed
"""


def remove_nodes(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(remove_nodes_doc_string,
        argv=command_arguments)
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.remove_nodes(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        nodes)


create_network_doc_string = """\
Create a new overlay network in the Swarm

usage:
    create <name>
    create (-h | --help)

options:
    -h --help       Show this screen
"""


def create_network(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(create_network_doc_string,
        argv=command_arguments)
    name = arguments["<name>"]
    results = docker_base.swarm.create_network(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        name)


manage_network_doc_string = """\
Manage network configuration one the Docker Swarm

usage:
    network <command> [<arguments>...]
    network (-h | --help)

options:
    -h --help       Show this screen

Commands:
    create      Create new overlay network
"""


def manage_network(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(manage_network_doc_string,
        argv=command_arguments, options_first=True)
    command = arguments.pop("<command>")
    command_arguments = arguments.pop("<arguments>")
    if command_arguments is None:
        command_arguments = {}

    # Otherwise merge with global_arguments.
    assert "--help" in arguments and len(arguments) == 1, arguments

    functions = {
        "create": create_network,
    }
    status = docker_base.call_subcommand(functions[command],
        command_arguments, global_arguments)


execute_command_doc_string = """\
Execute command on one or more Docker Swarm nodes

usage:
    execute <command> [<nodes>...]
    execute (-h | --help)

options:
    -h --help       Show this screen
    <command>       Command to execute
    <nodes>...      Names of nodes to execute command on

If no nodes are passed, the command is executed on all nodes
"""


def execute_command(
        command_arguments,
        global_arguments):
    arguments = docopt.docopt(execute_command_doc_string,
        argv=command_arguments)
    command = arguments["<command>"]
    nodes = arguments["<nodes>"]
    results = docker_base.swarm.execute_command(
        global_arguments["<driver>"],
        global_arguments["<host_prefix>"],
        command, nodes)


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    command = arguments.pop("<command>")
    command_arguments = arguments.pop("<arguments>")
    if command_arguments is None:
        command_arguments = {}
    global_arguments = arguments
    functions = {
        "create": create_swarm,
        "start": start_nodes,
        "status": status_of_swarm,
        "stop": stop_nodes,
        "pause": pause_nodes,
        "resume": resume_nodes,
        "add": add_nodes,
        "remove": remove_nodes,
        "network": manage_network,
        "execute": execute_command
    }
    status = docker_base.call_subcommand(functions[command],
        command_arguments, global_arguments)

    sys.exit(status)
