from dataclasses import dataclass


@dataclass
class BikeData:
    speed: int = 0
    rpm: int = 1200
    gear: str = "N"
    fuel: int = 78
    coolant: int = 172
    battery: float = 14.2
    ktrc: int = 1
    power_mode: str = "F"