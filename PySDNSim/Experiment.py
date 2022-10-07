from copy import deepcopy
from typing import List, Union
from PySDNSim.Config import Config
from PySDNSim.Host import Host
from PySDNSim.Microservice import Microservice
from PySDNSim.NetworkService import NetworkService


class Experiment:
    _name: str
    _config: Config
    _host: Host
    _microservices: List[Microservice]
    _network_services: List[NetworkService]

    def __init__(
        self,
        name: str,
        config: Config,
        host:Host,
        microservices: List[Microservice],
        network_services: List[NetworkService],
    ) -> None:
        self._name = name
        self._config = config
        self._host = host
        self._microservices = deepcopy(microservices)
        self._network_services = deepcopy(network_services)

    @property
    def name(self):
        return self._name

    @property
    def config(self):
        return self._config

    @property
    def host(self):
        return self._host

    @property
    def microservices(self):
        return self._microservices

    @property
    def network_services(self):
        return self._network_services

    def scale_all(self, resource: str, value: Union[int, float]):
        """Scale resoource for all microservices.

        Args:
            resource (str): resource name, "cpu", "ram", or "bw".
            value (Union[int,float]): value to scale.

        Raises:
            RuntimeWarning: if a wrong resource name is given.
        """
        if resource == "cpu":
            for ms in self.microservices:
                ms._cpus = ms.cpus + value
        elif resource == "ram":
            for ms in self.microservices:
                ms._ram = ms.ram + value
        elif resource == "bw":
            for ms in self.microservices:
                ms._bw = ms.bw + value
        else:
            raise RuntimeWarning(f"Resource {resource} does not exist.")

    def scale(self, ms_name: str, resource: str, value: Union[int, float]):
        """Scale resoource for a specific microservice.

        Args:
            ms_name (str): microservices name.
            resource (str): resource name, "cpu", "ram", or "bw".
            value (Union[int, float]): value to scale.

        Raises:
            RuntimeWarning: if microservice is not found or resource name is not correct.
        """
        found_ms = False
        if resource == "cpu":
            for ms in self.microservices:
                if ms.name == ms_name:
                    ms._cpus = ms.cpus + value
                    found_ms = True
                    break
        elif resource == "ram":
            for ms in self.microservices:
                if ms.name == ms_name:
                    ms._ram = ms.ram + value
                    found_ms = True
                    break
        elif resource == "bw":
            for ms in self.microservices:
                if ms.name == ms_name:
                    ms._bw = ms.bw + value
                    found_ms = True
                    break
        else:
            if found_ms is False:
                raise RuntimeWarning(f"Microservice {ms_name} not found.")
            else:
                raise RuntimeWarning(f"Resource {resource} does not exist.")
            
    def set_num_flows(self, num_flows:int):
        for ns in self.network_services:
            ns._flows = num_flows
            
