# Utilities Dashboard

This is a dashboard for monitoring energy utilities across the southeastern United States.

## Pre-generated GeoJSON Files

To improve performance and reliability, we've pre-generated GeoJSON files that are stored in the frontend's public directory:

### Available GeoJSON Files

- `frontend/public/geojson/southeast_zones.geojson` - The entire southeast region with all zones and state boundaries
- `frontend/public/geojson/zone_interfaces.geojson` - All zone interfaces with connection lines
- `frontend/public/geojson/fl_zones.geojson` - Florida with its zones
- `frontend/public/geojson/nc_zones.geojson` - North Carolina with its zones
- `frontend/public/geojson/sc_zones.geojson` - South Carolina with its zones
- And more for each state in the southeast

### How to Access the GeoJSON Files

In your frontend code, you can access these files directly through fetch:

```javascript
// Example: Loading the southeast region data
fetch('/geojson/southeast_zones.geojson')
  .then(response => response.json())
  .then(data => {
    // Process the GeoJSON data
    console.log(data);
  });
```

### Regenerating the GeoJSON Files

If you need to update the GeoJSON files, you can run the generate script:

```
python3 create_geojson_files.py
```

This will reprocess the source GeoJSON data and update all files in the frontend's public directory.

## Backend API Status and Alternative Data Access

The backend API service is currently experiencing stability issues and is being fixed. In the meantime, we've set up a simple HTTP server to serve the GeoJSON data for zone interfaces.

### Running the GeoJSON Server

1. Make sure the GeoJSON file is available in the root directory:
   ```
   zone_interfaces.geojson
   ```

2. Run the Python server script:
   ```
   python3 serve_geojson.py
   ```

3. The GeoJSON data will be available at:
   ```
   http://localhost:8080/geojson
   ```

## Docker Services

The application consists of two main Docker services:

1. **Backend API** - A FastAPI service running on port 8000
2. **TimescaleDB** - A PostgreSQL database with TimescaleDB extension for time-series data

To run the services:

```
docker-compose up -d
```

## Troubleshooting

If you encounter connection issues with the backend API, use the alternative GeoJSON server as described above.

The data has been pre-generated and saved to a file, so it can be used directly without requiring the backend API to be operational. 