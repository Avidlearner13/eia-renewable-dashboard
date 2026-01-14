"""Pagination utilities for EIA API."""

from typing import Callable, Generator, List, TypeVar, Any

T = TypeVar("T")


def paginate(
    fetch_func: Callable[..., Any],
    page_size: int = 5000,
    max_records: int = None,
    **kwargs,
) -> Generator[Any, None, None]:
    """Generic pagination helper.

    Args:
        fetch_func: Function that accepts offset and limit parameters.
        page_size: Number of records per page.
        max_records: Maximum total records to fetch.
        **kwargs: Additional arguments to pass to fetch_func.

    Yields:
        Individual records from each page.
    """
    offset = 0
    total_fetched = 0

    while True:
        response = fetch_func(offset=offset, limit=page_size, **kwargs)

        # Handle both PaginatedResponse and raw dict responses
        if hasattr(response, "data"):
            data = response.data
            has_more = response.has_more
        else:
            data = response.get("response", {}).get("data", [])
            total = response.get("response", {}).get("total", 0)
            has_more = offset + len(data) < total

        if not data:
            break

        for item in data:
            yield item
            total_fetched += 1

            if max_records and total_fetched >= max_records:
                return

        if not has_more or len(data) < page_size:
            break

        offset += len(data)


def collect_all(
    generator: Generator[T, None, None],
    max_items: int = None,
) -> List[T]:
    """Collect all items from a generator into a list.

    Args:
        generator: Generator to collect from.
        max_items: Maximum items to collect.

    Returns:
        List of collected items.
    """
    items = []
    for item in generator:
        items.append(item)
        if max_items and len(items) >= max_items:
            break
    return items


class BatchProcessor:
    """Process large datasets in batches."""

    def __init__(self, batch_size: int = 1000):
        """Initialize batch processor.

        Args:
            batch_size: Number of items per batch.
        """
        self.batch_size = batch_size

    def process(
        self,
        data: Generator[T, None, None],
        processor: Callable[[List[T]], None],
    ) -> int:
        """Process data in batches.

        Args:
            data: Generator of data items.
            processor: Function to process each batch.

        Returns:
            Total number of items processed.
        """
        batch = []
        total = 0

        for item in data:
            batch.append(item)

            if len(batch) >= self.batch_size:
                processor(batch)
                total += len(batch)
                batch = []

        if batch:
            processor(batch)
            total += len(batch)

        return total
