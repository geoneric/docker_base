from fabric.tasks import execute
from . import swarm_fabfile as fabfile


def create(
        nr_managers,
        nr_workers):

    return execute(fabfile.create, nr_managers=nr_managers,
        nr_workers=nr_workers)


def start_nodes(
        nodes):
    return execute(fabfile.start_nodes, nodes=nodes)


def stop_nodes(
        nodes):
    return execute(fabfile.stop_nodes, nodes=nodes)


def remove_nodes(
        nodes):
    return execute(fabfile.remove_nodes, nodes=nodes)


def add_manager_nodes(
        nr_nodes):
    return execute(fabfile.add_manager_nodes, nr_nodes=nr_nodes)


def add_worker_nodes(
        nr_nodes):
    return execute(fabfile.add_worker_nodes, nr_nodes=nr_nodes)


def status():
    return execute(fabfile.status_of_swarm)


def create_network(
        name):
    return execute(fabfile.create_network, name=name)


def execute_command(
        command,
        nodes):
    return execute(fabfile.execute_command, command=command, nodes=nodes)
