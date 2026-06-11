from dataclasses import dataclass


@dataclass(frozen=True)
class HedData:
    SAMPLING_RATE: int
    GAIN: int
