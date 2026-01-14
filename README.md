# EIA Renewable Energy Dashboard

Interactive dashboard for visualizing U.S. renewable energy data from the EIA (Energy Information Administration) API.

![Dashboard Preview](https://img.shields.io/badge/React-Leaflet-blue) ![Python](https://img.shields.io/badge/Python-FastAPI-green)

## Features

- **Interactive Map** - Leaflet map with solar/wind generator locations
- **Polygon Selection** - Draw polygons to analyze custom areas
- **Real-time Data** - Live generation data from major grid operators
- **Analytics Charts** - Capacity and generation visualizations
- **Filtering** - Filter by energy source, capacity, state

## Quick Start

### 1. Get Your API Key

Register for a free API key at: https://www.eia.gov/opendata/

### 2. Set Environment Variable

```bash
export EIA_API_KEY="your-api-key-here"
```

### 3. Run the Application

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start backend (terminal 1)
cd backend && python main.py

# Install and start frontend (terminal 2)
cd frontend && npm install && npm run dev
```

### 4. Open Dashboard

Visit http://localhost:5173

## Project Structure

```
├── eia_client/          # Python client for EIA API
│   ├── client.py        # Base API client
│   ├── endpoints/       # API endpoints
│   └── models/          # Data models
├── backend/             # FastAPI server
│   └── main.py          # API endpoints
├── frontend/            # React + Vite dashboard
│   └── src/
│       ├── components/
│       │   ├── Map.jsx          # Leaflet map
│       │   ├── Analytics.jsx    # Charts
│       │   ├── FilterPanel.jsx  # Filters
│       │   └── GeneratorList.jsx
│       └── api.js       # API client
└── examples/            # Python usage examples
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/generators` | Get renewable generators with coordinates |
| `GET /api/generation/realtime` | Real-time generation by region |
| `GET /api/capacity/by-state` | Installed capacity by state |
| `GET /api/analytics/polygon` | Analytics for drawn polygon |

## Python Client Usage

```python
from eia_client import EIAClient, RenewableEndpoint

client = EIAClient.from_api_key("your-api-key")
renewable = RenewableEndpoint(client)

# Get solar generation
solar = renewable.get_solar_generation(frequency="hourly", limit=100)
for record in solar.data:
    print(f"{record.period}: {record.value:,.0f} MWh")

# Get generator capacity
capacity = renewable.get_solar_capacity(states=["CA"], limit=100)
for gen in capacity.data:
    print(f"{gen.plant_name}: {gen.nameplate_capacity_mw} MW")
```

## Data Sources

- **Generation**: Real-time data from RTOs/ISOs (CAISO, ERCOT, PJM, MISO, etc.)
- **Capacity**: EIA-860 generator inventory with coordinates
- **Fuel Types**: Solar (SUN), Wind (WND), Hydro (WAT), Geothermal (GEO)

## Tech Stack

- **Frontend**: React, Vite, Leaflet, Recharts
- **Backend**: Python, FastAPI
- **Data**: U.S. EIA Open Data API

## License

MIT
