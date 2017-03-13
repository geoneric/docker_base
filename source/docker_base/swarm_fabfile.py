import os
import time
from fabric.api import *


class Swarm(object):


    def __init__(self,
            driver,
            host_prefix):
        self.driver = driver
        self.host_prefix = host_prefix


    def host_basename(self,
            name):
        # Allowed hostname chars are: 0-9a-zA-Z . -
        return name if len(self.host_prefix) == 0 else "{}-{}".format(
            self.host_prefix, name)


    def manager_basename(self):
        return self.host_basename("manager")


    def worker_basename(self):
        return self.host_basename("worker")


    def hostname(self,
            basename,
            idx):
        return "{}{}".format(basename, idx)


    def is_manager(self,
            node):
        return node.startswith(self.manager_basename())


    def is_worker(self,
            node):
        return node.startswith(self.worker_basename())


    def swarm_hostnames(self,
            state=None):

        filters = []
        if state:
            filters.append("state={}".format(state))
        filters = " ".join(["--filter \"{}\"".format(filter) for filter in
            filters])

        hosts = str(local("docker-machine ls --quiet {}".format(filters),
            capture=True)).strip()

        hosts = hosts.split("\n") if hosts else []

        # Sort hostnames. Put worker nodes in front of manager nodes. When
        # nodes are stopped / removed this is relevant. A manager node must
        # be stopped / removed last.
        worker_nodes = [node for node in hosts if
            node.startswith(self.worker_basename())]
        manager_nodes = [node for node in hosts if
            node.startswith(self.manager_basename())]
        # This assumes that the manager with the lowest index is the leader.
        # Everything should work if this isn't the case though.
        manager_nodes.sort()
        hosts = worker_nodes + list(reversed(manager_nodes))

        return hosts


    def manager_hostname(self,
            idx):
        return self.hostname(self.manager_basename(), idx)


    def worker_hostname(self,
            idx):
        return self.hostname(self.worker_basename(), idx)


    def manager_hostnames(self,
            state=None):
        return [hostname for hostname in self.swarm_hostnames(state) if
            not hostname.startswith(self.worker_basename())]


    def worker_hostnames(self,
            state=None):
        return [hostname for hostname in self.swarm_hostnames(state) if
            not hostname.startswith(self.manager_basename())]


    def new_manager_hostname(self):
        hostnames = self.manager_hostnames()
        idx = len(hostnames) + 1

        while self.manager_hostname(idx) in hostnames:
            idx += 1

        return self.manager_hostname(idx)


    def new_worker_hostname(self):
        hostnames = self.worker_hostnames()
        idx = len(hostnames) + 1

        while self.worker_hostname(idx) in hostnames:
            idx += 1

        return self.worker_hostname(idx)


    def status_of_node(self,
            node):
        """
        This function assumes a manager node is running
        """

        command = "sudo docker node inspect " \
            "--format='{{{{.Status.State}}}}' {}".format(node)
        status = self.run_on_manager(command).strip()
        assert status in ["ready", "down"], status
        return status


    def assert_no_swarm_exists(self):

        if self.swarm_hostnames():
            raise RuntimeError("A Swarm already exists...")


    def assert_swarm_exists(self):

        if not self.swarm_hostnames():
            raise RuntimeError("No Swarm exists yet...")


    def assert_swarm_is_running(self):

        self.assert_swarm_exists()

        if not self.swarm_hostnames(state="Running"):
            raise RuntimeError("Swarm is not running...")


    def create_host(self,
            hostname):

        options = [
            "--driver {}".format(self.driver),
            "--swarm",
            "--swarm-image \"swarm:1.2.6\"",
        ]

        if self.driver != "virtualbox":
            # Assume rsyslog is installed.
            options.append(
                "--engine-opt log-driver=syslog",
            )

        local("docker-machine create {} {}".format(" ".join(options),
            hostname))


    def ip_address(self,
            hostname):
        return str(local("docker-machine ip {}".format(hostname),
            capture=True))


    def run_on_node(self,
            node,
            command):

        # if self.driver == "virtualbox":
        #     with settings(
        #             host_string=self.ip_address(node),
        #             user="docker",
        #             password="tcuser",
        #             shell="/bin/sh -c"):
        #         result = run(command)
        # elif self.driver == "amazonec2":
        #     with settings(
        #             host_string=self.ip_address(node),
        #             # TODO Actually, this depends on the AMI, not the driver.
        #             user="ubuntu",
        #             key_filename=[
        #                 os.path.join(os.environ["HOME"],
        #                     ".docker/machine/machines/{}/id_rsa".format(node))
        #             ],
        #             shell="/bin/sh -c"):
        #         result = run(command)
        # else:
        #     assert False, self.driver

        command = "docker-machine ssh {} {}".format(node, command)
        result = local(command, capture=True)

        return result


    def run_on_manager(self,
            command):
        """
        This function assumes a manager node is running
        """

        # Just pick one of the managers.
        # TODO Detect which one is running and active.
        manager_hostname = self.manager_hostnames(state="Running")[-1]

        return self.run_on_node(manager_hostname, command)


    def init_swarm(self,
            manager_hostname):

        manager_ip_address = self.ip_address(manager_hostname)
        command = "sudo docker swarm init --advertise-addr {}:2377".format(
            manager_ip_address)
        self.run_on_node(manager_hostname, command)


    def join_info(self,
            node_type):

        command = "sudo docker swarm join-token --quiet {}".format(node_type)
        token = self.run_on_manager(command).strip()
        manager_ip_address = self.ip_address(self.manager_hostnames(
            state="Running")[-1])

        return token, manager_ip_address


    def manager_join_info(self):
        return self.join_info("manager")


    def worker_join_info(self):
        return self.join_info("worker")


    def add_node_to_swarm(self,
            hostname,
            join_token,
            manager_ip_address):

        command = "sudo docker swarm join --token {} {}:2377".format(
            join_token, manager_ip_address)
        self.run_on_node(hostname, command)


    def add_manager_to_swarm(self,
            hostname):

        self.add_node_to_swarm(hostname, *self.manager_join_info())


    def add_worker_to_swarm(self,
            hostname):

        self.add_node_to_swarm(hostname, *self.worker_join_info())


    def add_manager_nodes(self,
            nr_nodes):

        self.assert_swarm_exists()

        nr_nodes = int(nr_nodes)

        for m in range(nr_nodes):
            manager_hostname = self.new_manager_hostname()
            self.create_host(manager_hostname)
            self.add_manager_to_swarm(manager_hostname)


    def add_worker_nodes(self,
            nr_nodes):

        self.assert_swarm_exists()

        nr_nodes = int(nr_nodes)

        for n in range(nr_nodes):
            worker_hostname = self.new_worker_hostname()
            self.create_host(worker_hostname)
            self.add_worker_to_swarm(worker_hostname)


    def assert_node_has_status(self,
            node,
            status):
        """
        This function assumes a manager node is running
        """

        if self.status_of_node(node) != status:
            raise RuntimeError("Node {} is not {}...".format(node, status))


    def assert_node_is_ready(self,
            node):
        """
        This function assumes a manager node is running
        """

        self.assert_node_has_status(node, "ready")


    def assert_node_is_down(self,
            node):
        """
        This function assumes a manager node is running
        """

        self.assert_node_has_status(node, "down")


    def assert_node_is_stopped(self,
            node):
        if not node in self.swarm_hostnames(state="Stopped"):
            raise RuntimeError("Node {} must be stopped first...")


    def node_is_down(self,
            node):
        """
        This function assumes a manager node is running
        """

        return self.status_of_node(node) == "down"


    def join_swarm(self,
            node):
        if self.is_manager(node):
            self.add_manager_to_swarm(node)
        elif self.is_worker(node):
            self.add_worker_to_swarm(node)


    def leave_swarm(self,
            node):
        if self.is_manager(node):
            command = "sudo docker swarm leave --force"
        elif self.is_worker(node):
            command = "sudo docker swarm leave"

        self.run_on_node(node, command)


    def create(self,
            nr_managers,
            nr_workers):
        """
        Create a Swarm with one or more manager nodes and zero or more
        worker nodes

        First a manager node is created which is used to initialize the
        Swarm. After that, the other manager nodes are created and added to
        the Swarm. Then the worker nodes are created and added to the Swarm.

        This function fails if a Swarm already exists.
        """

        self.assert_no_swarm_exists()

        nr_managers = int(nr_managers)
        assert nr_managers >= 1
        nr_workers = int(nr_workers)


        # Create and configure the first Swarm manager. Initialize the Swarm.
        manager_hostname_ = self.new_manager_hostname()
        self.create_host(manager_hostname_)
        self.init_swarm(manager_hostname_)


        # Add manager and worker nodes. Add them to the Swarm.
        self.add_manager_nodes(nr_managers - 1)
        self.add_worker_nodes(nr_workers)


        print("Use this command to connect to the Swarm:\n\n{}\n".format(
            "    eval $(docker-machine env {})".format(manager_hostname_)))


    def status(self):
        self.assert_swarm_is_running()

        command = "sudo docker node ls"
        self.run_on_manager(command)

        command = "sudo docker network ls"
        self.run_on_manager(command)


    def stop(self,
            nodes):

        self.assert_swarm_exists()

        if not nodes:
            nodes = self.swarm_hostnames(state="Running")
        else:
            nodes = [self.host_basename(node) for node in nodes]

        for node in nodes:
            self.assert_node_is_ready(node)
            is_last_running_manager = self.is_manager(node) and \
                len(self.swarm_hostnames(state="Running")) == 1
            self.leave_swarm(node)
            local("docker-machine stop {}".format(node))

            if not is_last_running_manager:
                while not self.node_is_down(node):
                    time.sleep(10)

                if self.is_manager(node):
                    command = "sudo docker node demote {}".format(node)
                    self.run_on_manager(command)

                command = "sudo docker node rm {}".format(node)
                self.run_on_manager(command)


    def start(self,
            nodes):

        self.assert_swarm_exists()

        if not nodes:
            nodes = self.swarm_hostnames(state="Stopped")
        else:
            nodes = [self.host_basename(node) for node in nodes]

        for node in nodes:
            self.assert_node_is_down(node)
            local("docker-machine start {}".format(node))
            self.join_swarm(node)


    def remove(self,
            nodes):

        self.assert_swarm_exists()

        if not nodes:
            nodes = self.swarm_hostnames(state="Stopped")
        else:
            nodes = [self.host_basename(node) for node in nodes]

        for node in nodes:
            self.assert_node_is_stopped(node)

            local("docker-machine rm -f {}".format(node))


    def create_network(self,
            name):

        self.assert_swarm_is_running()

        command = "sudo docker network create --driver overlay {}".format(
            name)
        self.run_on_manager(command)


    def execute_command(self,
            command,
            nodes):

        self.assert_swarm_exists()

        if not nodes:
            nodes = self.swarm_hostnames(state="Running")
        else:
            nodes = [self.host_basename(node) for node in nodes]

        for node in nodes:
            self.assert_node_is_ready(node)

            self.run_on_node(node, command)


    def execute_on_nodes(self,
            nodes,
            command,
            arguments):

        self.assert_swarm_exists()

        if not nodes:
            nodes = swarm_hostnames(state="Running")
        else:
            nodes = [self.host_basename(node) for node in nodes]

        for node in nodes:
            self.assert_node_is_ready(node)

            command = "{} {}".format(command, " ".join(arguments))
            self.run_on_node(node, command)


