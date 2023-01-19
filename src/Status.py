#!/bin/python3

from dataclasses import dataclass


@dataclass(frozen=True)
class Status:
    co2_in_ppm: int
    temperature_in_celsius: float
