from PySDNSim.AutoScale import AutoScale
from typing import List
class Microservice:
    """
    Represents a Microservice.
    """

    _name: str
    _size: int
    _cpus: int
    _ram: int
    _bw: int
    _replicas: int
    _max_replicas: int
    _cpu_ratio: int
    _ram_ratio: int
    _bw_ratio: int
    _auto_scale: List[AutoScale]

    def __init__(self, name: str, size: int, cpus: int, ram: int, bw: int, replicas: int, max_replicas: int,
                 cpu_ratio: int, ram_ratio: int, bw_ratio: int):
        """
        Create a new Microservice with the given name, size, cpus, ram, bw, replicas, max_replicas, cpu_ratio, ram_ratio and bw_ratio.

        :param name: name of the new Microservice.
        :param size: image size of the new Microservice.
        :param cpus: number of cpus of the new Microservice.
        :param ram: size of ram of the new Microservice.
        :param bw: capacity of bw of the new Microservice.
        :param replicas: number of replicas of the new Microservice.
        :param max_replicas: maximum number of replicas of the new Microservice.
        :param cpu_ratio: amount of cpu that each flow consumes.
        :param ram_ratio: amount of ram that each flow consumes.
        :param bw_ratio: amount of bw that each flow consumes.
        """
        self._name = name
        self._size = size
        self._cpus = cpus
        self._ram = ram
        self._bw = bw
        self._replicas = replicas
        self._max_replicas = max_replicas
        self._cpu_ratio = cpu_ratio
        self._ram_ratio = ram_ratio
        self._bw_ratio = bw_ratio
        self._auto_scale = list()
        
    def add_auto_scale(self, telemetry:str, threshold:float):
        auto_scale = AutoScale(telemetry, threshold)
        self._auto_scale.append(auto_scale)

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def cpus(self):
        return self._cpus

    @property
    def ram(self):
        return self._ram

    @property
    def bw(self):
        return self._bw

    @property
    def replicas(self):
        return self._replicas

    @property
    def max_replicas(self):
        return self._max_replicas

    @property
    def cpu_ratio(self):
        return self._cpu_ratio

    @property
    def ram_ratio(self):
        return self._ram_ratio

    @property
    def bw_ratio(self):
        return self._bw_ratio
    
    @property
    def auto_scale(self):
        return self._auto_scale