def create(
        driver,
        host_prefix,
        nr_managers,
        nr_workers):
    """
    Create a Swarm with one or more manager nodes and zero or more
    worker nodes

    First a manager node is created which is used to initialize the
    Swarm. After that, the other manager nodes are created and added to
    the Swarm. Then the worker nodes are created and added to the Swarm.

    This function fails if a Swarm already exists.
    """
    swarm = Swarm(driver, host_prefix)
    swarm.create(nr_managers, nr_workers)


def status_of_swarm(
        driver,
        host_prefix):

    swarm = Swarm(driver, host_prefix)
    swarm.status()


def stop_nodes(
        driver,
        host_prefix,
        nodes):
    """
    Stop zero or more Swarm nodes

    Each node passed in is stopped. In case no nodes are passed in,
    all running nodes are stopped. Before a node is stopped, it leaves
    the Swarm.

    This function fails
    - if no Swarm exists
    - if one of the nodes passed is not a started node in the Swarm
    """
    swarm = Swarm(driver, host_prefix)
    swarm.stop(nodes)


def remove_nodes(
        driver,
        host_prefix,
        nodes):
    """
    Remove zero or more Swarm nodes

    Each node passed in is removed. In case no nodes are passed in,
    all stopped nodes are removed.

    This function fails
    - if no Swarm exists
    - if one of the nodes passed is not a stopped node in the Swarm
    """
    swarm = Swarm(driver, host_prefix)
    swarm.remove(nodes)


