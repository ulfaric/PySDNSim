from uuid import uuid4
from PySDNSim.AutoScale import AutoScale
from typing import List
class Microservice:
    """
    Represents a Microservice.
    """
    _id:int
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
    _idle_cpu: int
    _idle_ram: int
    _idle_bw: int
    _auto_scale: List[AutoScale]

    def __init__(self, name: str, size: int, cpus: int, replicas: int, max_replicas: int,
                 cpu_ratio: int, ram_ratio: int, bw_ratio: int, idle_cpu: int = None, idle_ram: int = None, idle_bw: int = None):
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
        self._id = uuid4()
        self._name = name
        self._size = size
        self._replicas = replicas
        self._max_replicas = max_replicas
        self._cpu_ratio = cpu_ratio
        self._ram_ratio = ram_ratio
        self._bw_ratio = bw_ratio
        if idle_cpu is not None:
            self._idle_cpu = idle_cpu
        else:
            self._idle_cpu = cpu_ratio
        if idle_ram is not None:
            self._idle_ram = idle_ram
        else:
            self._idle_ram = ram_ratio
        if idle_bw is not None:
            self._idle_bw = idle_bw
        else:
            self._idle_bw = bw_ratio  
        self._cpus = cpus + self.idle_cpu/100
        self._ram = round(ram_ratio * cpus / (cpu_ratio/100)) + self.idle_ram
        self._bw = round(bw_ratio * cpus / (cpu_ratio/100)) + self.idle_bw
        self._auto_scale = list()
        
    def add_auto_scale(self, telemetry:str, threshold:float):
        auto_scale = AutoScale(telemetry, threshold)
        self._auto_scale.append(auto_scale)
        
    def __lt__(self, __o: object) -> bool:
        if self.id > __o.id:
            return True
        else:
            return False
        
    def __eq__(self, __o: object) -> bool:
        if self.id == __o.id:
            return True
        else:
            return False
        
    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self._id
    
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
    def idle_cpu(self):
        return self._idle_cpu
    
    @property
    def idle_ram(self):
        return self._idle_ram
    
    @property
    def idle_bw(self):
        return self._idle_bw
    
    @property
    def auto_scale(self):
        return self._auto_scale