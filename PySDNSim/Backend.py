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
    _terminated: Union[bool, None]
    _max_num_threads: int
    _main_thread: Thread
    _terminator: Thread
    _backend_thread_queue: List[Thread]
    _running_backend_threads: List[Thread]

    def __init__(self, max_num_threads: int = 4):
        if os.path.isfile("backend.jar"):
            logger.info("Found simulation backend executable file.")
            self._ready = True
        else:
            logger.error("Can not find simulation backend executable file.")
            self._ready = False
        self._terminated = False
        self._max_num_threads = max_num_threads
        self._backend_thread_queue = list()
        self._running_backend_threads = list()

    @property
    def ready(self):
        return self._ready

    @property
    def terminated(self):
        return self._terminated

    @property
    def max_num_threads(self):
        return self._max_num_threads

    @property
    def main_thread(self):
        return self._main_thread

    @property
    def termminator(self):
        return self._terminator

    @property
    def backend_thread_queue(self):
        return self._backend_thread_queue

    @property
    def running_backend_threads(self):
        return self._running_backend_threads

    @staticmethod
    def generate_config(
        config: Config,
        hosts: List[Host],
        microservices: List[Microservice],
        network_services: List[NetworkService],
        config_file: str,
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

        logger.info(f"Generated new simulation configuration file\t {config_file}.")
        with open("configs/" + config_file, "w+") as config_file:
            json.dump(sim_config, config_file, indent=4)

    def start(self):
        if self.ready is True:
            self._main_thread = Thread(target=self.execute_experiments)
            self._main_thread.start()
        else:
            raise RuntimeError("Can't start, simulation backend executable file is missing.")

    def stop(self):
        if self.main_thread.is_alive():
            def wait_for_running_process():
                all_threads_complete = False
                while all_threads_complete is not True:
                    all_threads_complete = True
                    for thread in self.running_backend_threads:
                        if thread.is_alive():
                            all_threads_complete = False
                            break
                        else:
                            continue
                if all_threads_complete:
                    self._terminated = True

            self._terminator = Thread(target=wait_for_running_process, name="terminator")
            self._terminator.start()
            self._terminator.join()
        else:
            raise RuntimeWarning(f"Simulation backend has not started yet.")

    def add_experiment(self, experiment: Experiment, output_path: str):
        if self.ready is True:
            config_file = experiment.name + ".json"
            
            if os.path.exists(output_path) is False:
                os.makedirs(output_path)

            def backend_target():
                """
                Call javar simulation backend with configuration file.

                :return: None
                """
                subprocess.call(
                    [
                        "java",
                        "-jar",
                        "backend.jar",
                        "./configs/" + config_file,
                        output_path + "/" + experiment.name,
                    ]
                )

            self.generate_config(
                config=experiment.config,
                hosts=[experiment.host],
                microservices=experiment.microservices,
                network_services=experiment.network_services,
                config_file=config_file,
            )

            backend_process = Thread(target=backend_target, name=experiment.name)
            self.backend_thread_queue.append(backend_process)
        else:
            raise RuntimeError("Simulation backend executable file is missing.")

    def execute_experiments(self):
        while self.terminated is False or len(self.running_backend_threads)>0:
            if len(self.running_backend_threads) != 0:
                for backend_thread in self.running_backend_threads[:]:
                    if backend_thread.is_alive():
                        continue
                    else:
                        self._running_backend_threads.remove(backend_thread)
                        logger.info(f"Experiment\t {backend_thread.name} \tfinsihed.")

            while (
                len(self.running_backend_threads) < 6
                and len(self.backend_thread_queue) != 0
            ):
                backend_thread = self.backend_thread_queue.pop(0)
                self._running_backend_threads.append(backend_thread)
                backend_thread.start()
                logger.info(f"Experiment\t {backend_thread.name} \tstarted.")
        logger.info("Simulation terminated, all experiment complete successfully.")
