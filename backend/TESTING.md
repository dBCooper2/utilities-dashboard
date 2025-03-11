# Backend API Testing Guide

This document provides instructions for testing the Utilities Dashboard backend API endpoints, focusing on the data needed for the various dashboard components.

## Prerequisites

- The backend should be deployed and running (locally or on Railway)
- Access to the API base URL (e.g., `http://localhost:8000` or your Railway deployment URL)
- A tool for making API requests (curl, Postman, or Python with requests)

## Base URL

Replace `{BASE_URL}` in the examples below with:
- `http://localhost:8000` for local testing
- Your Railway deployment URL (e.g., `https://utilities-dashboard-production.up.railway.app`) for production testing

## Testing API Endpoints

### 1. Day-Ahead Market Zonal LBMP

#### Required Data:
- State GeoJSON data with zones
- Zone LBMP data
- Zone details

#### API Endpoints to Test:

1. **Get All States:**
   ```
   GET {BASE_URL}/api/energy/states
   ```
   Expected response: List of state codes (e.g., `["NY", "FL", "GA", ...]`)

2. **Get State GeoJSON:**
   ```
   GET {BASE_URL}/api/energy/state-geojson/{state_code}
   ```
   Example: `GET {BASE_URL}/api/energy/state-geojson/FL`
   
   Expected response: GeoJSON data for the specified state

3. **Get Zones by State:**
   ```
   GET {BASE_URL}/api/energy/zones?state={state_code}
   ```
   Example: `GET {BASE_URL}/api/energy/zones?state=FL`
   
   Expected response: List of zones in the specified state

4. **Get LBMP Data for a Zone:**
   ```
   GET {BASE_URL}/api/energy/lbmp/{zone_code}?type=DA&interval=hourly
   ```
   Example: `GET {BASE_URL}/api/energy/lbmp/FRCC?type=DA&interval=hourly`
   
   Parameters:
   - `type`: Set to `DA` for Day Ahead
   - `interval`: Data granularity (15min, hourly, daily)
   - `start_time` and `end_time`: Optional date-time filters (ISO format)
   
   Expected response: Time series of LBMP data for the specified zone

### 2. Real-Time Fuel Mix

#### Required Data:
- Fuel mix data by region or state
- Renewable fuel mix data

#### API Endpoints to Test:

1. **Get Fuel Mix Data:**
   ```
   GET {BASE_URL}/api/energy/fuel-mix?iso_rto={iso_rto}&interval=hourly
   ```
   Example: `GET {BASE_URL}/api/energy/fuel-mix?iso_rto=SERC&interval=hourly`
   
   Parameters:
   - `iso_rto`: ISO/RTO code (SERC, FRCC, PJM, MISO, SPP)
   - `state`: Optional filter by state
   - `start_time` and `end_time`: Optional date-time filters
   - `fuel_types`: Optional filter by fuel types
   - `interval`: Time interval (15min, hourly, daily)
   
   Expected response: Time series of fuel mix data for the specified region/state

2. **Get Renewable Fuel Mix:**
   ```
   GET {BASE_URL}/api/energy/renewable-fuel-mix?iso_rto={iso_rto}&interval=hourly
   ```
   Example: `GET {BASE_URL}/api/energy/renewable-fuel-mix?iso_rto=SERC&interval=hourly`
   
   Parameters: Similar to fuel-mix endpoint, but focuses on renewable sources
   
   Expected response: Time series of renewable fuel mix data

### 3. Interface Data

#### Required Data:
- LBMP, losses, and congestion data for zones

#### API Endpoints to Test:

1. **Get LBMP Data for a Zone (with components):**
   ```
   GET {BASE_URL}/api/energy/lbmp/{zone_code}?type=DA&interval=hourly
   ```
   Example: `GET {BASE_URL}/api/energy/lbmp/FRCC?type=DA&interval=hourly`
   
   Parameters:
   - Include appropriate time range with `start_time` and `end_time`
   
   Expected response: Time series with LBMP, loss, and congestion components

