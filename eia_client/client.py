"""Base EIA API client with authentication and request handling."""

import time
from typing import Any, Dict, List, Optional, Generator
from urllib.parse import urljoin

import requests

from .config import EIAConfig
from .exceptions import (
    EIAAuthenticationError,
    EIADataNotFoundError,
    EIARateLimitError,
    EIARequestError,
)


class EIAClient:
    """Base client for interacting with the EIA API v2."""

    def __init__(self, config: EIAConfig):
        """Initialize the EIA client.

        Args:
            config: EIAConfig instance with API credentials and settings.
        """
        self._config = config
        self._session = requests.Session()
        self._session.params = {"api_key": config.api_key}

    @classmethod
    def from_api_key(cls, api_key: str, **kwargs) -> "EIAClient":
        """Create client from API key directly.

        Args:
            api_key: EIA API key.
            **kwargs: Additional config options.
        """
        config = EIAConfig(api_key=api_key, **kwargs)
        return cls(config)

    @classmethod
    def from_env(cls) -> "EIAClient":
        """Create client from environment variables."""
        config = EIAConfig.from_env()
        return cls(config)

    @property
    def config(self) -> EIAConfig:
        """Get client configuration."""
        return self._config

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for API endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self._config.base_url}/{endpoint}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors.

        Args:
            response: Response from requests.

        Returns:
            Parsed JSON response.

        Raises:
            EIAAuthenticationError: If API key is invalid.
            EIARateLimitError: If rate limit exceeded.
            EIADataNotFoundError: If data not found.
            EIARequestError: For other request errors.
        """
        if response.status_code == 401:
            raise EIAAuthenticationError("Invalid API key")

        if response.status_code == 429:
            raise EIARateLimitError("API rate limit exceeded")

        if response.status_code == 404:
            raise EIADataNotFoundError(f"Data not found: {response.url}")

        if response.status_code >= 400:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"error": response.text}

            raise EIARequestError(
                f"Request failed: {response.status_code}",
                status_code=response.status_code,
                response=error_data,
            )

        return response.json()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            params: Query parameters.
            **kwargs: Additional request arguments.

        Returns:
            Parsed JSON response.
        """
        url = self._build_url(endpoint)
        params = params or {}

        for attempt in range(self._config.max_retries):
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    timeout=self._config.timeout,
                    **kwargs,
                )
                return self._handle_response(response)

            except EIARateLimitError:
                if attempt < self._config.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise

            except requests.RequestException as e:
                if attempt < self._config.max_retries - 1:
                    time.sleep(1)
                else:
                    raise EIARequestError(f"Request failed: {str(e)}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request to API.

        Args:
            endpoint: API endpoint.
            params: Query parameters.

        Returns:
            Parsed JSON response.
        """
        return self._request("GET", endpoint, params=params)

    def get_route_metadata(self, route: str) -> Dict[str, Any]:
        """Get metadata for an API route.

        Args:
            route: API route path (e.g., 'electricity/rto').

        Returns:
            Route metadata including available facets and data columns.
        """
        return self.get(route)

    def get_data(
        self,
        route: str,
        data_columns: Optional[List[str]] = None,
        facets: Optional[Dict[str, List[str]]] = None,
        frequency: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        length: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get data from an API route.

        Args:
            route: API route path (e.g., 'electricity/rto/fuel-type-data').
            data_columns: List of data columns to return.
            facets: Filter facets as {facet_name: [values]}.
            frequency: Data frequency (hourly, daily, monthly, quarterly, annual).
            start: Start date/time.
            end: End date/time.
            sort: Sort order as [{'column': 'name', 'direction': 'asc/desc'}].
            length: Number of records to return (max 5000).
            offset: Offset for pagination.

        Returns:
            Data response with 'data' array and metadata.
        """
        # Use list of tuples to support multiple values for same key
        # Include api_key since list params don't merge with session.params
        params = [("api_key", self._config.api_key)]

        if data_columns:
            for col in data_columns:
                params.append(("data[]", col))

        if facets:
            for facet_name, values in facets.items():
                for value in values:
                    params.append((f"facets[{facet_name}][]", value))

        if frequency:
            params.append(("frequency", frequency))

        if start:
            params.append(("start", start))

        if end:
            params.append(("end", end))

        if sort:
            for i, s in enumerate(sort):
                params.append((f"sort[{i}][column]", s["column"]))
                params.append((f"sort[{i}][direction]", s.get("direction", "desc")))

        if length:
            params.append(("length", min(length, self._config.page_size)))

        if offset:
            params.append(("offset", offset))

        endpoint = f"{route}/data" if not route.endswith("/data") else route
        return self._request("GET", endpoint, params=params)

    def get_all_data(
        self,
        route: str,
        data_columns: Optional[List[str]] = None,
        facets: Optional[Dict[str, List[str]]] = None,
        frequency: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Get all data from an API route with automatic pagination.

        Args:
            route: API route path.
            data_columns: List of data columns to return.
            facets: Filter facets.
            frequency: Data frequency.
            start: Start date/time.
            end: End date/time.
            sort: Sort order.
            max_records: Maximum total records to fetch (None for all).

        Yields:
            Individual data records.
        """
        offset = 0
        total_fetched = 0

        while True:
            response = self.get_data(
                route=route,
                data_columns=data_columns,
                facets=facets,
                frequency=frequency,
                start=start,
                end=end,
                sort=sort,
                length=self._config.page_size,
                offset=offset,
            )

            data = response.get("response", {}).get("data", [])
            if not data:
                break

            for record in data:
                yield record
                total_fetched += 1

                if max_records and total_fetched >= max_records:
                    return

            if len(data) < self._config.page_size:
                break

            offset += len(data)
