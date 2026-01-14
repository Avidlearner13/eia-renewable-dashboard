"""
EIA API Client - Python client for U.S. Energy Information Administration API.

A modular, SOLID-principle based client for accessing renewable energy data
from the EIA Open Data API.

Example:
    >>> from eia_client import EIAClient, RenewableEndpoint
    >>>
    >>> # Initialize client
    >>> client = EIAClient.from_api_key("your-api-key")
    >>>
    >>> # Access renewable energy data
    >>> renewable = RenewableEndpoint(client)
    >>> solar_data = renewable.get_solar_generation(
    ...     frequency="daily",
    ...     start="2024-01-01",
    ...     end="2024-01-31"
    ... )
    >>>
    >>> for record in solar_data.data:
    ...     print(f"{record.period}: {record.value} MWh")
"""

__version__ = "1.0.0"
__author__ = "EIA Client"

from .client import EIAClient
from .config import EIAConfig
from .exceptions import (
    EIAException,
    EIAAuthenticationError,
    EIADataNotFoundError,
    EIARateLimitError,
    EIARequestError,
    EIAValidationError,
)
from .endpoints import (
    BaseEndpoint,
    ElectricityEndpoint,
    RenewableEndpoint,
)
from .models import (
    FuelTypeData,
    GeneratorCapacity,
    ElectricityGeneration,
    RenewableSource,
)
from .utils import (
    export_to_csv,
    export_to_json,
    export_to_dataframe,
    collect_all,
)

__all__ = [
    # Client
    "EIAClient",
    "EIAConfig",
    # Exceptions
    "EIAException",
    "EIAAuthenticationError",
    "EIADataNotFoundError",
    "EIARateLimitError",
    "EIARequestError",
    "EIAValidationError",
    # Endpoints
    "BaseEndpoint",
    "ElectricityEndpoint",
    "RenewableEndpoint",
    # Models
    "FuelTypeData",
    "GeneratorCapacity",
    "ElectricityGeneration",
    "RenewableSource",
    # Utils
    "export_to_csv",
    "export_to_json",
    "export_to_dataframe",
    "collect_all",
]
