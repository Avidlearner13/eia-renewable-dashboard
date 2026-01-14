"""FastAPI backend for EIA Renewable Energy Dashboard."""

import os
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for eia_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from eia_client import EIAClient, RenewableEndpoint

# Initialize API
app = FastAPI(
    title="EIA Renewable Energy API",
    description="API for renewable energy data visualization",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# EIA Client - Get API key from environment variable
API_KEY = os.getenv("EIA_API_KEY")
if not API_KEY:
    raise ValueError("EIA_API_KEY environment variable is required. Get one at https://www.eia.gov/opendata/")

client = EIAClient.from_api_key(API_KEY)
renewable = RenewableEndpoint(client)


# Response Models
class Generator(BaseModel):
    id: str
    name: str
    state: str
    technology: str
    energy_source: str
    capacity_mw: float
    lat: Optional[float]
    lon: Optional[float]
    operating_year: Optional[int]


class GenerationData(BaseModel):
    period: str
    region: str
    region_name: str
    fuel_type: str
    value: float


class RegionSummary(BaseModel):
    region: str
    region_name: str
    solar_mwh: float
    wind_mwh: float
    hydro_mwh: float
    total_mwh: float


class StateCapacity(BaseModel):
    state: str
    solar_mw: float
    wind_mw: float
    total_mw: float
    generator_count: int


# Routes
@app.get("/")
def root():
    return {"status": "ok", "message": "EIA Renewable Energy API"}


@app.get("/api/generators", response_model=List[Generator])
def get_generators(
    states: Optional[str] = Query(None, description="Comma-separated state codes (CA,TX,FL)"),
    energy_source: Optional[str] = Query(None, description="Energy source (SUN, WND, WAT)"),
    min_capacity: float = Query(0, description="Minimum capacity in MW"),
    limit: int = Query(500, description="Max records to return"),
):
    """Get renewable generators with location data."""
    state_list = states.split(",") if states else None
    source_list = [energy_source] if energy_source else ["SUN", "WND", "WAT"]

    generators = []

    for source in source_list:
        try:
            if source == "SUN":
                data = renewable.get_solar_capacity(states=state_list, limit=limit)
            elif source == "WND":
                data = renewable.get_wind_capacity(states=state_list, limit=limit)
            else:
                # For hydro/other, use electricity endpoint directly
                data = renewable._electricity.get_operating_capacity(
                    states=state_list,
                    energy_sources=[source],
                    statuses=["OP"],
                    limit=limit,
                )

            for g in data.data:
                if g.nameplate_capacity_mw >= min_capacity and g.latitude and g.longitude:
                    generators.append(Generator(
                        id=f"{g.plant_id}-{g.generator_id}",
                        name=g.plant_name,
                        state=g.state,
                        technology=g.technology,
                        energy_source=g.energy_source,
                        capacity_mw=g.nameplate_capacity_mw,
                        lat=g.latitude,
                        lon=g.longitude,
                        operating_year=g.operating_year,
                    ))
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    return generators


@app.get("/api/generators/bounds")
def get_generators_in_bounds(
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    min_lon: float = Query(..., description="Minimum longitude"),
    max_lon: float = Query(..., description="Maximum longitude"),
    energy_source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(1000),
):
    """Get generators within geographic bounds."""
    # Get generators for relevant states based on bounds
    # This is a simplified approach - in production you'd use a spatial database

    # Map bounds to likely states (rough approximation)
    all_states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    source_list = [energy_source] if energy_source else ["SUN", "WND"]
    generators = []

    for source in source_list:
        try:
            if source == "SUN":
                data = renewable.get_solar_capacity(limit=limit)
            else:
                data = renewable.get_wind_capacity(limit=limit)

            for g in data.data:
                if (g.latitude and g.longitude and
                    min_lat <= g.latitude <= max_lat and
                    min_lon <= g.longitude <= max_lon and
                    g.nameplate_capacity_mw > 0):
                    generators.append({
                        "id": f"{g.plant_id}-{g.generator_id}",
                        "name": g.plant_name,
                        "state": g.state,
                        "technology": g.technology,
                        "energy_source": g.energy_source,
                        "capacity_mw": g.nameplate_capacity_mw,
                        "lat": g.latitude,
                        "lon": g.longitude,
                        "operating_year": g.operating_year,
                    })
        except Exception as e:
            print(f"Error: {e}")

    return generators


@app.get("/api/generation/realtime")
def get_realtime_generation(
    regions: Optional[str] = Query(None, description="Comma-separated region codes"),
):
    """Get real-time generation by region."""
    region_list = regions.split(",") if regions else ["CISO", "ERCO", "PJM", "MISO", "NYIS", "ISNE"]

    results = []
    for region in region_list:
        try:
            solar = renewable.get_solar_generation(respondents=[region], limit=1)
            wind = renewable.get_wind_generation(respondents=[region], limit=1)

            solar_val = solar.data[0].value if solar.data else 0
            wind_val = wind.data[0].value if wind.data else 0
            solar_name = solar.data[0].respondent_name if solar.data else region

            results.append(RegionSummary(
                region=region,
                region_name=solar_name,
                solar_mwh=solar_val,
                wind_mwh=wind_val,
                hydro_mwh=0,  # Would need separate call
                total_mwh=solar_val + wind_val,
            ))
        except Exception as e:
            print(f"Error for {region}: {e}")

    return results


@app.get("/api/capacity/by-state")
def get_capacity_by_state(
    states: Optional[str] = Query(None, description="Comma-separated state codes"),
):
    """Get installed capacity by state."""
    state_list = states.split(",") if states else ["CA", "TX", "FL", "AZ", "NC", "NV"]

    results = []
    for state in state_list:
        try:
            solar = renewable.get_solar_capacity(states=[state], limit=500)
            wind = renewable.get_wind_capacity(states=[state], limit=500)

            solar_mw = sum(g.nameplate_capacity_mw for g in solar.data)
            wind_mw = sum(g.nameplate_capacity_mw for g in wind.data)

            results.append(StateCapacity(
                state=state,
                solar_mw=solar_mw,
                wind_mw=wind_mw,
                total_mw=solar_mw + wind_mw,
                generator_count=len(solar.data) + len(wind.data),
            ))
        except Exception as e:
            print(f"Error for {state}: {e}")

    return results


@app.get("/api/analytics/polygon")
def get_polygon_analytics(
    coordinates: str = Query(..., description="JSON array of [lat,lon] coordinates"),
):
    """Get analytics for generators within a polygon."""
    import json

    try:
        coords = json.loads(coordinates)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid coordinates JSON")

    # Get bounding box of polygon
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Get generators in bounding box
    generators = get_generators_in_bounds(
        min_lat=min_lat, max_lat=max_lat,
        min_lon=min_lon, max_lon=max_lon,
        limit=2000,
    )

    # Filter to those actually in polygon
    def point_in_polygon(lat, lon, polygon):
        """Ray casting algorithm for point in polygon."""
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            if ((polygon[i][0] > lat) != (polygon[j][0] > lat) and
                lon < (polygon[j][1] - polygon[i][1]) * (lat - polygon[i][0]) /
                      (polygon[j][0] - polygon[i][0]) + polygon[i][1]):
                inside = not inside
            j = i
        return inside

    filtered = [g for g in generators if point_in_polygon(g["lat"], g["lon"], coords)]

    # Calculate analytics
    solar_generators = [g for g in filtered if g["energy_source"] == "SUN"]
    wind_generators = [g for g in filtered if g["energy_source"] == "WND"]

    return {
        "total_generators": len(filtered),
        "solar_count": len(solar_generators),
        "wind_count": len(wind_generators),
        "solar_capacity_mw": sum(g["capacity_mw"] for g in solar_generators),
        "wind_capacity_mw": sum(g["capacity_mw"] for g in wind_generators),
        "total_capacity_mw": sum(g["capacity_mw"] for g in filtered),
        "generators": filtered[:100],  # Return first 100 for display
        "states": list(set(g["state"] for g in filtered)),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
