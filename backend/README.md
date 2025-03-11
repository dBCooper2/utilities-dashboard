# Energy Dashboard Backend

This is the backend API for the Southeastern US Energy Dashboard. It provides data for weather and energy metrics in the southeastern United States.

## Features

- Weather data from Meteostat
- Energy data from EIA API
- TimescaleDB for time-series data
- Daily data updates
- RESTful API with FastAPI

## Setup Options

You can set up the backend using either a local Python environment or Docker (recommended).

### Option 1: Docker Setup (Recommended)

The Docker setup is recommended for consistent development and easier deployment to Railway.

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Running with Docker Compose

1. Make sure you're in the root directory of the project

2. Set your EIA API key as an environment variable:
   ```bash
   export EIA_API_KEY=your_eia_api_key
   ```
   
   Alternatively, create a `.env` file in the project root with:
   ```
   EIA_API_KEY=your_eia_api_key
   ```

3. Start the services:
   ```bash
   docker-compose up
   ```

   This will:
   - Start a PostgreSQL database with TimescaleDB
   - Build and start the backend API
   - Set up the database tables and initial sample data
   - The API will be available at http://localhost:8000

4. To stop the services:
   ```bash
   docker-compose down
   ```

5. If you want to remove all data and start fresh:
   ```bash
   docker-compose down -v
   ```

#### Initial Data Ingestion

The application will automatically create tables and some sample data on startup. To manually trigger data ingestion:

1. With the containers running, access the API's data ingestion endpoints:
   ```bash
   curl -X POST http://localhost:8000/api/weather/update
   curl -X POST http://localhost:8000/api/energy/update
   ```

2. Or you can execute commands inside the container:
   ```bash
   # Access the container shell
   docker-compose exec backend bash
   
   # Then run Python commands
   python -c "from app.db.database import SessionLocal; from app.etl.weather import update_weather_data; db = SessionLocal(); update_weather_data(db); db.close()"
   python -c "from app.db.database import SessionLocal; from app.etl.energy import update_energy_data; db = SessionLocal(); update_energy_data(db); db.close()"
   ```

#### Testing the API

1. Check if the API is running:
   ```bash
   curl http://localhost:8000/
   ```
   
2. Test specific endpoints:
   ```bash
   # Get all regions
   curl http://localhost:8000/api/weather/regions
   
   # Get all zones
   curl http://localhost:8000/api/energy/zones
   ```

3. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Local Setup

If you prefer to run without Docker, you can follow these steps:

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

Create a `.env` file in the backend directory with the following variables:

```
# Database connection settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_dashboard
DB_USER=postgres
DB_PASSWORD=postgres

# API Keys
EIA_API_KEY=your_eia_api_key

# TimescaleDB Settings
TIMESCALE_ENABLED=True
CHUNK_TIME_INTERVAL=1 day

# ETL Settings
FETCH_DAYS_BACK=30
FORECAST_DAYS=7
LOG_LEVEL=INFO
```

4. Create the PostgreSQL database:

```bash
createdb energy_dashboard
```

5. Install TimescaleDB extension:

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
```

## Running the API

### With Docker
```bash
docker-compose up
```

### Without Docker
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Weather API

- `GET /api/weather/regions` - Get all regions
- `GET /api/weather/current/{region_code}` - Get current weather for a region
- `GET /api/weather/daily/{region_code}` - Get daily weather for a region
- `GET /api/weather/time-series/{region_code}` - Get weather time series for a region
- `GET /api/weather/forecast/{region_code}` - Get weather forecast for a region
- `GET /api/weather/comparison/{region_code}` - Compare forecast with actual weather
- `POST /api/weather/update` - Trigger weather data update (for manual ingestion)

### Energy API

- `GET /api/energy/zones` - Get all zones
- `GET /api/energy/zone/{zone_code}` - Get details for a specific zone
- `GET /api/energy/lbmp/{zone_code}` - Get LBMP data for a zone
- `GET /api/energy/load/{zone_code}` - Get load data for a zone
- `GET /api/energy/fuel-mix` - Get fuel mix data
- `GET /api/energy/interface-flow` - Get interface flow data between regions
- `POST /api/energy/update` - Trigger energy data update (for manual ingestion)

## Development Notes

### Checking Logs

To view logs in Docker:
```bash
docker-compose logs -f backend
```

### Debugging

To access a shell in the container:
```bash
docker-compose exec backend bash
```

### Database Access

To connect to the database:
```bash
# With Docker
docker-compose exec timescaledb psql -U postgres -d energy_dashboard

# Without Docker
psql -U postgres -d energy_dashboard
```

## Data Sources

- Weather data: [Meteostat](https://meteostat.net/)
- Energy data: [EIA API](https://www.eia.gov/opendata/) 