def start_nodes(
        driver,
        host_prefix,
        nodes):
    """
    Start zero or more Swarm nodes

    Each node passed in is started. In case no nodes are passed in,
    all stopped nodes are started. After a node has started, it joins
    the Swarm.

    This function fails
    - if no Swarm exists
    - if one of the nodes passed is not a stopped node in the Swarm
    """
    swarm = Swarm(driver, host_prefix)
    swarm.start(nodes)


def add_manager_nodes(
        driver,
        host_prefix,
        nr_nodes):

    swarm = Swarm(driver, host_prefix)
    swarm.add_manager_nodes(nr_nodes)


def add_worker_nodes(
        driver,
        host_prefix,
        nr_nodes):

    swarm = Swarm(driver, host_prefix)
    swarm.add_worker_nodes(nr_nodes)


def create_network(
        driver,
        host_prefix,
        name):

    swarm = Swarm(driver, host_prefix)
    swarm.create_network(name)


def execute_command(
        driver,
        host_prefix,
        command,
        nodes):
    swarm = Swarm(driver, host_prefix)
    swarm.execute_command(command, nodes)


def execute_on_nodes(
        driver,
        host_prefix,
        nodes,
        command,
        arguments):
    swarm = Swarm(driver, host_prefix)
    swarm.execute_on_nodes(nodes, command, arguments)
