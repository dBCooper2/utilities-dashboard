import os
import logging
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import SessionLocal
from app.etl.weather import update_weather_data
from app.models.weather import WeatherPoint, HourlyWeather, DailyWeather
from app.etl.energy import update_energy_data
from app.models.energy import LBMP, Load, FuelMix, InterfaceFlow

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

def start_scheduler():
    """Start the background scheduler for ETL tasks"""
    scheduler = BackgroundScheduler()
    
    # Add weather data update job (runs daily at 1:00 AM)
    scheduler.add_job(
        run_weather_update,
        trigger=CronTrigger(hour=1, minute=0),
        id="weather_update",
        name="Update weather data",
        replace_existing=True
    )
    
    # Add energy data update job (runs daily at 2:00 AM)
    scheduler.add_job(
        run_energy_update,
        trigger=CronTrigger(hour=2, minute=0),
        id="energy_update",
        name="Update energy data",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    return scheduler

def run_weather_update():
    """Run weather data update job"""
    logger.info(f"Running weather data update job at {datetime.now()}")
    
    # Create database session
    db = SessionLocal()
    try:
        # Update weather data
        update_weather_data(db)
        logger.info("Weather data update completed")
    except Exception as e:
        logger.error(f"Error updating weather data: {str(e)}")
    finally:
        db.close()

def run_energy_update():
    """Run energy data update job"""
    logger.info(f"Running energy data update job at {datetime.now()}")
    
    # Create database session
    db = SessionLocal()
    try:
        # Update energy data
        update_energy_data(db)
        logger.info("Energy data update completed")
    except Exception as e:
        logger.error(f"Error updating energy data: {str(e)}")
    finally:
        db.close()

def is_database_empty(db: Session):
    """Check if the database is empty or lacks sufficient data
    
    Returns True if the database is empty or has insufficient data
    """
    # Check weather data
    weather_count = db.query(func.count(WeatherPoint.id)).scalar() or 0
    hourly_count = db.query(func.count(HourlyWeather.id)).scalar() or 0
    daily_count = db.query(func.count(DailyWeather.id)).scalar() or 0
    
    # Check energy data
    lbmp_count = db.query(func.count(LBMP.id)).scalar() or 0
    load_count = db.query(func.count(Load.id)).scalar() or 0
    fuel_mix_count = db.query(func.count(FuelMix.id)).scalar() or 0
    
    # Return True if data is insufficient
    weather_empty = (weather_count < 10 or hourly_count < 100 or daily_count < 10)
    energy_empty = (lbmp_count < 100 or load_count < 100 or fuel_mix_count < 100)
    
    return weather_empty or energy_empty

def check_data_freshness(db: Session):
    """Check if the latest data is fresh or needs updating
    
    Returns True if data is stale and needs updating
    """
    # Get current date
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check most recent weather data
    latest_weather = db.query(func.max(WeatherPoint.timestamp)).scalar()
    latest_hourly = db.query(func.max(HourlyWeather.timestamp)).scalar()
    
    # Check most recent energy data
    latest_lbmp = db.query(func.max(LBMP.timestamp)).scalar()
    latest_load = db.query(func.max(Load.timestamp)).scalar()
    
    # Check if any data is missing or stale
    if not latest_weather or not latest_hourly or not latest_lbmp or not latest_load:
        return True
    
    # Convert to date objects
    try:
        weather_date = latest_weather.date()
        hourly_date = latest_hourly.date()
        lbmp_date = latest_lbmp.date()
        load_date = latest_load.date()
        
        # Check if data is from yesterday or earlier
        weather_stale = weather_date < yesterday
        hourly_stale = hourly_date < yesterday
        lbmp_stale = lbmp_date < yesterday
        load_stale = load_date < yesterday
        
        return weather_stale or hourly_stale or lbmp_stale or load_stale
    except:
        # If any error occurs, consider data as stale
        return True

def run_initial_data_load():
    """Run initial data load if database is empty or data is stale"""
    logger.info(f"Checking if initial data load is needed at {datetime.now()}")
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if database is empty or data is stale
        if is_database_empty(db) or check_data_freshness(db):
            logger.info(f"Database is empty or data is stale, running initial data load")
            
            # Set date range: from January 1st of current year to today
            today = date.today()
            start_date = date(today.year, 1, 1)
            days_back = (today - start_date).days
            
            # Update weather data with specific date range
            update_weather_data(db, days_back=days_back)
            logger.info("Initial weather data load completed")
            
            # Update energy data with specific date range
            update_energy_data(db, days_back=days_back)
            logger.info("Initial energy data load completed")
        else:
            logger.info("Database already contains data, skipping initial load")
            
    except Exception as e:
        logger.error(f"Error during initial data load: {str(e)}")
    finally:
        db.close() 