### 4. Load With Losses

#### Required Data:
- Load data for zones, with and without losses

#### API Endpoints to Test:

1. **Get Load Data:**
   ```
   GET {BASE_URL}/api/energy/load/{zone_code}?interval=15min&include_losses=true
   ```
   Example: `GET {BASE_URL}/api/energy/load/FRCC?interval=15min&include_losses=true`
   
   Parameters:
   - `zone_code`: Zone identifier
   - `include_losses`: Set to true to include load with losses
   - `interval`: Time interval (15min, hourly, daily)
   - `start_time` and `end_time`: Optional date-time filters
   
   Expected response: Time series of load data for the specified zone

### 5. Load vs LBMP

#### Required Data:
- Load data for zones
- LBMP data for zones

#### API Endpoints to Test:

1. **Get Load Data:**
   See "Load With Losses" section above

2. **Get LBMP Data:**
   See "Interface Data" section above

### 6. Daily Fuel Mix: Totals

#### Required Data:
- Fuel mix data aggregated by day

#### API Endpoints to Test:

1. **Get Fuel Mix Data (with daily interval):**
   ```
   GET {BASE_URL}/api/energy/fuel-mix?iso_rto={iso_rto}&interval=daily
   ```
   Example: `GET {BASE_URL}/api/energy/fuel-mix?iso_rto=SERC&interval=daily`
   
   Parameters:
   - `interval`: Set to "daily"
   - Other parameters as needed
   
   Expected response: Daily aggregated fuel mix data

### 7. Flow

#### Required Data:
- Interface flow data between regions

#### API Endpoints to Test:

1. **Get Zone Interfaces:**
   ```
   GET {BASE_URL}/api/energy/zone-interfaces
   ```
   
   Expected response: List of interfaces between zones

2. **Get Zone Interface Flow:**
   ```
   GET {BASE_URL}/api/energy/zone-interface-flow/{interface_id}?interval=15min
   ```
   Example: `GET {BASE_URL}/api/energy/zone-interface-flow/1?interval=15min`
   
   Parameters:
   - `interface_id`: ID of the interface
   - `interval`: Time interval (15min, hourly, daily)
   - `start_time` and `end_time`: Optional date-time filters
   
   Expected response: Time series of flow data for the specified interface

3. **Get Zone Interfaces GeoJSON:**
   ```
   GET {BASE_URL}/api/energy/zone-interfaces-geojson
   ```
   
   Expected response: GeoJSON data representing zone interfaces

### 8. Zonal Data

#### Required Data:
- LBMP data for multiple zones

#### API Endpoints to Test:

1. **Get Zones (to identify available zones):**
   ```
   GET {BASE_URL}/api/energy/zones
   ```
   
   Expected response: List of available zones

2. **Get LBMP Data for Multiple Zones:**
   Perform multiple requests to the LBMP endpoint for different zones:
   ```
   GET {BASE_URL}/api/energy/lbmp/{zone_code}?interval=15min
   ```
   
   Expected response: LBMP data for each zone

### 9. Weather Data

#### Required Data:
- Weather forecasts and historical data

#### API Endpoints to Test:

1. **Get Regions (to identify available weather regions):**
   ```
   GET {BASE_URL}/api/weather/regions
   ```
   
   Expected response: List of available weather regions

2. **Get Current Weather:**
   ```
   GET {BASE_URL}/api/weather/current/{region_code}
   ```
   Example: `GET {BASE_URL}/api/weather/current/FL`
   
   Expected response: Current weather data for the specified region

3. **Get Daily Weather:**
   ```
   GET {BASE_URL}/api/weather/daily/{region_code}?start_date=2023-01-01&end_date=2023-01-07
   ```
   
   Expected response: Daily weather data for the specified date range

