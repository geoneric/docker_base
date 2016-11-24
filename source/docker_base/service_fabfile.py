from fabric.api import *
from . import swarm_fabfile as fabfile


def create(
        name,
        image,
        command,
        arguments,
        environments,
        mode,
        mounts,
        network,
        publish,
        replicas):

    fabfile.assert_swarm_is_running()

    environments = " ".join(["--env {}".format(environment) for environment in
        environments])
    mode = "--mode {}".format(mode) if mode else ""
    mounts = " ".join(["--mount {}".format(mount) for mount in mounts])
    network = "--network {}".format(network) if network else ""
    publish = "--publish {}".format(publish) if publish else ""
    replicas = "--replicas {}".format(replicas) if replicas else ""
    command_ = "docker service create --name " \
        "{} {} {} {} {} {} {} {} {} {}".format(
            name, environments, mode, mounts, network,
            publish, replicas, image, command, " ".join(arguments))
    fabfile.run_on_manager(command_)


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
