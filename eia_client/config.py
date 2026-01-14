"""Configuration management for EIA API client."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EIAConfig:
    """Configuration for EIA API client."""

    api_key: str
    base_url: str = "https://api.eia.gov/v2"
    timeout: int = 30
    max_retries: int = 3
    page_size: int = 5000  # EIA API max is 5000

    @classmethod
    def from_env(cls) -> "EIAConfig":
        """Create config from environment variables."""
        api_key = os.getenv("EIA_API_KEY")
        if not api_key:
            raise ValueError("EIA_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            base_url=os.getenv("EIA_BASE_URL", "https://api.eia.gov/v2"),
            timeout=int(os.getenv("EIA_TIMEOUT", "30")),
            max_retries=int(os.getenv("EIA_MAX_RETRIES", "3")),
            page_size=int(os.getenv("EIA_PAGE_SIZE", "5000")),
        )
