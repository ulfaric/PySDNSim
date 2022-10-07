# PySDNSim
This is a simulation tool for microservice based SDN. It uses a executable jar built upon CloudSim Plus (https://cloudsimplus.org/) as the backend.

## Example

    import random
    from copy import deepcopy
    from typing import List

    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    from dash import Dash, Input, Output, dcc, html
    from PySDNSim.Backend import Backend
    from PySDNSim.Config import Config
    from PySDNSim.Experiment import Experiment
    from PySDNSim.Host import Host
    from PySDNSim.Job import Job
    from PySDNSim.Microservice import Microservice
    from PySDNSim.NetworkService import NetworkService, create_network_service
    from treelib import Node, Tree
    
create simulation config

    sim_config = Config(seed=1024, interval=1.0, step_size=0.01)

create host

    host = Host(
        cpus=64,
        ram=102400,
        bw=100000,
        storage=1024000,
        max_power=1600.0,
        static_power=300.0,
        replicas=3,
    )
    
create microservices

    microservices: List[Microservice] = list()
    ms_mqtt_broker = Microservice(
        name="mqtt_broker",
        size=512,
        cpus=2,
        ram=1024,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=25,
        ram_ratio=32,
        bw_ratio=25,
    )
    microservices.append(ms_mqtt_broker)
    ms_chirpstack_gateway = Microservice(
        name="chirpstack_gateway",
        size=128,
        cpus=2,
        ram=1024,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=25,
        ram_ratio=32,
        bw_ratio=25,
    )
    microservices.append(ms_chirpstack_gateway)
    ms_chirpstack = Microservice(
        name="chirpstack",
        size=128,
        cpus=4,
        ram=2048,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=10,
        ram_ratio=32,
        bw_ratio=25,
    )
    microservices.append(ms_chirpstack)
    ms_chirpstack_rest_api = Microservice(
        name="chirpstack_rest_api",
        size=128,
        cpus=2,
        ram=1024,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=5,
        ram_ratio=128,
        bw_ratio=25,
    )
    microservices.append(ms_chirpstack_rest_api)
    ms_postgresql = Microservice(
        name="postgresql",
        size=2048,
        cpus=2,
        ram=1024,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=50,
        ram_ratio=128,
        bw_ratio=100,
    )
    microservices.append(ms_postgresql)
    ms_redis = Microservice(
        name="redis",
        size=2048,
        cpus=2,
        ram=1024,
        bw=1000,
        replicas=1,
        max_replicas=1,
        cpu_ratio=50,
        ram_ratio=128,
        bw_ratio=100,
    )
    microservices.append(ms_redis)
    
create network services

    ns_list = list()
    register_device = create_network_service(
        name="register_device",
        microservices=[2, 5, 1],
        schdeule=[0, 1, 1],
        schedule_length=[10, 10, 10],
    )
    ns_list.append(register_device)
    read_data = create_network_service(
        name="receive_data",
        microservices=[1, 0, 2, 4],
        schdeule=[0, 1, 2, 3],
        schedule_length=[10, 10, 10, 10],
    )
    ns_list.append(read_data)
    retrive_data = create_network_service(
        name="retrive_data",
        microservices=[3, 2, 4, 2],
        schdeule=[0, 1, 2, 3],
        schedule_length=[10, 10, 10, 10],
    )
    ns_list.append(retrive_data)
    
start a simulation that randomly select network services at each iteration.

    backend.start()
    for iter in range(10):
        num_ns = random.randint(1, 20)
        chosen_ns: List[NetworkService] = deepcopy(random.choices(ns_list, k=num_ns))
        for ns in chosen_ns:
            ns.offset_schedule(random.randint(0, 5))
        experiment = Experiment(
            name=f"{iter}",
            config=sim_config,
            host=host,
            microservices=microservices,
            network_services=chosen_ns,
        )
        backend.add_experiment(experiment=experiment, output_path="./results")
    backend.stop()
