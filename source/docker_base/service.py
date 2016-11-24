from fabric.tasks import execute
from . import service_fabfile as fabfile


def create(
        name,
        image,
        command,
        arguments,
        environments=[],
        mode="",
        mounts=[],
        network="",
        publish="",
        replicas=""):

    return execute(fabfile.create, replicas=replicas,
        name=name, image=image, command=command, arguments=arguments,
        environments=environments, mode=mode, mounts=mounts, network=network,
        publish=publish)


def remove(
        names):

    return execute(fabfile.remove, names=names)


def status():

    return execute(fabfile.status)
