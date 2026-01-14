"""Export utilities for EIA data."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from ..models.base import BaseModel


def export_to_csv(
    data: Iterable[Union[BaseModel, Dict[str, Any]]],
    filepath: Union[str, Path],
    columns: Optional[List[str]] = None,
    include_header: bool = True,
) -> int:
    """Export data to CSV file.

    Args:
        data: Iterable of model instances or dictionaries.
        filepath: Output file path.
        columns: Specific columns to include (None for all).
        include_header: Whether to include header row.

    Returns:
        Number of rows written.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    fieldnames = None

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = None

        for item in data:
            if isinstance(item, BaseModel):
                row = item.to_dict()
            else:
                row = item

            if columns:
                row = {k: v for k, v in row.items() if k in columns}

            if writer is None:
                fieldnames = list(row.keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if include_header:
                    writer.writeheader()

            writer.writerow(row)
            rows_written += 1

    return rows_written


def export_to_json(
    data: Iterable[Union[BaseModel, Dict[str, Any]]],
    filepath: Union[str, Path],
    indent: int = 2,
) -> int:
    """Export data to JSON file.

    Args:
        data: Iterable of model instances or dictionaries.
        filepath: Output file path.
        indent: JSON indentation level.

    Returns:
        Number of records written.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for item in data:
        if isinstance(item, BaseModel):
            records.append(item.to_dict())
        else:
            records.append(item)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=indent, default=str)

    return len(records)


def export_to_dataframe(
    data: Iterable[Union[BaseModel, Dict[str, Any]]],
):
    """Export data to pandas DataFrame.

    Args:
        data: Iterable of model instances or dictionaries.

    Returns:
        pandas DataFrame.

    Raises:
        ImportError: If pandas is not installed.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for DataFrame export. Install with: pip install pandas")

    records = []
    for item in data:
        if isinstance(item, BaseModel):
            records.append(item.to_dict())
        else:
            records.append(item)

    return pd.DataFrame(records)
