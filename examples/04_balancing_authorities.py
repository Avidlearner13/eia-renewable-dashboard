"""
Balancing authority analysis example.

This script demonstrates how to:
1. List available balancing authorities (RTOs/ISOs)
2. Compare renewable generation across regions
3. Analyze specific balancing authorities

Balancing Authorities include:
- CAISO (California ISO)
- ERCOT (Texas)
- PJM (Mid-Atlantic)
- MISO (Midwest)
- And many more...

Before running, set your API key:
    export EIA_API_KEY="your-api-key-here"
"""

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eia_client import EIAClient, RenewableEndpoint


def main():
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Please set EIA_API_KEY environment variable")
        return

    client = EIAClient.from_api_key(api_key)
    renewable = RenewableEndpoint(client)

    print("=" * 60)
    print("EIA Renewable Energy - Balancing Authority Analysis")
    print("=" * 60)

    # 1. Get available balancing authorities
    print("\n1. Available Balancing Authorities:")
    bas = renewable.get_balancing_authorities()

    # Show first 10
    print(f"   Found {len(bas)} balancing authorities")
    print("\n   Code    | Name")
    print("   " + "-" * 50)
    for ba in bas[:15]:
        name = ba.get("name", ba.get("id", "Unknown"))
        code = ba.get("id", "")
        print(f"   {code:<8} | {name[:45]}")
    print("   ...")

    # 2. Get available fuel types
    print("\n2. Available Fuel Types:")
    fuel_types = renewable.get_fuel_types()

    print("   Code | Description")
    print("   " + "-" * 40)
    for ft in fuel_types:
        code = ft.get("id", "")
        name = ft.get("name", "Unknown")
        print(f"   {code:<5} | {name}")

    # 3. Compare major ISOs
    print("\n3. Renewable generation by major ISO (recent data):")

    major_isos = ["CISO", "ERCO", "PJM", "MISO", "NYIS", "ISNE"]

    print("\n   ISO    | Solar (MWh)    | Wind (MWh)     | Total Renewable")
    print("   " + "-" * 65)

    for iso in major_isos:
        try:
            # Get solar
            solar = renewable.get_solar_generation(
                respondents=[iso],
                frequency="hourly",
                limit=24,  # Last 24 hours
            )
            solar_total = sum(r.value for r in solar.data)

            # Get wind
            wind = renewable.get_wind_generation(
                respondents=[iso],
                frequency="hourly",
                limit=24,
            )
            wind_total = sum(r.value for r in wind.data)

            total = solar_total + wind_total
            print(f"   {iso:<7}| {solar_total:>14,.0f} | {wind_total:>14,.0f} | {total:>15,.0f}")

        except Exception as e:
            print(f"   {iso:<7}| Error: {str(e)[:40]}")

    # 4. Detailed look at CAISO
    print("\n4. CAISO (California) renewable breakdown:")
    all_renewable = renewable.get_all_renewable_generation(
        respondents=["CISO"],
        frequency="hourly",
        limit=100,
    )

    by_type = defaultdict(float)
    for record in all_renewable.data:
        by_type[record.fuel_type_description] += record.value

    print("\n   Fuel Type              | Generation (MWh)")
    print("   " + "-" * 45)
    for fuel_type, value in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"   {fuel_type:<24} | {value:>15,.0f}")

    print("\n" + "=" * 60)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
