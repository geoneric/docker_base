from fabric.api import *
from . import swarm_fabfile as fabfile


def create(
        nr_instances,
        name,
        image,
        command,
        arguments,
        network,
        publish):

    fabfile.assert_swarm_is_running()

    network = "--network {}".format(network) if network else ""
    publish = "--publish {}".format(publish) if publish else ""
    command = \
        "docker service create --replicas {} --name {} {} {} {} {} {}".format(
            nr_instances, name, network, publish, image, command,
            " ".join(arguments))
    fabfile.run_on_manager(command)


def remove(
        names):

    fabfile.assert_swarm_is_running()

    for name in names:
        command = "docker service rm {}".format(name)
        fabfile.run_on_manager(command)


def service_names():
    command = "docker service ls"

    # Example output:
    #
    # ID            NAME     REPLICAS  IMAGE   COMMAND
    # cmxx7hguy4j6  pinger   2/2       alpine  ping docker.com
    # dhh7v9efigqo  pinger2  2/2       alpine  ping docker.com

    lines = str(fabfile.run_on_manager(command)).split("\n")[1:]
    lines = [line.strip() for line in lines]
    names = [line.split()[1] for line in lines]
    return names


def status():

    fabfile.assert_swarm_is_running()

    command = "docker service ls"
    fabfile.run_on_manager(command)

    services = service_names()

    for service in services:
        command = "docker service ps {}".format(service)
        fabfile.run_on_manager(command)
