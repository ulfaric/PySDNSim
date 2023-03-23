import json
import os
import subprocess
from threading import Thread
from typing import List, Union

from PySDNSim.Config import Config
from PySDNSim.Experiment import Experiment
from PySDNSim.Host import Host
from PySDNSim.Log import logger
from PySDNSim.Microservice import Microservice
from PySDNSim.NetworkService import NetworkService


class Backend:
    _ready: Union[bool, None]
    _debug:bool

    def __init__(self, debug: bool = False):
        self._debug = debug
        if os.path.isfile("backend.jar"):
            if self.debug:
                logger.info("Found simulation backend executable file.")
            self._ready = True
        else:
            if self.debug:
                logger.error("Can not find simulation backend executable file.")
            self._ready = False



    @property
    def ready(self):
        return self._ready
    
    @property
    def debug(self):
        return self._debug

    @staticmethod
    def generate_config(
        config: Config,
        hosts: List[Host],
        microservices: List[Microservice],
        network_services: List[NetworkService],
        config_file: str,
        debug: bool = False,
    ):
        sim_config = dict()
        sim_config["Config"] = {
            "interval": config.interval,
            "sampleInterval": config.sample_interval,
            "stepSize": config.step_size,
            "seed": config.seed,
        }

        sim_config["Hosts"] = list()
        for host in hosts:
            sim_config["Hosts"].append(
                {
                    "replica": host.replicas,
                    "ram": host.ram,
                    "bw": host.bw,
                    "storage": host.storage,
                    "pes": host.cpus,
                    "maxPower": host.max_power,
                    "staticPower": host.static_power,
                    "vmScheduler": host.vm_scheduler,
                }
            )

        sim_config["Microservices"] = list()
        for ms in microservices:
            ms_config = {
                "name": ms.name,
                "size": ms.size,
                "cpu": ms.cpus,
                "ram": ms.ram,
                "bw": ms.bw,
                "replicas": ms.replicas,
                "maxReplicas": ms.max_replicas,
                "cpuRatio": ms.cpu_ratio,
                "ramRatio": ms.ram_ratio,
                "bwRatio": ms.bw_ratio,
                "idleCPU": ms.idle_cpu,
                "idleRAM": ms.idle_ram,
                "idleBW": ms.idle_bw,
            }
            ms_config["autoScale"] = list()
            for auto_scale in ms.auto_scale:
                ms_config["autoScale"].append({"telemetry": auto_scale.telemetry,"threshold": auto_scale.threshold})
                
            sim_config["Microservices"].append(ms_config)

        sim_config["NetworkServices"] = list()
        for ns in network_services:
            ns_config = {"name": ns.name, "flows": ns.flows, "Job": list()}
            for job in ns.jobs:
                job_config = {
                    "ms": job.ms_id,
                    "length": job.length,
                    "schedule": job.schedule,
                }
                ns_config["Job"].append(job_config)
            sim_config["NetworkServices"].append(ns_config)

        if os.path.exists("configs") is False:
            os.makedirs("configs")
        if debug:
            logger.info(f"Generated new simulation configuration file\t {config_file}.")
        with open("configs/" + config_file, "w+") as file:
            json.dump(sim_config, file, indent=4)

    def run_experiment(self, experiment: Experiment, output_path: str):
        if self.ready is True:
                config_file = experiment.name + ".json"
                
                if os.path.exists(output_path) is False:
                    os.makedirs(output_path)

                self.generate_config(
                    config=experiment.config,
                    hosts=[experiment.host],
                    microservices=experiment.microservices,
                    network_services=experiment.network_services,
                    config_file=config_file,
                    debug = self.debug
                )

                subprocess.call(
                        [
                            "java",
                            "-jar",
                            "backend.jar",
                            "./configs/" + config_file,
                            output_path + "/" + experiment.name,
                        ]
                    )
                if self.debug:
                    logger.info(f"Simulation completed for experiment\t {experiment.name}.")

        else:
            raise RuntimeError("Simulation backend executable file is missing.")

        
