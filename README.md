# PySDNSim
This is a simulation tool for microservice based SDN. It uses a executable jar built upon CloudSim Plus (https://cloudsimplus.org/) as the backend, specifically "org.cloudsimplus:cloudsim-plus:7.3.0"

The backend jar is available from https://drive.google.com/file/d/1PWtYCWDBRV02VcOD1kn_J-lLbsxyfXhT/view?usp=sharing.

The backend.jar must be put into the same directory as your program.

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
        replicas=1,
        max_replicas=3,
        cpu_ratio=25,
        ram_ratio=32,
        bw_ratio=25,
    )
    ms_mqtt_broker.add_auto_scale("cpu",0.5)
    ms_mqtt_broker.add_auto_scale("ram",0.5)
    ms_mqtt_broker.add_auto_scale("bw",0.5)
    microservices.append(ms_mqtt_broker)
    ms_chirpstack_gateway = Microservice(
        name="chirpstack_gateway",
        size=128,
        cpus=2,
        replicas=1,
        max_replicas=3,
        cpu_ratio=25,
        ram_ratio=32,
        bw_ratio=25,
    )
    ms_chirpstack_gateway.add_auto_scale("cpu",0.5)
    ms_chirpstack_gateway.add_auto_scale("ram",0.5)
    ms_chirpstack_gateway.add_auto_scale("bw",0.5)
    microservices.append(ms_chirpstack_gateway)
    ms_chirpstack = Microservice(
        name="chirpstack",
        size=128,
        cpus=4,
        replicas=1,
        max_replicas=3,
        cpu_ratio=10,
        ram_ratio=32,
        bw_ratio=25,
    )
    ms_chirpstack.add_auto_scale("cpu",0.5)
    ms_chirpstack.add_auto_scale("ram",0.5)
    ms_chirpstack.add_auto_scale("bw",0.5)
    microservices.append(ms_chirpstack)
    ms_chirpstack_rest_api = Microservice(
        name="chirpstack_rest_api",
        size=128,
        cpus=2,
        replicas=1,
        max_replicas=3,
        cpu_ratio=5,
        ram_ratio=128,
        bw_ratio=25,
    )
    ms_chirpstack_rest_api.add_auto_scale("cpu",0.5)
    ms_chirpstack_rest_api.add_auto_scale("ram",0.5)
    ms_chirpstack_rest_api.add_auto_scale("bw",0.5)
    microservices.append(ms_chirpstack_rest_api)
    ms_postgresql = Microservice(
        name="postgresql",
        size=2048,
        cpus=2,
        replicas=1,
        max_replicas=3,
        cpu_ratio=50,
        ram_ratio=128,
        bw_ratio=100,
    )
    ms_postgresql.add_auto_scale("cpu",0.5)
    ms_postgresql.add_auto_scale("ram",0.5)
    ms_postgresql.add_auto_scale("bw",0.5)
    microservices.append(ms_postgresql)
    ms_redis = Microservice(
        name="redis",
        size=2048,
        cpus=2,
        replicas=1,
        max_replicas=3,
        cpu_ratio=50,
        ram_ratio=128,
        bw_ratio=100,
    )
    ms_redis.add_auto_scale("cpu",0.5)
    ms_redis.add_auto_scale("ram",0.5)
    ms_redis.add_auto_scale("bw",0.5)
    microservices.append(ms_redis)
    
create network services

    ns_list = list()
    register_device = create_network_service(
        name="register_device",
        microservices=["chirpstack", "redis", "chirpstack_gateway"],
        schdeule=[0, 1, 1],
        schedule_length=[10, 10, 10],
        ms_pool=microservices
    )
    ns_list.append(register_device)
    read_data = create_network_service(
        name="receive_data",
        microservices=["chirpstack_gateway", "mqtt_broker", "chirpstack", "postgresql"],
        schdeule=[0, 1, 2, 3],
        schedule_length=[10, 10, 10, 10],
        ms_pool=microservices
    )
    ns_list.append(read_data)
    retrive_data = create_network_service(
        name="retrive_data",
        microservices=["chirpstack_rest_api", "chirpstack", "postgresql", "chirpstack"],
        schdeule=[0, 1, 2, 3],
        schedule_length=[10, 10, 10, 10],
        ms_pool=microservices
    )
    ns_list.append(retrive_data)
    
start a simulation that randomly select network services at each iteration.

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
        backend.run_experiment(experiment=experiment, output_path="./results")
