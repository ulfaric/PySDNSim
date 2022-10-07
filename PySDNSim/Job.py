from uuid import uuid4
from PySDNSim.Microservice import Microservice
from typing import List

class Job:
    """
    Represents a single job.
    """
    _id:int
    _ms:Microservice
    _ms_id: int
    _length: int
    _schedule: int

    def __init__(self, ms_name: str, length: int,schedule: int, ms_pool:List[Microservice]):
        """
        Create a new Job with the given ms, length, file_size, schedule specified.

        :param ms: id of microservice.
        :param length: length of the job in MIPS.
        :param file_size: input/output size of the job in bytes.
        :param schedule: schedule of the job.
        """
        self._id = uuid4()
        for ms in ms_pool:
            if ms.name == ms_name:  
                self._ms = ms       
                self._ms_id = ms_pool.index(ms)
        self._length = length
        self._schedule = schedule
        
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
    def ms(self):
        return self._ms
    
    @property
    def ms_id(self):
        return self._ms_id

    @property
    def length(self):
        return self._length

    @property
    def schedule(self):
        return self._schedule
