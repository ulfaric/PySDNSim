class AutoScale:
    """
    AutoScale config for microservices.
    """
    _telemetry: str
    _threshold: float

    def __init__(self, telemetry: str, threshold: float):
        """
        create a new AutoScale config with  the given telemetry and threshold.

        :param telemetry: telemetry.
        :param threshold: threshold value.
        """
        self._telemetry: str = telemetry
        self._threshold: float = threshold

    @property
    def telemetry(self) -> str:
        return self._telemetry

    @property
    def threshold(self) -> float:
        return self._threshold
