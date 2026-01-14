"""High-level renewable energy endpoint with convenient methods."""

from typing import Dict, Generator, List, Optional, Any
from collections import defaultdict

from .base import BaseEndpoint
from .electricity import ElectricityEndpoint
from ..models.base import PaginatedResponse
from ..models.renewable import (
    FuelTypeData,
    GeneratorCapacity,
    RenewableSource,
    StateRenewableProfile,
)


class RenewableEndpoint(BaseEndpoint):
    """Specialized endpoint for renewable energy data analysis."""

    BASE_ROUTE = "electricity"

    # EIA fuel type codes for renewables
    SOLAR_CODE = "SUN"
    WIND_CODE = "WND"
    HYDRO_CODE = "WAT"

    # Energy source codes for capacity data
    RENEWABLE_ENERGY_SOURCES = ["SUN", "WND", "WAT", "GEO", "WDS", "BIO", "OBG", "OBS"]

    def __init__(self, client):
        """Initialize renewable endpoint.

        Args:
            client: EIA API client instance.
        """
        super().__init__(client)
        self._electricity = ElectricityEndpoint(client)

    # ==================== Solar Data ====================

    def get_solar_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[FuelTypeData]:
        """Get solar generation data.

        Args:
            frequency: Data frequency (hourly, daily).
            start: Start datetime (YYYY-MM-DDTHH for hourly).
            end: End datetime.
            respondents: Balancing authority codes to filter.
            limit: Max records.

        Returns:
            Solar generation data.
        """
        return self._electricity.get_fuel_type_generation(
            fuel_types=[self.SOLAR_CODE],
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            limit=limit,
        )

    def get_all_solar_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[FuelTypeData, None, None]:
        """Get all solar generation data with pagination.

        Args:
            frequency: Data frequency.
            start: Start datetime.
            end: End datetime.
            respondents: Balancing authority codes.
            max_records: Maximum records to fetch.

        Yields:
            Solar generation records.
        """
        yield from self._electricity.get_all_fuel_type_generation(
            fuel_types=[self.SOLAR_CODE],
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            max_records=max_records,
        )

    # ==================== Wind Data ====================

    def get_wind_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[FuelTypeData]:
        """Get wind generation data.

        Args:
            frequency: Data frequency.
            start: Start datetime.
            end: End datetime.
            respondents: Balancing authority codes.
            limit: Max records.

        Returns:
            Wind generation data.
        """
        return self._electricity.get_fuel_type_generation(
            fuel_types=[self.WIND_CODE],
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            limit=limit,
        )

    def get_all_wind_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[FuelTypeData, None, None]:
        """Get all wind generation data with pagination.

        Yields:
            Wind generation records.
        """
        yield from self._electricity.get_all_fuel_type_generation(
            fuel_types=[self.WIND_CODE],
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            max_records=max_records,
        )

    # ==================== Hydro Data ====================

    def get_hydro_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[FuelTypeData]:
        """Get hydro generation data.

        Returns:
            Hydro generation data.
        """
        return self._electricity.get_fuel_type_generation(
            fuel_types=[self.HYDRO_CODE],
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            limit=limit,
        )

    # ==================== Combined Renewable Data ====================

    def get_all_renewable_generation(
        self,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        respondents: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[FuelTypeData]:
        """Get generation data for all renewable sources.

        Args:
            frequency: Data frequency.
            start: Start datetime.
            end: End datetime.
            respondents: Balancing authority codes.
            limit: Max records.

        Returns:
            All renewable generation data.
        """
        renewable_codes = [self.SOLAR_CODE, self.WIND_CODE, self.HYDRO_CODE]
        return self._electricity.get_fuel_type_generation(
            fuel_types=renewable_codes,
            respondents=respondents,
            frequency=frequency,
            start=start,
            end=end,
            limit=limit,
        )

    # ==================== Capacity Data ====================

    def get_solar_capacity(
        self,
        states: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[GeneratorCapacity]:
        """Get solar generator capacity.

        Args:
            states: Filter by state codes.
            limit: Max records.

        Returns:
            Solar capacity data.
        """
        return self._electricity.get_operating_capacity(
            states=states,
            energy_sources=[self.SOLAR_CODE],
            statuses=["OP"],  # Operating only
            limit=limit,
        )

    def get_wind_capacity(
        self,
        states: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[GeneratorCapacity]:
        """Get wind generator capacity.

        Args:
            states: Filter by state codes.
            limit: Max records.

        Returns:
            Wind capacity data.
        """
        return self._electricity.get_operating_capacity(
            states=states,
            energy_sources=[self.WIND_CODE],
            statuses=["OP"],
            limit=limit,
        )

    def get_all_renewable_capacity(
        self,
        states: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[GeneratorCapacity, None, None]:
        """Get all renewable generator capacity with pagination.

        Args:
            states: Filter by state codes.
            max_records: Maximum records.

        Yields:
            Generator capacity records for renewables.
        """
        yield from self._electricity.get_all_operating_capacity(
            states=states,
            energy_sources=self.RENEWABLE_ENERGY_SOURCES,
            statuses=["OP"],
            max_records=max_records,
        )

    # ==================== Aggregation Methods ====================

    def get_state_renewable_summary(
        self,
        states: Optional[List[str]] = None,
        max_records: int = 50000,
    ) -> Dict[str, Dict[str, float]]:
        """Get aggregated renewable capacity by state.

        Args:
            states: Filter by state codes (None for all states).
            max_records: Max records to process.

        Returns:
            Dictionary of state -> {source: capacity_mw}.
        """
        state_summary: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

        for generator in self.get_all_renewable_capacity(
            states=states,
            max_records=max_records,
        ):
            state = generator.state
            source = generator.energy_source
            capacity = generator.nameplate_capacity_mw

            state_summary[state][source] += capacity
            state_summary[state]["total"] += capacity

        return dict(state_summary)

    def get_balancing_authorities(self) -> List[Dict[str, str]]:
        """Get list of available balancing authorities (RTOs/ISOs).

        Returns:
            List of balancing authority info.
        """
        metadata = self._electricity.get_metadata("rto/fuel-type-data")
        facets = metadata.get("response", {}).get("facets", [])

        for facet in facets:
            if facet.get("id") == "respondent":
                return facet.get("facetValueCounts", [])

        return []

    def get_fuel_types(self) -> List[Dict[str, str]]:
        """Get list of available fuel types.

        Returns:
            List of fuel type info with codes and descriptions.
        """
        metadata = self._electricity.get_metadata("rto/fuel-type-data")
        facets = metadata.get("response", {}).get("facets", [])

        for facet in facets:
            if facet.get("id") == "fueltype":
                return facet.get("facetValueCounts", [])

        return []
