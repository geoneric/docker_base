import time
from fabric.api import *


def manager_basename():
    return "manager"


def worker_basename():
    return "worker"


def hostname(
        basename,
        idx):
    return "{}{}".format(basename, idx)


def is_manager(
        node):
    return node.startswith(manager_basename())


def is_worker(
        node):
    return node.startswith(worker_basename())


def node_index(
        node,
        basename):
    return int(node[len(basename):])


def manager_index(
        node):
    return node_index(node, manager_basename())


def worker_index(
        node):
    return node_index(node, worker_basename())


def swarm_hostnames(
        state=None):

    filters = []
    if state:
        filters.append("state={}".format(state))
    filters = " ".join(["--filter \"{}\"".format(filter) for filter in filters])

    hosts = str(local("docker-machine ls --quiet {}".format(filters),
        capture=True)).strip()

    hosts = hosts.split("\n") if hosts else []

    # Sort hostnames. Put worker nodes in front of manager nodes. When
    # nodes are stopped / removed this is relevant. A manager node must
    # be stopped / removed last.
    worker_nodes = [node for node in hosts if
        node.startswith(worker_basename())]
    manager_nodes = [node for node in hosts if
        node.startswith(manager_basename())]
    # This assumes that the manager with the lowest index is the leader.
    # Everything should work if this isn't the case though.
    manager_nodes.sort()
    hosts = worker_nodes + list(reversed(manager_nodes))

    # def node_kind(
    #         node):
    #     # Sort workers before managers.
    #     if is_worker(node):
    #         return 0
    #     elif is_manager(node):
    #         # Sort managers by index. This assumes that the manager with
    #         # the lowest index is the leader.
    #         assert len(hosts) + 1 >= manager_index(node), "{}, {}, {}".format(
    #             hosts, node, manager_index(node))
    #         return 2 + (len(hosts) - manager_index(node))

    # hosts.sort(key=node_kind)

    # print hosts

    return hosts


def manager_hostname(
        idx):
    return hostname(manager_basename(), idx)


def worker_hostname(
        idx):
    return hostname(worker_basename(), idx)


def manager_hostnames(
        state=None):
    return [hostname for hostname in swarm_hostnames(state) if
        not hostname.startswith(worker_basename())]


def worker_hostnames():
    return [hostname for hostname in swarm_hostnames() if
        not hostname.startswith(manager_basename())]


def new_manager_hostname():
    hostnames = manager_hostnames()
    idx = len(hostnames) + 1

    while manager_hostname(idx) in hostnames:
        idx += 1

    return manager_hostname(idx)


def new_worker_hostname():
    hostnames = worker_hostnames()
    idx = len(hostnames) + 1

    while worker_hostname(idx) in hostnames:
        idx += 1

    return worker_hostname(idx)


def ip_address(
        hostname):
    return str(local("docker-machine ip {}".format(hostname), capture=True))


def assert_no_swarm_exists():

    if swarm_hostnames():
        raise RuntimeError("A Swarm already exists...")


def assert_swarm_exists():

    if not swarm_hostnames():
        raise RuntimeError("No Swarm exists yet...")


def assert_swarm_is_running():

    assert_swarm_exists()

    if not swarm_hostnames(state="Running"):
        raise RuntimeError("Swarm is not running...")


def run_on_node(
        node,
        command):

    with settings(
            host_string=ip_address(node),
            user="docker",
            password="tcuser",
            shell="/bin/sh -c"):
        result = run(command)

    return result


def run_on_manager(
        command):

    # Just pick one of the managers.
    # TODO Detect which one is running and active.
    manager_hostname = manager_hostnames(state="Running")[-1]

    return run_on_node(manager_hostname, command)


def status_of_node(
        node):

    command = "docker node inspect --format='{{{{.Status.State}}}}' {}".format(node)
    status = run_on_manager(command).strip()
    assert status in ["ready", "down"]
    return status


def assert_node_has_status(
        node,
        status):

    if status_of_node(node) != status:
        raise RuntimeError("Node {} is not {}...".format(node, status))


def assert_node_is_ready(
        node):

    assert_node_has_status(node, "ready")


def assert_node_is_down(
        node):

    assert_node_has_status(node, "down")


def node_is_down(
        node):
    return status_of_node(node) == "down"


def create_host(
        hostname):

    options = [
        "--driver virtualbox",
        "--swarm",
        "--swarm-image \"swarm:1.2.5\"",
    ]

    local("docker-machine create {} {}".format(" ".join(options), hostname))


def join_info(
        node_type):

    command = "docker swarm join-token --quiet {}".format(node_type)
    token = run_on_manager(command).strip()
    manager_ip_address = ip_address(manager_hostnames(state="Running")[-1])

    return token, manager_ip_address


