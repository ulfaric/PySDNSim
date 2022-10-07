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

random.seed(1024)

# simulation configuration.
sim_config = Config(seed=1024, interval=1.0, step_size=0.01)

# host configuration.
host = Host(
    cpus=16,
    ram=65536,
    bw=10000,
    storage=102400,
    max_power=750.0,
    static_power=300.0,
    replicas=5,
)

# create microservices.
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

# create network service
ns_list = list()
register_device = create_network_service(
    name="register_device",
    microservices=["chirpstack", "redis", "chirpstack_gateway"],
    schdeule=[0, 1, 1],
    schedule_length=[10, 10, 10],
    ms_pool=microservices,
    flows=3
)
ns_list.append(register_device)
read_data = create_network_service(
    name="receive_data",
    microservices=["chirpstack_gateway", "mqtt_broker", "chirpstack", "postgresql"],
    schdeule=[0, 1, 2, 3],
    schedule_length=[10, 10, 10, 10],
    ms_pool=microservices,
    flows=3
)
ns_list.append(read_data)
retrive_data = create_network_service(
    name="retrive_data",
    microservices=["chirpstack_rest_api", "chirpstack", "postgresql", "chirpstack"],
    schdeule=[0, 1, 2, 3],
    schedule_length=[10, 10, 10, 10],
    ms_pool=microservices,
    flows=3
) 
ns_list.append(retrive_data)

# find baseline for each network service
backend = Backend(max_num_threads=2)
backend.start()
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

chosen_ns: List[NetworkService] = deepcopy(random.choices(ns_list, k=50))
# server network service one by one
for iter in range(50):
    experiment = Experiment(
        name=f"1_ns_{iter}",
        config=sim_config,
        host=host,
        microservices=microservices,
        network_services=[chosen_ns[iter]],
    )
    backend.add_experiment(experiment=experiment, output_path="./results/1_ns/")

for iter in range(10):
    experiment = Experiment(
        name=f"5_ns_{iter}",
        config=sim_config,
        host=host,
        microservices=microservices,
        network_services=chosen_ns[iter*5:(iter+1)*5],
    )
    backend.add_experiment(experiment=experiment, output_path="./results/5_ns/")


for iter in range(5):
    experiment = Experiment(
        name=f"10_ns_{iter}",
        config=sim_config,
        host=host,
        microservices=microservices,
        network_services=chosen_ns[iter*10:(iter+1)*10],
    )
    backend.add_experiment(experiment=experiment, output_path="./results/10_ns/")
backend.stop()


df = pd.read_csv(f"results\\register_device_baseline\\NSummary.csv")
register_device_delay = df.loc[0, "finish"] - df.loc[0, "start"]

df = pd.read_csv(f"results\\receive_data_baseline\\NSummary.csv")
receive_data_delay = df.loc[0, "finish"] - df.loc[0, "start"]

df = pd.read_csv(f"results\\retrive_data_baseline\\NSummary.csv")
retrive_data_delay = df.loc[0, "finish"] - df.loc[0, "start"]

df_1_ns = pd.DataFrame(columns=['power'])
for i in range(50):
    df_i = pd.read_csv(f"results\\1_ns\\1_ns_{i}\\DC.csv")
    df_i = df_i.loc[:,["power"]]
    df_1_ns=pd.concat([df_1_ns,df_i],ignore_index=True)
df_1_ns.index.name = "sample"
df_1_ns.to_csv("results\\1_ns\\1_ns_power.csv")

df_5_ns = pd.DataFrame(columns=['power'])
for i in range(10):
    df_i = pd.read_csv(f"results\\5_ns\\5_ns_{i}\\DC.csv")
    df_i = df_i.loc[:,["power"]]
    df_5_ns=pd.concat([df_5_ns,df_i],ignore_index=True)
df_5_ns.index.name = "sample"
df_5_ns.to_csv("results\\5_ns\\5_ns_power.csv")

df_10_ns = pd.DataFrame(columns=['power'])
for i in range(5):
    df_i = pd.read_csv(f"results\\10_ns\\10_ns_{i}\\DC.csv")
    df_i = df_i.loc[:,["power"]]
    df_10_ns=pd.concat([df_10_ns,df_i],ignore_index=True)
df_10_ns.index.name = "sample"
df_10_ns.to_csv("results\\10_ns\\10_ns_power.csv")

# success_rate = list()
# fail_rate = list()
# delays = list()
# for i in range(100):
#     success = 0
#     fail = 0
#     average_delay = 0
#     df = pd.read_csv(f"results\\{i}\\NSummary.csv")
#     for row_index in range(len(df)):
#         if df.loc[row_index, "complete"] == True:
#             success = success + 1
#             average_delay = average_delay + (
#                 df.loc[row_index, "finish"] - df.loc[row_index, "start"]
#             )
#             if df.loc[row_index, "name"] == "register_device":
#                 average_delay = average_delay - register_device_delay
#             if df.loc[row_index, "name"] == "receive_data":
#                 average_delay = average_delay - receive_data_delay
#             if df.loc[row_index, "name"] == "retrive_data":
#                 average_delay = average_delay - retrive_data_delay
#         if df.loc[row_index, "complete"] == False:
#             fail = fail + 1
#             if df.loc[row_index, "name"] == "register_device":
#                 average_delay = average_delay + register_device_delay
#             if df.loc[row_index, "name"] == "receive_data":
#                 average_delay = average_delay + receive_data_delay
#             if df.loc[row_index, "name"] == "retrive_data":
#                 average_delay = average_delay + retrive_data_delay
#     average_delay = average_delay / len(df)
#     delays.append(average_delay)
#     success_rate.append(success / len(df))
#     fail_rate.append(fail / len(df))

# df = pd.DataFrame(
#     {
#         "id": [i for i in range(10)],
#         "Success rate": success_rate,
#         "Fail rate": fail_rate,
#         "Delay": delays,
#     }
# )

# app = Dash(__name__)

# fig_delay = px.bar(data_frame=df, x="id", y="Delay", title="Delay")
# fig_delay.update_xaxes(dtick=1)
# app.layout = html.Div(
#     [
#         html.H4("Network Service"),
#         dcc.Graph(id="graph", animate=True),
#         dcc.Checklist(
#             id="dropdown",
#             options=["Success", "Fail"],
#             value=["Success"],
#         ),
#         dcc.Graph(id="graph_delay", animate=True, figure=fig_delay),
#     ]
# )


# @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
# def display_color(selection: List):
#     fig = go.Figure()
#     if selection.count("Success") != 0:
#         fig.add_trace(go.Scatter(x=df["id"], y=df["Success rate"], name="Success rate"))
#     if selection.count("Fail") != 0:
#         fig.add_trace(go.Scatter(x=df["id"], y=df["Fail rate"], name="Fail rate"))
#     fig.update_layout(title="Success/Fail rate", xaxis_title="id", yaxis_title="Rate")
#     fig.update_xaxes(dtick=1)
#     return fig


# app.run_server(debug=True)