from fabric.tasks import execute
from . import service_fabfile as fabfile


def create(
        nr_instances,
        name,
        image,
        command,
        arguments,
        network="",
        publish=""):

    return execute(fabfile.create, nr_instances=nr_instances,
        name=name, image=image, command=command, arguments=arguments,
        network=network, publish=publish)


def remove(
        names):

    return execute(fabfile.remove, names=names)


def status():

    return execute(fabfile.status)
