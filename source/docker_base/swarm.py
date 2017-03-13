from fabric.tasks import execute
from . import swarm_fabfile as fabfile


def create(
        driver,
        host_prefix,
        nr_managers,
        nr_workers):

    return execute(fabfile.create,
        driver=driver, host_prefix=host_prefix,
        nr_managers=nr_managers, nr_workers=nr_workers)


def start_nodes(
        driver,
        host_prefix,
        nodes):
    return execute(fabfile.start_nodes,
        driver=driver, host_prefix=host_prefix,
        nodes=nodes)


def stop_nodes(
        driver,
        host_prefix,
        nodes):
    return execute(fabfile.stop_nodes,
        driver=driver, host_prefix=host_prefix,
        nodes=nodes)


def remove_nodes(
        driver,
        host_prefix,
        nodes):
    return execute(fabfile.remove_nodes,
        driver=driver, host_prefix=host_prefix,
        nodes=nodes)


def add_manager_nodes(
        driver,
        host_prefix,
        nr_nodes):
    return execute(fabfile.add_manager_nodes,
        driver=driver, host_prefix=host_prefix,
        nr_nodes=nr_nodes)


def add_worker_nodes(
        driver,
        host_prefix,
        nr_nodes):
    return execute(fabfile.add_worker_nodes,
        driver=driver, host_prefix=host_prefix,
        nr_nodes=nr_nodes)


def status(
        driver,
        host_prefix):
    return execute(fabfile.status_of_swarm,
        driver=driver, host_prefix=host_prefix)


def create_network(
        driver,
        host_prefix,
        name):
    return execute(fabfile.create_network,
        driver=driver, host_prefix=host_prefix,
        name=name)


def execute_command(
        driver,
        host_prefix,
        command,
        nodes):
    return execute(fabfile.execute_command,
        driver=driver, host_prefix=host_prefix,
        command=command, nodes=nodes)


def execute_on_nodes(
        driver,
        host_prefix,
        nodes,
        command,
        arguments):
    return execute(fabfile.execute_on_nodes,
        driver=driver, host_prefix=host_prefix,
        nodes=nodes, command=command, arguments=arguments)
