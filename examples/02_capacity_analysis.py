"""
Renewable capacity analysis example.

This script demonstrates how to:
1. Fetch generator capacity data
2. Analyze capacity by state
3. Filter by specific renewable types

Before running, set your API key:
    export EIA_API_KEY="your-api-key-here"
"""

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eia_client import EIAClient, RenewableEndpoint, export_to_csv, collect_all


def main():
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Please set EIA_API_KEY environment variable")
        return

    client = EIAClient.from_api_key(api_key)
    renewable = RenewableEndpoint(client)

    print("=" * 60)
    print("EIA Renewable Energy - Capacity Analysis")
    print("=" * 60)

    # 1. Get solar capacity for specific states
    print("\n1. Solar capacity in California, Texas, and Florida...")
    states = ["CA", "TX", "FL"]

    for state in states:
        solar_cap = renewable.get_solar_capacity(states=[state], limit=5000)
        total_mw = sum(g.nameplate_capacity_mw for g in solar_cap.data)
        print(f"   {state}: {total_mw:,.0f} MW ({len(solar_cap.data)} generators)")

    # 2. Get wind capacity
    print("\n2. Wind capacity in top wind states...")
    wind_states = ["TX", "IA", "OK", "KS"]

    for state in wind_states:
        wind_cap = renewable.get_wind_capacity(states=[state], limit=5000)
        total_mw = sum(g.nameplate_capacity_mw for g in wind_cap.data)
        print(f"   {state}: {total_mw:,.0f} MW ({len(wind_cap.data)} generators)")

    # 3. Aggregate capacity summary (limited for demo)
    print("\n3. State renewable capacity summary (sample)...")
    print("   (Fetching data - this may take a moment...)")

    # Get a sample of renewable generators
    generators = list(renewable.get_all_renewable_capacity(
        states=["CA", "TX"],
        max_records=1000,
    ))

    # Aggregate by state and source
    state_totals = defaultdict(lambda: defaultdict(float))
    for gen in generators:
        state_totals[gen.state][gen.energy_source] += gen.nameplate_capacity_mw
        state_totals[gen.state]["total"] += gen.nameplate_capacity_mw

    print("\n   State | Solar (MW) | Wind (MW) | Total (MW)")
    print("   " + "-" * 50)
    for state in sorted(state_totals.keys()):
        data = state_totals[state]
        solar = data.get("SUN", 0)
        wind = data.get("WND", 0)
        total = data.get("total", 0)
        print(f"   {state:5} | {solar:>10,.0f} | {wind:>9,.0f} | {total:>10,.0f}")

    # 4. Export detailed generator data
    print("\n4. Exporting generator details to CSV...")
    rows = export_to_csv(
        generators,
        "output/renewable_generators.csv",
        columns=[
            "state", "plant_name", "technology", "energy_source",
            "nameplate_capacity_mw", "operating_year", "latitude", "longitude"
        ],
    )
    print(f"   Exported {rows} generators to output/renewable_generators.csv")

    print("\n" + "=" * 60)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
