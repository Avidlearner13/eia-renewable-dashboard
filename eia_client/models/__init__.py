"""Data models for EIA API responses."""

from .base import BaseModel, PaginatedResponse
from .renewable import (
    FuelTypeData,
    GeneratorCapacity,
    ElectricityGeneration,
    RenewableSource,
)

__all__ = [
    "BaseModel",
    "PaginatedResponse",
    "FuelTypeData",
    "GeneratorCapacity",
    "ElectricityGeneration",
    "RenewableSource",
]