4. **Get Weather Time Series:**
   ```
   GET {BASE_URL}/api/weather/time-series/{region_code}?interval=15min
   ```
   
   Parameters:
   - `interval`: Time interval (15min, hourly, daily)
   - `start_time` and `end_time`: Optional date-time filters
   
   Expected response: Time series of weather data points

5. **Get Weather Forecast:**
   ```
   GET {BASE_URL}/api/weather/forecast/{region_code}?days=7
   ```
   
   Expected response: Weather forecast for the specified number of days

6. **Get Forecast Comparison:**
   ```
   GET {BASE_URL}/api/weather/comparison/{region_code}?target_date=2023-01-01
   ```
   
   Expected response: Comparison of forecast vs. actual weather for the specified date

## Example Python Script for Testing

Here's a simple Python script to test some of the key endpoints:

```python
import requests
import json
from datetime import datetime, timedelta

# Set your base URL
BASE_URL = "http://localhost:8000"  # or your Railway URL

# Helper function to make requests
def make_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Test state and zone data
states = make_request("/api/energy/states")
print(f"Available states: {states}")

if states and len(states) > 0:
    # Get first state
    state = states[0]
    print(f"\nTesting with state: {state}")
    
    # Get state GeoJSON
    state_geojson = make_request(f"/api/energy/state-geojson/{state}")
    print(f"State GeoJSON received: {state_geojson is not None}")
    
    # Get zones in the state
    zones = make_request(f"/api/energy/zones", {"state": state})
    print(f"Zones in state {state}: {len(zones) if zones else 0}")
    
    if zones and len(zones) > 0:
        # Test with first zone
        zone = zones[0]["code"]
        print(f"\nTesting with zone: {zone}")
        
        # Get LBMP data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=3)
        lbmp_data = make_request(f"/api/energy/lbmp/{zone}", {
            "type": "DA",
            "interval": "hourly",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        print(f"LBMP data points: {len(lbmp_data) if lbmp_data else 0}")
        
        # Get Load data
        load_data = make_request(f"/api/energy/load/{zone}", {
            "interval": "hourly",
            "include_losses": "true",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        })
        print(f"Load data points: {len(load_data) if load_data else 0}")

# Test fuel mix
fuel_mix = make_request("/api/energy/fuel-mix", {
    "iso_rto": "SERC",
    "interval": "daily",
    "start_time": (datetime.now() - timedelta(days=7)).isoformat(),
    "end_time": datetime.now().isoformat()
})
print(f"\nFuel mix data points: {len(fuel_mix) if fuel_mix else 0}")

# Test weather data
regions = make_request("/api/weather/regions")
print(f"\nAvailable weather regions: {len(regions) if regions else 0}")

if regions and len(regions) > 0:
    region = regions[0]["code"]
    print(f"Testing with region: {region}")
    
    # Get forecast
    forecast = make_request(f"/api/weather/forecast/{region}", {"days": 7})
    print(f"Weather forecast days: {len(forecast) if forecast else 0}")
```

## Troubleshooting

If you encounter issues with the API:

1. **Check Server Logs:**
   - If running locally: Check terminal output
   - If on Railway: Check logs in the Railway dashboard

2. **Verify Database Connection:**
   - Ensure database environment variables are correctly set
   - Check if the database is accessible

3. **Initialization Problems:**
   - Verify that the startup event in `main.py` completes successfully
   - Check if sample data was created properly

4. **404 Errors:**
   - Verify the endpoint path is correct
   - Check if the requested resource (zone, region, etc.) exists in the database

5. **Data Range Issues:**
   - If no data is returned, try expanding the time range
   - Some data may only be available for specific date ranges

## Data Refresh

To manually refresh the energy and weather data:

1. **Update Energy Data:**
   ```
   POST {BASE_URL}/api/energy/update
   ```

2. **Update Weather Data:**
   ```
   POST {BASE_URL}/api/weather/update
   ``` 