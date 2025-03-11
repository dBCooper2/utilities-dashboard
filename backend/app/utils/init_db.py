import os
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from meteostat import Point
from sqlalchemy import text

from app.db.database import Base, engine, init_timescale_db, create_hypertable
from app.models.weather import Region, WeatherPoint, HourlyWeather, DailyWeather, MonthlyWeather, ClimateNormal
from app.models.energy import Zone, LBMP, Load, FuelMix, InterfaceFlow, ZoneInterface, ZoneInterfaceFlow
from app.utils.geojson import import_zones_from_geojson

# Configure logging
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with tables and sample data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize TimescaleDB
    init_timescale_db()
    
    # Create hypertables for time-series data
    create_hypertable("weather_points", "timestamp")
    create_hypertable("hourly_weather", "timestamp")
    create_hypertable("lbmp", "timestamp")
    create_hypertable("load", "timestamp")
    create_hypertable("fuel_mix", "timestamp")
    create_hypertable("interface_flow", "timestamp")
    create_hypertable("zone_interface_flow", "timestamp")
    
    logger.info("Database initialized")

def create_sample_regions(db: Session):
    """Create sample regions for testing"""
    # Check if regions already exist
    if db.query(Region).count() > 0:
        logger.info("Regions already exist, skipping sample data creation")
        return
    
    # Create sample regions
    regions = [
        Region(
            code="US-SE-ATL",
            name="Atlanta",
            state="Georgia",
            latitude=33.7490,
            longitude=-84.3880
        ),
        Region(
            code="US-SE-MIA",
            name="Miami",
            state="Florida",
            latitude=25.7617,
            longitude=-80.1918
        ),
        Region(
            code="US-SE-CHA",
            name="Charlotte",
            state="North Carolina",
            latitude=35.2271,
            longitude=-80.8431
        )
    ]
    
    db.add_all(regions)
    db.commit()
    
    logger.info(f"Created {len(regions)} sample regions")

def import_southeast_zones(db: Session):
    """Import southeastern zones from GeoJSON file"""
    # Check if zones already exist
    if db.query(Zone).count() > 0:
        logger.info("Zones already exist, skipping import")
        return
    
    # Get the path to the GeoJSON file
    geojson_path = os.path.join(os.getcwd(), "southeast_regions.geojson")
    
    # Import zones
    count = import_zones_from_geojson(db, geojson_path)
    
    logger.info(f"Imported {count} zones from GeoJSON")

def create_sample_weather_data(db: Session):
    """Create sample weather data for testing"""
    # Check if weather data already exists
    if db.query(WeatherPoint).count() > 0:
        logger.info("Weather data already exists, skipping sample data creation")
        return
    
    # Drop existing daily weather data to avoid ID conflicts
    try:
        db.execute(text("DELETE FROM daily_weather"))
        db.commit()
        logger.info("Cleared existing daily weather data")
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing daily weather data: {str(e)}")
    
    # Get regions
    regions = db.query(Region).all()
    
    if not regions:
        logger.warning("No regions found, skipping weather data creation")
        return
    
    # Create sample weather data for each region
    for region in regions:
        # Create a Meteostat Point
        point = Point(region.latitude, region.longitude)
        
        # Set time period (last 7 days)
        end = datetime.now()
        start = end - timedelta(days=7)
        
        # Create sample hourly data
        for i in range(7 * 24):
            timestamp = start + timedelta(hours=i)
            
            # Create hourly weather record
            hourly = HourlyWeather(
                id=i + 1,  # Add an explicit ID
                region_id=region.id,
                timestamp=timestamp,
                temperature=20 + 5 * (i % 24) / 24,  # Simple diurnal pattern
                feels_like=20 + 5 * (i % 24) / 24,
                humidity=60 + 20 * (i % 24) / 24,
                precipitation=0.1 if i % 12 == 0 else 0,
                snow=0,
                wind_speed=5 + 3 * (i % 24) / 24,
                wind_direction=180,
                pressure=1013,
                condition=1 if i % 24 > 6 and i % 24 < 18 else 3,
                cloud_cover=30
            )
            
            db.add(hourly)
        
        # Create sample daily data
        for i in range(7):
            date = (start + timedelta(days=i)).date()
            
            # Create daily weather record
            daily = DailyWeather(
                region_id=region.id,
                date=date,
                temperature_min=18,
                temperature_max=25,
                temperature_avg=22,
                precipitation=0.5 if i % 3 == 0 else 0,
                snow=0,
                wind_speed=7,
                wind_direction=180,
                pressure=1013,
                condition=1 if i % 3 != 0 else 4,
                cloud_cover=30
            )
            
            db.add(daily)
    
    db.commit()
    logger.info("Created sample weather data")

