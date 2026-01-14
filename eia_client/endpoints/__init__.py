"""API endpoint modules."""

from .base import BaseEndpoint
from .electricity import ElectricityEndpoint
from .renewable import RenewableEndpoint

__all__ = [
    "BaseEndpoint",
    "ElectricityEndpoint",
    "RenewableEndpoint",
]
