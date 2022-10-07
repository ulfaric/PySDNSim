from distutils.log import INFO
from typing import List

from PySDNSim.Job import Job


class NetworkService:
    """
    Represents a network service.
    """

    _name: str
    _flows: int
    _jobs: List[Job]

    def __init__(self, name: str, flows: int):
        """
        Create a new network service with the given name and flows.

        :param name: name of the network service.
        :param flows: number of flows of the network service.
        """
        self._name = name
        self._flows = flows
        self._jobs = list()

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

    def add_job(self, job: Job):
        """Add a job to the network services

        Args:
            job (Job): job to be added.
        """
        self._jobs.append(job)

    def offset_schedule(self, offset: int):
        """Offset all the job schedule. This allow you to predefine and reuse a network services with different start time.

        Args:
            offset (int): the offset.
        """
        for job in self.jobs:
            job._schedule = job.schedule + offset

def create_network_service(name:str, microservices:List[int], schdeule:List[int], schedule_length:List[int], flows:int=1) -> NetworkService:
    """Create a network service.

    Args:
        name (str): name of the network service.
        microservices (List[int]): list of microservices.
        schdeule (List[int]): list of schedule  for each microservice.
        schedule_length (List[int]): list of length for each schedule.
        flows (int, optional): number of flows. Defaults to 1.

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
            job = Job(ms=value, length=schedule_length[index], schedule=schdeule[index])
            ns.add_job(job)
        return ns
        
    