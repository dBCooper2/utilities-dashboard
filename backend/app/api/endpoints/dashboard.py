from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import logging
import traceback
from app.db.session import get_db
from app.services.ski_resort_service import SkiResortService
from app.services.eia_service import EIAService
from app.services.meteostat_service import MeteostatService
from app.services.iea_service import IEAService
from app.schemas.dashboard import DashboardResponse, ResortEnergyData
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def map_resort_to_region(resort):
    """Map a resort to its energy market region based on location"""
    # Simple mapping based on country/coordinates
    country = resort.get("country", "US")
    lat = resort.get("latitude", 0)
    lon = resort.get("longitude", 0)
    
    if country == "US":
        if lon < -100:
            return "US_WEST"
        elif lon > -80:
            return "US_EAST"
        else:
            return "US_CENTRAL"
    elif country in ["FR", "CH", "AT", "IT"]:
        return "EU_ALPINE"
    elif country in ["SE", "NO", "FI"]:
        return "EU_NORDIC"
    else:
        return "OTHER"

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    request: Request,
    db: Session = Depends(get_db),
    ski_service: SkiResortService = Depends(),
    eia_service: EIAService = Depends(),
    meteostat: MeteostatService = Depends(),
    iea_service: IEAService = Depends()
):
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Dashboard data requested from {client_host}")
    
    try:
        # 1. Get ski resort locations
        logger.info("Fetching ski resort locations")
        resorts = await ski_service.get_resort_locations()
        
        # 2. For each resort, get energy market data for its region
        resort_data = []
        
        for resort in resorts[:10]:  # Limit to 10 resorts for demo
            resort_id = resort.get("id", "unknown")
            logger.info(f"Processing resort: {resort.get('name', 'unknown')} (ID: {resort_id})")
            
            try:
                # Map resort to the closest energy market region
                region_code = map_resort_to_region(resort)
                
                # Get energy data from EIA
                logger.info(f"Fetching electricity data for region {region_code}")
                energy_data = await eia_service.get_electricity_data(region_code)
                
                logger.info(f"Fetching day-ahead prices for region {region_code}")
                day_ahead = await eia_service.get_day_ahead_prices(region_code)
                
                # Get energy mix data from IEA
                country = resort.get("country", "US")
                logger.info(f"Fetching energy mix data for country {country}")
                energy_mix = await iea_service.get_realtime_data(country)
                
                # Get weather data
                lat, lon = resort.get("latitude"), resort.get("longitude")
                logger.info(f"Fetching weather data for coordinates ({lat}, {lon})")
                weather = await meteostat.get_point_data(lat, lon)
                
                # Combine data
                resort_energy = ResortEnergyData(
                    resort_id=resort["id"],
                    resort_name=resort["name"],
                    region=region_code,
                    load_data=energy_data["total_load"],
                    losses=energy_data.get("transmission_losses", 0),
                    lbmp_data=day_ahead["prices"],
                    energy_mix=energy_mix["electricity_mix"],
                    weather=weather
                )
                resort_data.append(resort_energy)
            except Exception as e:
                logger.error(f"Error processing resort {resort_id}: {str(e)}")
                logger.error(traceback.format_exc())
                # Continue with other resorts instead of failing completely
        
        if not resort_data:
            logger.error("No resort data could be processed successfully")
            raise HTTPException(status_code=500, detail="Failed to process any resort data")
        
        # 3. Get interface flows between regions
        logger.info("Fetching interface flows between regions")
        interface_flows = await eia_service.get_interface_flows()
        
        # Convert datetime to string for the timestamp
        current_time = datetime.now().isoformat()
        
        response = DashboardResponse(
            resort_data=resort_data,
            interface_flows=interface_flows,
            timestamp=current_time  # Use string timestamp instead of datetime object
        )
        
        logger.info(f"Successfully generated dashboard response with {len(resort_data)} resorts")
        return response
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to generate dashboard data",
                "error": str(e),
                "timestamp": datetime.now().isoformat()  # Use string timestamp here too
            }
        ) 