def manager_join_info():
    return join_info("manager")


def worker_join_info():
    return join_info("worker")


def add_node_to_swarm(
        hostname,
        join_token,
        manager_ip_address):

    command = "docker swarm join --token {} {}:2377".format(
        join_token, manager_ip_address)
    run_on_node(hostname, command)


def add_manager_to_swarm(
        hostname):

    add_node_to_swarm(hostname, *manager_join_info())


def add_worker_to_swarm(
        hostname):

    add_node_to_swarm(hostname, *worker_join_info())


def join_swarm(
        node):
    if is_manager(node):
        add_manager_to_swarm(node)
    elif is_worker(node):
        add_worker_to_swarm(node)


def leave_swarm(
        node):
    if is_manager(node):
        command = "docker swarm leave --force"
    elif is_worker(node):
        command = "docker swarm leave"

    run_on_node(node, command)


def init_swarm(
        manager_hostname):

    manager_ip_address = ip_address(manager_hostname)
    command = "docker swarm init --advertise-addr {}:2377".format(
        manager_ip_address)
    run_on_node(manager_hostname, command)


def add_manager_nodes(
        nr_nodes):

    assert_swarm_exists()

    nr_nodes = int(nr_nodes)

    for m in range(nr_nodes):
        manager_hostname = new_manager_hostname()
        create_host(manager_hostname)
        add_manager_to_swarm(manager_hostname)


def add_worker_nodes(
        nr_nodes):

    assert_swarm_exists()

    nr_nodes = int(nr_nodes)

    for n in range(nr_nodes):
        worker_hostname = new_worker_hostname()
        create_host(worker_hostname)
        add_worker_to_swarm(worker_hostname)


def create(
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

    assert_no_swarm_exists()

    nr_managers = int(nr_managers)
    assert nr_managers >= 1
    nr_workers = int(nr_workers)


    # Create and configure the first Swarm manager. Initialize the Swarm.
    manager_hostname_ = new_manager_hostname()
    create_host(manager_hostname_)
    init_swarm(manager_hostname_)


    # Add manager and worker nodes. Add them to the Swarm.
    add_manager_nodes(nr_managers - 1)
    add_worker_nodes(nr_workers)


    print("Use this command to connect to the Swarm:\n\n{}\n".format(
        "    eval $(docker-machine env {})".format(manager_hostname_)))


def stop_nodes(
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

    assert_swarm_exists();

    if not nodes:
        nodes = swarm_hostnames(state="Running")

    for node in nodes:
        assert_node_is_ready(node)
        is_last_running_manager = is_manager(node) and \
            len(swarm_hostnames(state="Running")) == 1
        leave_swarm(node)
        local("docker-machine stop {}".format(node))

        if not is_last_running_manager:
            while not node_is_down(node):
                time.sleep(10)

            if is_manager(node):
                command = "docker node demote {}".format(node)
                run_on_manager(command)

            command = "docker node rm {}".format(node)
            run_on_manager(command)


def start_nodes(
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

    assert_swarm_exists();

    if not nodes:
        nodes = swarm_hostnames(state="Stopped")

    for node in nodes:
        assert_node_is_down(node)
        local("docker-machine start {}".format(node))
        join_swarm(node)


def remove_nodes(
        nodes):
    """
    Remove zero or more Swarm nodes

    Each node passed in is removed. In case no nodes are passed in,
    all stopped nodes are removed.

    This function fails
    - if no Swarm exists
    - if one of the nodes passed is not a stopped node in the Swarm
    """

    assert_swarm_exists()

    if not nodes:
        nodes = swarm_hostnames(state="Stopped")

    for node in nodes:
        assert_node_is_down(node)

        local("docker-machine rm -f {}".format(node))


def status_of_swarm():

    assert_swarm_is_running()

    command = "docker node ls"
    run_on_manager(command)

    command = "docker network ls"
    run_on_manager(command)


def create_network(
        name):

    assert_swarm_is_running()

    command = "docker network create --driver overlay {}".format(name)
    run_on_manager(command)


def execute_command(
        command,
        nodes):

    assert_swarm_exists()

    if not nodes:
        nodes = swarm_hostnames(state="Running")

    for node in nodes:
        assert_node_is_ready(node)

        run_on_node(node, command)


def execute_on_nodes(
        nodes,
        command,
        arguments):

    assert_swarm_exists()

    if not nodes:
        nodes = swarm_hostnames(state="Running")

    for node in nodes:
        assert_node_is_ready(node)

        command = "{} {}".format(command, " ".join(arguments))
        run_on_node(node, command)
