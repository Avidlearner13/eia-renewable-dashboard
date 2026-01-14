"""Electricity-related API endpoints."""

from typing import Generator, List, Optional, Dict, Any

from .base import BaseEndpoint
from ..models.base import PaginatedResponse
from ..models.renewable import FuelTypeData, GeneratorCapacity, ElectricityGeneration


class ElectricityEndpoint(BaseEndpoint):
    """Endpoint for electricity data including generation and capacity."""

    BASE_ROUTE = "electricity"

    # Sub-routes
    ROUTE_RTO_FUEL_TYPE = "rto/fuel-type-data"
    ROUTE_OPERATING_CAPACITY = "operating-generator-capacity"
    ROUTE_STATE_PROFILES = "state-electricity-profiles"
    ROUTE_FACILITY_FUEL = "facility-fuel"

    def get_fuel_type_generation(
        self,
        fuel_types: Optional[List[str]] = None,
        respondents: Optional[List[str]] = None,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> PaginatedResponse[FuelTypeData]:
        """Get real-time generation data by fuel type.

        Args:
            fuel_types: Filter by fuel type codes (SUN, WND, WAT, etc.).
            respondents: Filter by balancing authority codes.
            frequency: Data frequency (hourly, daily, etc.).
            start: Start datetime (YYYY-MM-DDTHH).
            end: End datetime.
            limit: Max records to return.
            offset: Pagination offset.

        Returns:
            Paginated fuel type generation data.
        """
        facets = {}
        if fuel_types:
            facets["fueltype"] = fuel_types
        if respondents:
            facets["respondent"] = respondents

        route = self._build_route(self.ROUTE_RTO_FUEL_TYPE)
        return self._fetch_data(
            route=route,
            model_cls=FuelTypeData,
            data_columns=["value"],
            facets=facets if facets else None,
            frequency=frequency,
            start=start,
            end=end,
            limit=limit,
            offset=offset,
        )

    def get_all_fuel_type_generation(
        self,
        fuel_types: Optional[List[str]] = None,
        respondents: Optional[List[str]] = None,
        frequency: str = "hourly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        max_records: Optional[int] = None,
    ) -> Generator[FuelTypeData, None, None]:
        """Get all fuel type generation data with pagination.

        Args:
            fuel_types: Filter by fuel type codes.
            respondents: Filter by balancing authority codes.
            frequency: Data frequency.
            start: Start datetime.
            end: End datetime.
            max_records: Maximum records to fetch.

        Yields:
            FuelTypeData instances.
        """
        facets = {}
        if fuel_types:
            facets["fueltype"] = fuel_types
        if respondents:
            facets["respondent"] = respondents

        route = self._build_route(self.ROUTE_RTO_FUEL_TYPE)
        yield from self._fetch_all_data(
            route=route,
            model_cls=FuelTypeData,
            data_columns=["value"],
            facets=facets if facets else None,
            frequency=frequency,
            start=start,
            end=end,
            max_records=max_records,
        )

    # Data columns for capacity endpoint
    CAPACITY_DATA_COLUMNS = [
        "nameplate-capacity-mw",
        "net-summer-capacity-mw",
        "net-winter-capacity-mw",
        "operating-year-month",
        "latitude",
        "longitude",
    ]

    def get_operating_capacity(
        self,
        states: Optional[List[str]] = None,
        energy_sources: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sectors: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> PaginatedResponse[GeneratorCapacity]:
        """Get operating generator capacity data.

        Args:
            states: Filter by state codes (CA, TX, etc.).
            energy_sources: Filter by energy source codes.
            statuses: Filter by status (OP=Operating, etc.).
            sectors: Filter by sector codes.
            limit: Max records to return.
            offset: Pagination offset.

        Returns:
            Paginated generator capacity data.
        """
        facets = {}
        if states:
            facets["stateid"] = states
        if energy_sources:
            facets["energy_source_code"] = energy_sources
        if statuses:
            facets["status"] = statuses
        if sectors:
            facets["sector"] = sectors

        route = self._build_route(self.ROUTE_OPERATING_CAPACITY)
        return self._fetch_data(
            route=route,
            model_cls=GeneratorCapacity,
            data_columns=self.CAPACITY_DATA_COLUMNS,
            facets=facets if facets else None,
            limit=limit,
            offset=offset,
        )

    def get_all_operating_capacity(
        self,
        states: Optional[List[str]] = None,
        energy_sources: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        sectors: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[GeneratorCapacity, None, None]:
        """Get all operating generator capacity with pagination.

        Args:
            states: Filter by state codes.
            energy_sources: Filter by energy source codes.
            statuses: Filter by status.
            sectors: Filter by sector codes.
            max_records: Maximum records to fetch.

        Yields:
            GeneratorCapacity instances.
        """
        facets = {}
        if states:
            facets["stateid"] = states
        if energy_sources:
            facets["energy_source_code"] = energy_sources
        if statuses:
            facets["status"] = statuses
        if sectors:
            facets["sector"] = sectors

        route = self._build_route(self.ROUTE_OPERATING_CAPACITY)
        yield from self._fetch_all_data(
            route=route,
            model_cls=GeneratorCapacity,
            data_columns=self.CAPACITY_DATA_COLUMNS,
            facets=facets if facets else None,
            max_records=max_records,
        )

    def get_facility_fuel_data(
        self,
        plant_ids: Optional[List[str]] = None,
        states: Optional[List[str]] = None,
        fuel_codes: Optional[List[str]] = None,
        frequency: str = "monthly",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get facility-level fuel consumption and generation.

        Args:
            plant_ids: Filter by plant IDs.
            states: Filter by state codes.
            fuel_codes: Filter by fuel codes.
            frequency: Data frequency.
            start: Start date.
            end: End date.
            limit: Max records.
            offset: Pagination offset.

        Returns:
            Raw API response with facility data.
        """
        facets = {}
        if plant_ids:
            facets["plantCode"] = plant_ids
        if states:
            facets["state"] = states
        if fuel_codes:
            facets["fuel2002"] = fuel_codes

        route = self._build_route(self.ROUTE_FACILITY_FUEL)
        return self._client.get_data(
            route=route,
            facets=facets if facets else None,
            frequency=frequency,
            start=start,
            end=end,
            length=limit,
            offset=offset,
        )
