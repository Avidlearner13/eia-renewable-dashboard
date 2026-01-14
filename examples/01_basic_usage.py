"""
Basic usage example for EIA API client.

This script demonstrates how to:
1. Initialize the client
2. Fetch solar and wind generation data
3. Export data to CSV

Before running, set your API key:
    export EIA_API_KEY="your-api-key-here"

Or pass it directly to the client.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eia_client import EIAClient, RenewableEndpoint, export_to_csv


def main():
    # Get API key from environment or use placeholder
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Please set EIA_API_KEY environment variable")
        print("Get your free API key at: https://www.eia.gov/opendata/")
        return

    # Initialize client
    client = EIAClient.from_api_key(api_key)
    renewable = RenewableEndpoint(client)

    print("=" * 60)
    print("EIA Renewable Energy Data - Basic Usage")
    print("=" * 60)

    # 1. Get recent solar generation (hourly data)
    print("\n1. Fetching recent solar generation data...")
    solar_data = renewable.get_solar_generation(
        frequency="hourly",
        limit=100,
    )
    print(f"   Retrieved {len(solar_data.data)} solar generation records")
    print(f"   Total available: {solar_data.total}")

    if solar_data.data:
        sample = solar_data.data[0]
        print(f"   Sample: {sample.period} - {sample.respondent_name}: {sample.value:,.0f} MWh")

    # 2. Get recent wind generation
    print("\n2. Fetching recent wind generation data...")
    wind_data = renewable.get_wind_generation(
        frequency="hourly",
        limit=100,
    )
    print(f"   Retrieved {len(wind_data.data)} wind generation records")

    if wind_data.data:
        sample = wind_data.data[0]
        print(f"   Sample: {sample.period} - {sample.respondent_name}: {sample.value:,.0f} MWh")

    # 3. Get all renewable generation together
    print("\n3. Fetching all renewable generation...")
    all_renewable = renewable.get_all_renewable_generation(
        frequency="hourly",
        limit=100,
    )
    print(f"   Retrieved {len(all_renewable.data)} records (solar, wind, hydro)")

    # 4. Export to CSV
    print("\n4. Exporting solar data to CSV...")
    rows = export_to_csv(
        solar_data.data,
        "output/solar_generation.csv",
        columns=["period", "respondent_name", "fuel_type_description", "value", "units"],
    )
    print(f"   Exported {rows} rows to output/solar_generation.csv")

    print("\n" + "=" * 60)
    print("Done! Check the 'output' directory for exported files.")


if __name__ == "__main__":
    main()