def create_sample_energy_data(db: Session):
    """Create sample energy data for testing"""
    # Check if energy data already exists
    if db.query(LBMP).count() > 0:
        logger.info("Energy data already exists, skipping sample data creation")
        return
    
    # Get zones
    zones = db.query(Zone).all()
    
    if not zones:
        logger.warning("No zones found, skipping energy data creation")
        return
    
    # Create sample energy data for each zone
    for zone in zones:
        # Set time period (last 7 days)
        end = datetime.now()
        start = end - timedelta(days=7)
        
        # Create sample LBMP data
        for i in range(7 * 24):
            timestamp = start + timedelta(hours=i)
            
            # Create LBMP record
            lbmp = LBMP(
                zone_id=zone.id,
                timestamp=timestamp,
                type="DA",
                price=30 + 10 * (i % 24) / 24,  # Simple diurnal pattern
                congestion=2 + (i % 24) / 24,
                losses=1 + 0.5 * (i % 24) / 24
            )
            
            db.add(lbmp)
        
        # Create sample load data
        for i in range(7 * 24):
            timestamp = start + timedelta(hours=i)
            
            # Create load record
            load = Load(
                zone_id=zone.id,
                timestamp=timestamp,
                type="D",
                value=1000 + 500 * (i % 24) / 24,  # Simple diurnal pattern
                with_losses=1100 + 550 * (i % 24) / 24
            )
            
            db.add(load)
    
    # Create sample fuel mix data
    iso_rtos = set(zone.iso_rto for zone in zones)
    for iso_rto in iso_rtos:
        # Set time period (last 7 days)
        end = datetime.now()
        start = end - timedelta(days=7)
        
        # Create sample fuel mix data
        for i in range(7 * 24):
            timestamp = start + timedelta(hours=i)
            
            # Create fuel mix records for different fuel types
            fuel_types = {
                "COL": 500 + 100 * (i % 24) / 24,  # Coal
                "NG": 800 + 200 * (i % 24) / 24,   # Natural Gas
                "NUC": 1000,                        # Nuclear (constant)
                "WND": 200 + 100 * (i % 24) / 24,   # Wind
                "SUN": 300 * (i % 24) / 24 if 6 <= (i % 24) <= 18 else 0  # Solar (daytime only)
            }
            
            for fuel_type, generation in fuel_types.items():
                fuel_mix = FuelMix(
                    iso_rto=iso_rto,
                    state=None,
                    timestamp=timestamp,
                    fuel_type=fuel_type,
                    generation=generation
                )
                
                db.add(fuel_mix)
    
    # Create sample interface flow data
    iso_rto_list = list(iso_rtos)
    if len(iso_rto_list) >= 2:
        # Set time period (last 7 days)
        end = datetime.now()
        start = end - timedelta(days=7)
        
        # Create sample interface flow data between first two ISO/RTOs
        from_iso = iso_rto_list[0]
        to_iso = iso_rto_list[1]
        
        for i in range(7 * 24):
            timestamp = start + timedelta(hours=i)
            
            # Create interface flow record
            flow = InterfaceFlow(
                timestamp=timestamp,
                from_iso_rto=from_iso,
                to_iso_rto=to_iso,
                value=200 + 100 * (i % 24) / 24  # Simple diurnal pattern
            )
            
            db.add(flow)
    
    db.commit()
    logger.info("Created sample energy data")

