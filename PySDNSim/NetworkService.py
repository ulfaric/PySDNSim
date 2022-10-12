from distutils.log import INFO
from typing import List
from uuid import uuid4

from PySDNSim.Job import Job
from PySDNSim.Microservice import Microservice


class NetworkService:
    """
    Represents a network service.
    """
    _id:int
    _name: str
    _flows: int
    _jobs: List[Job]

    def __init__(self, name: str, flows: int):
        """
        Create a new network service with the given name and flows.

        :param name: name of the network service.
        :param flows: number of flows of the network service.
        """
        self._id = uuid4()
        self._name = name
        self._flows = flows
        self._jobs = list()
        
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
    def flows(self):
        return self._flows

    @flows.setter
    def flows(self, flows: int):
        self._flows = flows

    @property
    def jobs(self):
        return self._jobs

    def add_job(self, ms_name:str, length:int, schedule:int, ms_pool:List[Microservice]):
        """Add a job to network service.
        
        Args:
            ms_name (str): name of the microservice.
            length (int): length of the job.
            schedule (int): schedule of the job.
            ms_pool (List[Microservice]): available microservices.
        """
        job = Job(ms_name=ms_name, length=length, schedule=schedule, ms_pool=ms_pool)
        self.jobs.append(job)
        self.jobs.sort(key=lambda x: x.schedule)

    def offset_schedule(self, offset: int):
        """Offset all the job schedule. This allow you to predefine and reuse a network services with different start time.

        Args:
            offset (int): the offset.
        """
        for job in self.jobs:
            job._schedule = job.schedule + offset
            
    def get_schedule(self)->List[List[int]]:
        """Return the schedule of the network service.

        Returns:
            List[List[int]]: list of schedule in microservice id.
        """
        schedule = list()
        self.jobs.sort(key=lambda x: x.schedule)
        for i in range(self.jobs[-1].schedule+1):
            time_slot = list()
            for job in self.jobs:
                if job.schedule == i:
                    time_slot.append(job.ms_id)
            schedule.append(time_slot)
        return schedule

def create_network_service(name:str, microservices:List[str], schdeule:List[int], schedule_length:List[int], ms_pool:List[Microservice], flows:int=1) -> NetworkService:
    """Create a network service.

    Args:
        name (str): name of the network service.
        microservices (List[int]): list of microservices.
        schdeule (List[int]): list of schedule  for each microservice.
        schedule_length (List[int]): list of length for each schedule.
        flows (int, optional): number of flows. Defaults to 1.
        ms_pool (List[Microservice]): list of available microservices.

    Raises:
        RuntimeError: If lists of microservices, schedule and schedule length are mismatching.

    Returns:
        NetworkService: the created network service.
    """
    
    if len(microservices) != len(schdeule) or len(microservices) != len(schedule_length) or len(schdeule) != len(schedule_length):
        raise RuntimeError("Lists of microservices, schedule amd length are miss matching!")
    else:
        ns = NetworkService(name=name,flows=flows)
        for index, value  in enumerate(microservices):
            ns.add_job(ms_name=value, length=schedule_length[index], schedule=schdeule[index], ms_pool=ms_pool)
        return ns