"""Base data models for EIA API responses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar("T")


class BaseModel(ABC):
    """Base model with common functionality (not a dataclass to avoid inheritance issues)."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create instance from dictionary."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        pass


@dataclass
class PaginatedResponse(Generic[T]):
    """Paginated API response wrapper."""

    data: List[T]
    total: int
    offset: int
    page_size: int
    request_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_more(self) -> bool:
        """Check if more pages are available."""
        return self.offset + len(self.data) < self.total

    @property
    def next_offset(self) -> int:
        """Get offset for next page."""
        return self.offset + len(self.data)


@dataclass
class ResponseMetadata:
    """Metadata from API response."""

    request_id: Optional[str] = None
    command: Optional[str] = None
    total_records: int = 0
    date_format: Optional[str] = None
    frequency: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "ResponseMetadata":
        """Parse metadata from API response."""
        resp = response.get("response", {})
        return cls(
            request_id=response.get("request", {}).get("command"),
            total_records=resp.get("total", 0),
            date_format=resp.get("dateFormat"),
            frequency=resp.get("frequency"),
            description=resp.get("description"),
        )
