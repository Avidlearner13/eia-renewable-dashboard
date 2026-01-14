"""
Time series analysis example.

This script demonstrates how to:
1. Fetch historical generation data
2. Analyze trends over time
3. Compare different renewable sources

Before running, set your API key:
    export EIA_API_KEY="your-api-key-here"
"""

import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eia_client import EIAClient, RenewableEndpoint, export_to_dataframe


def main():
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Please set EIA_API_KEY environment variable")
        return

    client = EIAClient.from_api_key(api_key)
    renewable = RenewableEndpoint(client)

    print("=" * 60)
    print("EIA Renewable Energy - Time Series Analysis")
    print("=" * 60)

    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%dT00")
    end_str = end_date.strftime("%Y-%m-%dT00")

    print(f"\nAnalyzing data from {start_date.date()} to {end_date.date()}")

    # 1. Get daily solar generation
    print("\n1. Fetching daily solar generation...")
    solar_daily = renewable.get_solar_generation(
        frequency="daily",
        start=start_str[:10],  # YYYY-MM-DD for daily
        end=end_str[:10],
        limit=1000,
    )

    # Aggregate by date
    solar_by_date = defaultdict(float)
    for record in solar_daily.data:
        solar_by_date[record.period] += record.value

    print(f"   Retrieved data for {len(solar_by_date)} days")
    for date in sorted(solar_by_date.keys())[-5:]:
        print(f"   {date}: {solar_by_date[date]:>15,.0f} MWh")

    # 2. Get daily wind generation
    print("\n2. Fetching daily wind generation...")
    wind_daily = renewable.get_wind_generation(
        frequency="daily",
        start=start_str[:10],
        end=end_str[:10],
        limit=1000,
    )

    wind_by_date = defaultdict(float)
    for record in wind_daily.data:
        wind_by_date[record.period] += record.value

    print(f"   Retrieved data for {len(wind_by_date)} days")
    for date in sorted(wind_by_date.keys())[-5:]:
        print(f"   {date}: {wind_by_date[date]:>15,.0f} MWh")

    # 3. Compare sources
    print("\n3. Solar vs Wind comparison (last 5 days):")
    print("   Date       |      Solar (MWh) |       Wind (MWh) | Wind/Solar")
    print("   " + "-" * 65)

    for date in sorted(set(solar_by_date.keys()) & set(wind_by_date.keys()))[-5:]:
        solar = solar_by_date[date]
        wind = wind_by_date[date]
        ratio = wind / solar if solar > 0 else 0
        print(f"   {date} | {solar:>16,.0f} | {wind:>16,.0f} | {ratio:>10.2f}")

    # 4. Export to pandas DataFrame (if available)
    print("\n4. Exporting to DataFrame...")
    try:
        df = export_to_dataframe(solar_daily.data)
        print(f"   Created DataFrame with {len(df)} rows")
        print(f"   Columns: {list(df.columns)}")

        # Save to CSV
        df.to_csv("output/solar_timeseries.csv", index=False)
        print("   Saved to output/solar_timeseries.csv")

    except ImportError:
        print("   pandas not installed - skipping DataFrame export")
        print("   Install with: pip install pandas")

    print("\n" + "=" * 60)
    print("Time series analysis complete!")


if __name__ == "__main__":
    main()
