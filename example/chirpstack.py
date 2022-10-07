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

random.seed(1024)

# simulation configuration.
sim_config = Config(seed=1024, interval=1.0, step_size=0.01)

# host configuration.
host = Host(
    cpus=64,
    ram=102400,
    bw=100000,
    storage=1024000,
    max_power=1600.0,
    static_power=300.0,
    replicas=3,
)

# create microservices.
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

# create network service
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

# find baseline for each network service
backend = Backend(max_num_threads=2)
baseline_register_device = Experiment(
    name="register_device_baseline",
    config=sim_config,
    host=host,
    microservices=microservices,
    network_services=[register_device],
)
backend.add_experiment(experiment=baseline_register_device, output_path="./results")
baseline_receive_data = Experiment(
    name="receive_data_baseline",
    config=sim_config,
    host=host,
    microservices=microservices,
    network_services=[read_data],
)
backend.add_experiment(experiment=baseline_receive_data, output_path="./results")
baseline_retrive_data = Experiment(
    name="retrive_data_baseline",
    config=sim_config,
    host=host,
    microservices=microservices,
    network_services=[retrive_data],
)
backend.add_experiment(experiment=baseline_retrive_data, output_path="./results")

# randomly select network service
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

df = pd.read_csv(f"results\\register_device_baseline\\NSummary.csv")
register_device_delay = df.loc[0, "finish"] - df.loc[0, "start"]

df = pd.read_csv(f"results\\receive_data_baseline\\NSummary.csv")
receive_data_delay = df.loc[0, "finish"] - df.loc[0, "start"]

df = pd.read_csv(f"results\\retrive_data_baseline\\NSummary.csv")
retrive_data_delay = df.loc[0, "finish"] - df.loc[0, "start"]


success_rate = list()
fail_rate = list()
delays = list()
for i in range(10):
    success = 0
    fail = 0
    average_delay = 0
    df = pd.read_csv(f"results\\{i}\\NSummary.csv")
    for row_index in range(len(df)):
        if df.loc[row_index, "complete"] == True:
            success = success + 1
            average_delay = average_delay + (
                df.loc[row_index, "finish"] - df.loc[row_index, "start"]
            )
            if df.loc[row_index, "name"] == "register_device":
                average_delay = average_delay - register_device_delay
            if df.loc[row_index, "name"] == "receive_data":
                average_delay = average_delay - receive_data_delay
            if df.loc[row_index, "name"] == "retrive_data":
                average_delay = average_delay - retrive_data_delay
        if df.loc[row_index, "complete"] == False:
            fail = fail + 1
            if df.loc[row_index, "name"] == "register_device":
                average_delay = average_delay + register_device_delay
            if df.loc[row_index, "name"] == "receive_data":
                average_delay = average_delay + receive_data_delay
            if df.loc[row_index, "name"] == "retrive_data":
                average_delay = average_delay + retrive_data_delay
    average_delay = average_delay / len(df)
    delays.append(average_delay)
    success_rate.append(success / len(df))
    fail_rate.append(fail / len(df))

df = pd.DataFrame(
    {
        "id": [i for i in range(10)],
        "Success rate": success_rate,
        "Fail rate": fail_rate,
        "Delay": delays,
    }
)

app = Dash(__name__)

fig_delay = px.bar(data_frame=df, x="id", y="Delay", title="Delay")
fig_delay.update_xaxes(dtick=1)
app.layout = html.Div(
    [
        html.H4("Network Service"),
        dcc.Graph(id="graph", animate=True),
        dcc.Checklist(
            id="dropdown",
            options=["Success", "Fail"],
            value=["Success"],
        ),
        dcc.Graph(id="graph_delay", animate=True, figure=fig_delay),
    ]
)


@app.callback(Output("graph", "figure"), Input("dropdown", "value"))
def display_color(selection: List):
    fig = go.Figure()
    if selection.count("Success") != 0:
        fig.add_trace(go.Scatter(x=df["id"], y=df["Success rate"], name="Success rate"))
    if selection.count("Fail") != 0:
        fig.add_trace(go.Scatter(x=df["id"], y=df["Fail rate"], name="Fail rate"))
    fig.update_layout(title="Success/Fail rate", xaxis_title="id", yaxis_title="Rate")
    fig.update_xaxes(dtick=1)
    return fig


app.run_server(debug=True)

tree = Tree()
n = Node()