def create_sample_zone_interfaces(db: Session):
    """Create sample zone interfaces based on existing zones"""
    # Check if zone interfaces already exist
    if db.query(ZoneInterface).count() > 0:
        logger.info("Zone interfaces already exist, skipping sample data creation")
        return
    
    # Get all zones
    zones = db.query(Zone).all()
    
    if not zones:
        logger.warning("No zones found in the database, skipping zone interface creation")
        return
    
    # Group zones by ISO/RTO
    zones_by_iso = {}
    for zone in zones:
        if zone.iso_rto not in zones_by_iso:
            zones_by_iso[zone.iso_rto] = []
        zones_by_iso[zone.iso_rto].append(zone)
    
    interfaces = []
    
    # First, create interfaces between neighboring zones within the same ISO/RTO
    for iso_rto, iso_zones in zones_by_iso.items():
        # For simplicity, we'll create interfaces between zones with consecutive indices
        for i in range(len(iso_zones) - 1):
            from_zone = iso_zones[i]
            to_zone = iso_zones[i + 1]
            
            # Create interfaces in both directions
            interfaces.append(
                ZoneInterface(
                    name=f"{from_zone.code}-{to_zone.code}",
                    from_zone_id=from_zone.id,
                    to_zone_id=to_zone.id,
                    capacity=1000.0,  # Sample capacity
                    is_active=1
                )
            )
            
            interfaces.append(
                ZoneInterface(
                    name=f"{to_zone.code}-{from_zone.code}",
                    from_zone_id=to_zone.id,
                    to_zone_id=from_zone.id,
                    capacity=1000.0,  # Sample capacity
                    is_active=1
                )
            )
    
    # Second, create interfaces between ISOs/RTOs (connecting border zones)
    for from_iso, from_iso_zones in zones_by_iso.items():
        for to_iso, to_iso_zones in zones_by_iso.items():
            if from_iso != to_iso:
                # For simplicity, connect the first zone of each ISO/RTO
                from_zone = from_iso_zones[0]
                to_zone = to_iso_zones[0]
                
                # Create interface in one direction
                interfaces.append(
                    ZoneInterface(
                        name=f"{from_iso}-{to_iso}",
                        from_zone_id=from_zone.id,
                        to_zone_id=to_zone.id,
                        capacity=2000.0,  # Sample capacity for inter-ISO connections
                        is_active=1
                    )
                )
    
    # Add interfaces to database
    db.add_all(interfaces)
    db.commit()
    
    logger.info(f"Created {len(interfaces)} sample zone interfaces")

def create_sample_zone_interface_flow(db: Session):
    """Create sample flow data for zone interfaces"""
    # Check if zone interface flow data already exists
    if db.query(ZoneInterfaceFlow).count() > 0:
        logger.info("Zone interface flow data already exists, skipping sample data creation")
        return
    
    # Get all zone interfaces
    interfaces = db.query(ZoneInterface).all()
    
    if not interfaces:
        logger.warning("No zone interfaces found in the database, skipping flow data creation")
        return
    
    # Set time period for sample data
    end = datetime.now()
    start = datetime(end.year, 1, 1)  # From January 1st of current year
    
    # Create hourly data points
    current = start
    flow_data = []
    
    while current <= end:
        for interface in interfaces:
            # Create some random flow data with daily patterns
            hour = current.hour
            base_flow = interface.capacity * 0.6  # Base flow is 60% of capacity
            
            # Add time-of-day variation
            if 7 <= hour <= 22:  # Daytime: higher flow
                flow_factor = 0.8 + 0.2 * (hour - 7) / 15  # Ramping up during the day
            else:  # Nighttime: lower flow
                flow_factor = 0.5
            
            # Add some randomness
            flow_factor += (hash(f"{interface.id}-{current}") % 100) / 200 - 0.25  # ±25% variation
            
            # Ensure flow is within capacity limits
            flow = max(0, min(interface.capacity, base_flow * flow_factor))
            
            # Add congestion during peak hours
            congestion = 0.0
            if 17 <= hour <= 21:  # Peak hours
                congestion = (flow / interface.capacity) * 10.0  # Higher congestion when flow approaches capacity
            
            flow_data.append(
                ZoneInterfaceFlow(
                    interface_id=interface.id,
                    timestamp=current,
                    value=flow,
                    congestion=congestion
                )
            )
        
        # Move to next hour
        current += timedelta(hours=1)
        
        # Commit in batches to avoid memory issues
        if len(flow_data) >= 1000:
            db.add_all(flow_data)
            db.commit()
            flow_data = []
    
    # Commit any remaining flow data
    if flow_data:
        db.add_all(flow_data)
        db.commit()
    
    logger.info(f"Created sample flow data for {len(interfaces)} zone interfaces")

def create_sample_data(db: Session):
    """Create all sample data for the application"""
    # Create regions and zones
    create_sample_regions(db)
    import_southeast_zones(db)
    
    # Create zone interfaces
    create_sample_zone_interfaces(db)
    
    # Create weather data
    create_sample_weather_data(db)
    
    # Create energy data
    create_sample_energy_data(db)
    
    # Create zone interface flow data
    create_sample_zone_interface_flow(db)
    
    logger.info("Sample data creation completed")

def main():
    """Main function to initialize database and create sample data"""
    from app.db.database import SessionLocal
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        # Create sample data
        create_sample_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 