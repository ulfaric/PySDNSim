from typing import Any


class Config:
    """
    Simulation configurations.
    """
    _interval: float
    _sample_interval:float
    _step_size: float
    _seed: Any

    def __init__(self, seed: Any, interval: float = 1.0, sample_interval:float=1.0, step_size: float = 0.001):
        """Simulation basic configurations.

        Args:
            seed (Any): seed for random.
            interval (float, optional): datacenter schedule interval, must be larger than step size. Defaults to 1.0.
            sample_interval (float, optional): data collection interval, must be larger than step size. Defaults to 1.0.
            step_size (float, optional): simulation step size, should be smaller or equal to 0.01. Defaults to 0.001.
        """
        self._interval = interval
        self._sample_interval = sample_interval
        self._step_size = step_size
        self._seed = seed

    @property
    def interval(self):
        return self._interval

    @property
    def step_size(self):
        return self._step_size

    @property
    def seed(self):
        return self._seed

    @property
    def sample_interval(self):
        return self._sample_interval