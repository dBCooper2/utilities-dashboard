import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import json
import math

# Load environment variables
load_dotenv()

# Custom JSON encoder to handle NaN and Infinity values
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj):
                return None
            if math.isinf(obj):
                return None
        return super().default(obj)

# Create FastAPI app
app = FastAPI(
    title="Energy Dashboard API",
    description="API for the Southeastern US Energy Dashboard",
    version="1.0.0"
)

# Override the default JSONResponse to use our custom encoder
@app.middleware("http")
async def replace_nan_with_none(request, call_next):
    response = await call_next(request)
    if isinstance(response, JSONResponse):
        response_body = json.loads(response.body)
        # Use the custom encoder to handle NaN and Infinity values
        fixed_body = json.dumps(response_body, cls=CustomJSONEncoder)
        return JSONResponse(
            content=json.loads(fixed_body),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=response.background
        )
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.weather import router as weather_router
from app.api.energy import router as energy_router

app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])
app.include_router(energy_router, prefix="/api/energy", tags=["Energy"])

# Import database initialization functions
from app.db.database import SessionLocal
from app.utils.init_db import init_db, import_southeast_zones, create_sample_regions, create_sample_weather_data, create_sample_energy_data, create_sample_zone_interfaces, create_sample_zone_interface_flow
from app.etl.scheduler import start_scheduler, run_initial_data_load

@app.get("/")
async def root():
    return {"message": "Energy Dashboard API is running"}

@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup"""
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    try:
        # Import southeastern zones from GeoJSON
        import_southeast_zones(db)
        
        # Create sample regions if needed
        create_sample_regions(db)
        
        # Create sample data for testing
        # Note: Each sample data creation function already checks
        # if data exists before creating new data
        create_sample_weather_data(db)
        create_sample_energy_data(db)
        
        # Create sample zone interfaces and flow data
        create_sample_zone_interfaces(db)
        create_sample_zone_interface_flow(db)
    finally:
        db.close()
    
    # Start the scheduler
    scheduler = start_scheduler()
    
    # Run initial data load in the background if needed
    # This will only fetch real data if the database is empty or data is stale
    run_initial_data_load()

# Run the application using Uvicorn when script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 