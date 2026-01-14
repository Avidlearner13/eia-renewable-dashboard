"""Base endpoint class for EIA API routes."""

from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Generator, TypeVar, Type

if TYPE_CHECKING:
    from ..client import EIAClient

from ..models.base import BaseModel, PaginatedResponse, ResponseMetadata

T = TypeVar("T", bound=BaseModel)


class BaseEndpoint(ABC):
    """Base class for API endpoints following Open/Closed principle."""

    BASE_ROUTE: str = ""

    def __init__(self, client: "EIAClient"):
        """Initialize endpoint with client.

        Args:
            client: EIA API client instance.
        """
        self._client = client

    @property
    def client(self) -> "EIAClient":
        """Get the API client."""
        return self._client

    def _build_route(self, *parts: str) -> str:
        """Build route from parts."""
        route_parts = [self.BASE_ROUTE] + list(parts)
        return "/".join(p.strip("/") for p in route_parts if p)

    def get_metadata(self, sub_route: str = "") -> Dict[str, Any]:
        """Get metadata for this endpoint.

        Args:
            sub_route: Optional sub-route to get metadata for.

        Returns:
            Endpoint metadata including available facets and data columns.
        """
        route = self._build_route(sub_route)
        return self._client.get_route_metadata(route)

    def get_facets(self, sub_route: str = "") -> Dict[str, Any]:
        """Get available facets for filtering.

        Args:
            sub_route: Optional sub-route.

        Returns:
            Available facets with their possible values.
        """
        metadata = self.get_metadata(sub_route)
        return metadata.get("response", {}).get("facets", {})

    def _fetch_data(
        self,
        route: str,
        model_cls: Type[T],
        data_columns: Optional[List[str]] = None,
        facets: Optional[Dict[str, List[str]]] = None,
        frequency: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> PaginatedResponse[T]:
        """Fetch data with model conversion.

        Args:
            route: API route.
            model_cls: Model class to convert results to.
            data_columns: Data columns to return.
            facets: Filter facets.
            frequency: Data frequency.
            start: Start date.
            end: End date.
            sort: Sort order.
            limit: Max records.
            offset: Pagination offset.

        Returns:
            Paginated response with model instances.
        """
        response = self._client.get_data(
            route=route,
            data_columns=data_columns,
            facets=facets,
            frequency=frequency,
            start=start,
            end=end,
            sort=sort,
            length=limit,
            offset=offset,
        )

        resp_data = response.get("response", {})
        raw_data = resp_data.get("data", [])
        total = resp_data.get("total", len(raw_data))

        models = [model_cls.from_dict(item) for item in raw_data]

        return PaginatedResponse(
            data=models,
            total=total,
            offset=offset,
            page_size=len(raw_data),
            request_info=response.get("request", {}),
        )

    def _fetch_all_data(
        self,
        route: str,
        model_cls: Type[T],
        data_columns: Optional[List[str]] = None,
        facets: Optional[Dict[str, List[str]]] = None,
        frequency: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        max_records: Optional[int] = None,
    ) -> Generator[T, None, None]:
        """Fetch all data with automatic pagination.

        Args:
            route: API route.
            model_cls: Model class.
            data_columns: Data columns.
            facets: Filter facets.
            frequency: Data frequency.
            start: Start date.
            end: End date.
            sort: Sort order.
            max_records: Maximum records to fetch.

        Yields:
            Model instances.
        """
        for record in self._client.get_all_data(
            route=route,
            data_columns=data_columns,
            facets=facets,
            frequency=frequency,
            start=start,
            end=end,
            sort=sort,
            max_records=max_records,
        ):
            yield model_cls.from_dict(record)
