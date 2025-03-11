import os
import logging
from datetime import datetime, timedelta
from meteostat import Point, Hourly, Daily, Monthly, Normals
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

from app.models.weather import Region, WeatherPoint, HourlyWeather, DailyWeather, MonthlyWeather, ClimateNormal, WeatherForecast
from app.etl.weather_forecast import generate_daily_forecast, generate_weekly_forecast
from app.etl.weather_interpolation import interpolate_to_15min

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

def fetch_weather_data(db: Session, days_back: int = 30):
    """
    Fetch weather data for all regions from Meteostat
    
    Args:
        db: Database session
        days_back: Number of days to fetch data for (from today backwards)
    """
    # Get all regions from the database
    regions = db.query(Region).all()
    
    if not regions:
        logger.warning("No regions found in the database")
        return
    
    # Set time period
    end = datetime.now()
    start = end - timedelta(days=days_back)
    
    for region in regions:
        logger.info(f"Fetching weather data for {region.code} ({region.name})")
        
        # Create Meteostat Point
        point = Point(region.latitude, region.longitude)
        
        # Fetch hourly data
        fetch_hourly_data(db, region, point, start, end)
        
        # Fetch daily data
        fetch_daily_data(db, region, point, start, end)
        
        # Fetch monthly data
        fetch_monthly_data(db, region, point, start, end)
        
        # Fetch climate normals
        fetch_climate_normals(db, region, point)
        
        # Generate 15-minute data
        generate_15min_data(db, region, start, end)
        
        # Generate forecasts
        generate_forecasts(db, region)

def fetch_hourly_data(db: Session, region: Region, point: Point, start: datetime, end: datetime):
    """Fetch hourly weather data from Meteostat"""
    try:
        # Get hourly data
        data = Hourly(point, start, end)
        data = data.fetch()
        
        if data.empty:
            logger.warning(f"No hourly data found for {region.code}")
            return
            
        # Handle missing values - drop rows with too many missing values and fill others
        # Drop rows where all important weather variables are missing
        important_cols = ['temp', 'rhum', 'prcp', 'wspd']
        available_cols = [col for col in important_cols if col in data.columns]
        
        if available_cols:
            # Drop rows where all important weather variables are NaN
            data = data.dropna(subset=available_cols, how='all')
            
            # For remaining rows, fill NaN values with appropriate values
            if 'temp' in data.columns:
                # Use forward/backward fill for temperature
                data['temp'] = data['temp'].fillna(method='ffill').fillna(method='bfill')
                
            if 'rhum' in data.columns:
                # Use median for humidity
                data['rhum'] = data['rhum'].fillna(data['rhum'].median())
                
            if 'prcp' in data.columns:
                # Use 0 for precipitation (assuming no rain when data is missing)
                data['prcp'] = data['prcp'].fillna(0)
                
            if 'snow' in data.columns:
                # Use 0 for snow (assuming no snow when data is missing)
                data['snow'] = data['snow'].fillna(0)
                
            if 'wspd' in data.columns:
                # Use median for wind speed
                data['wspd'] = data['wspd'].fillna(data['wspd'].median())
        
        # Get the maximum ID from the database to start our counter
        max_id = db.query(func.max(HourlyWeather.id)).scalar() or 0
        counter = max_id + 1
        
        # Process each row
        for index, row in data.iterrows():
            # Check if data already exists
            existing = db.query(HourlyWeather).filter(
                HourlyWeather.region_id == region.id,
                HourlyWeather.timestamp == index
            ).first()
            
            if existing:
                continue
            
            # Create new hourly weather record
            hourly = HourlyWeather(
                id=counter,  # Set explicit ID
                region_id=region.id,
                timestamp=index,
                temperature=row.get('temp'),
                feels_like=row.get('feels_like'),
                humidity=row.get('rhum'),
                precipitation=row.get('prcp'),
                snow=row.get('snow'),
                wind_speed=row.get('wspd'),
                wind_direction=row.get('wdir'),
                pressure=row.get('pres'),
                condition=row.get('coco'),
            )
            
            db.add(hourly)
            counter += 1
        
        db.commit()
        logger.info(f"Added hourly data for {region.code}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching hourly data for {region.code}: {str(e)}")

def fetch_daily_data(db: Session, region: Region, point: Point, start: datetime, end: datetime):
    """Fetch daily weather data from Meteostat"""
    try:
        # Get daily data
        data = Daily(point, start, end)
        data = data.fetch()
        
        if data.empty:
            logger.warning(f"No daily data found for {region.code}")
            return
            
        # Handle missing values
        # Drop rows where all important weather variables are missing
        important_cols = ['tavg', 'tmin', 'tmax', 'prcp', 'wspd']
        available_cols = [col for col in important_cols if col in data.columns]
        
        if available_cols:
            # Drop rows where all important weather variables are NaN
            data = data.dropna(subset=available_cols, how='all')
            
            # For remaining rows, fill NaN values with appropriate values
            for temp_col in ['tavg', 'tmin', 'tmax']:
                if temp_col in data.columns:
                    # Use forward/backward fill for temperature
                    data[temp_col] = data[temp_col].fillna(method='ffill').fillna(method='bfill')
                    
            if 'prcp' in data.columns:
                # Use 0 for precipitation (assuming no rain when data is missing)
                data['prcp'] = data['prcp'].fillna(0)
                
            if 'snow' in data.columns:
                # Use 0 for snow (assuming no snow when data is missing)
                data['snow'] = data['snow'].fillna(0)
                
            if 'wspd' in data.columns:
                # Use median for wind speed
                data['wspd'] = data['wspd'].fillna(data['wspd'].median())
        
        # Get the maximum ID from the database to start our counter
        max_id = db.query(func.max(DailyWeather.id)).scalar() or 0
        counter = max_id + 1
        
        # Process each row
        for index, row in data.iterrows():
            # Check if data already exists
            existing = db.query(DailyWeather).filter(
                DailyWeather.region_id == region.id,
                DailyWeather.date == index.date()
            ).first()
            
            if existing:
                continue
            
            # Create new daily weather record
            daily = DailyWeather(
                region_id=region.id,
                date=index.date(),
                temperature_min=row.get('tmin'),
                temperature_max=row.get('tmax'),
                temperature_avg=row.get('tavg'),
                precipitation=row.get('prcp'),
                snow=row.get('snow'),
                wind_speed=row.get('wspd'),
                wind_direction=row.get('wdir'),
                pressure=row.get('pres'),
                condition=None,  # Daily data doesn't have condition
                cloud_cover=None  # Daily data doesn't have cloud cover
            )
            
            db.add(daily)
        
        db.commit()
        logger.info(f"Added daily data for {region.code}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching daily data for {region.code}: {str(e)}")

def fetch_monthly_data(db: Session, region: Region, point: Point, start: datetime, end: datetime):
    """Fetch monthly weather data from Meteostat"""
    try:
        # Get monthly data
        data = Monthly(point, start.year, end.year)
        data = data.fetch()
        
        if data.empty:
            logger.warning(f"No monthly data found for {region.code}")
            return
        
        # Process each row
        for index, row in data.iterrows():
            year = index.year
            month = index.month
            
            # Check if data already exists
            existing = db.query(MonthlyWeather).filter(
                MonthlyWeather.region_id == region.id,
                MonthlyWeather.year == year,
                MonthlyWeather.month == month
            ).first()
            
            if existing:
                continue
            
            # Create new monthly weather record
            monthly = MonthlyWeather(
                region_id=region.id,
                year=year,
                month=month,
                temperature_min=row.get('tmin'),
                temperature_max=row.get('tmax'),
                temperature_avg=row.get('tavg'),
                precipitation=row.get('prcp'),
                snow=None,  # Monthly data doesn't have snow
                wind_speed=None,  # Monthly data doesn't have wind speed
                wind_direction=None,  # Monthly data doesn't have wind direction
                pressure=None,  # Monthly data doesn't have pressure
                condition=None,  # Monthly data doesn't have condition
                cloud_cover=None  # Monthly data doesn't have cloud cover
            )
            
            db.add(monthly)
        
        db.commit()
        logger.info(f"Added monthly data for {region.code}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching monthly data for {region.code}: {str(e)}")

def fetch_climate_normals(db: Session, region: Region, point: Point):
    """Fetch climate normals from Meteostat"""
    try:
        # Get climate normals
        data = Normals(point)
        data = data.fetch()
        
        if data.empty:
            logger.warning(f"No climate normals found for {region.code}")
            return
        
        # Process each row
        for index, row in data.iterrows():
            month = index.month
            day = index.day
            
            # Check if data already exists
            existing = db.query(ClimateNormal).filter(
                ClimateNormal.region_id == region.id,
                ClimateNormal.month == month,
                ClimateNormal.day == day
            ).first()
            
            if existing:
                continue
            
            # Create new climate normal record
            normal = ClimateNormal(
                region_id=region.id,
                month=month,
                day=day,
                temperature_min=row.get('tmin'),
                temperature_max=row.get('tmax'),
                temperature_avg=row.get('tavg'),
                precipitation=row.get('prcp')
            )
            
            db.add(normal)
        
        db.commit()
        logger.info(f"Added climate normals for {region.code}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching climate normals for {region.code}: {str(e)}")

def generate_15min_data(db: Session, region: Region, start: datetime, end: datetime):
    """Generate 15-minute weather data from hourly, daily, and climate normals"""
    try:
        # Get the latest 15-minute data timestamp
        latest = db.query(WeatherPoint.timestamp).filter(
            WeatherPoint.region_id == region.id,
            WeatherPoint.is_forecast == False
        ).order_by(WeatherPoint.timestamp.desc()).first()
        
        if latest:
            # If we have data, start from the latest timestamp
            start = max(start, latest.timestamp)
        
        # Get hourly data
        hourly_data = db.query(HourlyWeather).filter(
            HourlyWeather.region_id == region.id,
            HourlyWeather.timestamp >= start,
            HourlyWeather.timestamp <= end
        ).order_by(HourlyWeather.timestamp).all()
        
        if not hourly_data:
            logger.warning(f"No hourly data found for {region.code} to generate 15-minute data")
            return
        
        # Convert to DataFrame
        hourly_df = pd.DataFrame([{
            "timestamp": h.timestamp,
            "temperature": h.temperature,
            "feels_like": h.feels_like,
            "humidity": h.humidity,
            "precipitation": h.precipitation,
            "snow": h.snow,
            "wind_speed": h.wind_speed,
            "wind_direction": h.wind_direction,
            "pressure": h.pressure,
            "condition": h.condition,
            "cloud_cover": h.cloud_cover
        } for h in hourly_data])
        
        # Set timestamp as index
        hourly_df.set_index("timestamp", inplace=True)
        
        # Get daily data for the same period
        daily_data = db.query(DailyWeather).filter(
            DailyWeather.region_id == region.id,
            DailyWeather.date >= start.date(),
            DailyWeather.date <= end.date()
        ).order_by(DailyWeather.date).all()
        
        daily_df = None
        if daily_data:
            daily_df = pd.DataFrame([{
                "date": d.date,
                "temperature_min": d.temperature_min,
                "temperature_max": d.temperature_max,
                "temperature_avg": d.temperature_avg,
                "precipitation": d.precipitation
            } for d in daily_data])
            daily_df.set_index("date", inplace=True)
        
        # Get climate normals
        normals = db.query(ClimateNormal).filter(
            ClimateNormal.region_id == region.id
        ).all()
        
        normals_df = None
        if normals:
            normals_df = pd.DataFrame([{
                "month": n.month,
                "day": n.day,
                "temperature_min": n.temperature_min,
                "temperature_max": n.temperature_max,
                "temperature_avg": n.temperature_avg,
                "precipitation": n.precipitation
            } for n in normals])
        
        # Generate 15-minute data using interpolation
        data_15min = interpolate_to_15min(hourly_df, daily_df, normals_df)
        
        # Save to database
        for index, row in data_15min.iterrows():
            # Check if data already exists
            existing = db.query(WeatherPoint).filter(
                WeatherPoint.region_id == region.id,
                WeatherPoint.timestamp == index,
                WeatherPoint.is_forecast == False
            ).first()
            
            if existing:
                continue
            
            # Create new weather point
            point = WeatherPoint(
                region_id=region.id,
                timestamp=index,
                temperature=row.get('temperature'),
                feels_like=row.get('feels_like'),
                humidity=row.get('humidity'),
                precipitation=row.get('precipitation'),
                snow=row.get('snow'),
                snow_depth=None,  # Not available in the source data
                wind_speed=row.get('wind_speed'),
                wind_direction=row.get('wind_direction'),
                pressure=row.get('pressure'),
                condition=row.get('condition'),
                cloud_cover=row.get('cloud_cover'),
                solar_radiation=None,  # Not available in the source data
                is_forecast=False
            )
            
            db.add(point)
        
        db.commit()
        logger.info(f"Generated 15-minute data for {region.code}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating 15-minute data for {region.code}: {str(e)}")

def generate_forecasts(db: Session, region: Region):
    """Generate daily and weekly forecasts"""
    try:
        # Get the latest data for forecasting
        latest_date = db.query(DailyWeather.date).filter(
            DailyWeather.region_id == region.id
        ).order_by(DailyWeather.date.desc()).first()
        
        if not latest_date:
            logger.warning(f"No daily data found for {region.code} to generate forecasts")
            return
        
        # Get historical data for forecasting
        historical = db.query(DailyWeather).filter(
            DailyWeather.region_id == region.id
        ).order_by(DailyWeather.date).all()
        
        if not historical:
            logger.warning(f"No historical data found for {region.code} to generate forecasts")
            return
        
        # Convert to DataFrame
        historical_df = pd.DataFrame([{
            "date": h.date,
            "temperature_min": h.temperature_min,
            "temperature_max": h.temperature_max,
            "temperature_avg": h.temperature_avg,
            "precipitation": h.precipitation
        } for h in historical])
        
        historical_df.set_index("date", inplace=True)
        
        # Get climate normals
        normals = db.query(ClimateNormal).filter(
            ClimateNormal.region_id == region.id
        ).all()
        
        normals_df = None
        if normals:
            normals_df = pd.DataFrame([{
                "month": n.month,
                "day": n.day,
                "temperature_min": n.temperature_min,
                "temperature_max": n.temperature_max,
                "temperature_avg": n.temperature_avg,
                "precipitation": n.precipitation
            } for n in normals])
        
        # Generate daily forecast
        forecast_date = datetime.now().date()
        daily_forecast = generate_daily_forecast(historical_df, normals_df, forecast_date)
        
        # Generate weekly forecast
        days = int(os.getenv("FORECAST_DAYS", "7"))
        weekly_forecast = generate_weekly_forecast(historical_df, normals_df, forecast_date, days)
        
        # Save forecasts to database
        for date, forecast in weekly_forecast.items():
            # Check if forecast already exists
            existing = db.query(WeatherForecast).filter(
                WeatherForecast.region_id == region.id,
                WeatherForecast.forecast_date == forecast_date,
                WeatherForecast.target_date == date
            ).first()
            
            if existing:
                # Update existing forecast
                existing.temperature_min = forecast.get('temperature_min')
                existing.temperature_max = forecast.get('temperature_max')
                existing.temperature_avg = forecast.get('temperature_avg')
                existing.precipitation = forecast.get('precipitation')
                existing.condition = forecast.get('condition')
            else:
                # Create new forecast
                new_forecast = WeatherForecast(
                    region_id=region.id,
                    forecast_date=forecast_date,
                    target_date=date,
                    temperature_min=forecast.get('temperature_min'),
                    temperature_max=forecast.get('temperature_max'),
                    temperature_avg=forecast.get('temperature_avg'),
                    precipitation=forecast.get('precipitation'),
                    condition=forecast.get('condition')
                )
                db.add(new_forecast)
        
        # Also generate 15-minute forecast data for the next 24 hours
        if daily_forecast:
            # Get the latest actual 15-minute data
            latest_point = db.query(WeatherPoint).filter(
                WeatherPoint.region_id == region.id,
                WeatherPoint.is_forecast == False
            ).order_by(WeatherPoint.timestamp.desc()).first()
            
            if latest_point:
                # Start from the next 15-minute interval
                start_time = latest_point.timestamp + timedelta(minutes=15)
                end_time = start_time + timedelta(hours=24)
                
                # Generate timestamps for the next 24 hours in 15-minute intervals
                timestamps = pd.date_range(start=start_time, end=end_time, freq='15min')
                
                for ts in timestamps:
                    # Simple linear interpolation for the forecast
                    hour = ts.hour + ts.minute / 60
                    
                    # Diurnal temperature variation (simple sine wave)
                    temp_range = daily_forecast.get('temperature_max') - daily_forecast.get('temperature_min')
                    temp_offset = np.sin(np.pi * (hour - 6) / 12)  # Peak at 6 PM, trough at 6 AM
                    temperature = daily_forecast.get('temperature_avg') + temp_offset * temp_range / 2
                    
                    # Check if forecast already exists
                    existing = db.query(WeatherPoint).filter(
                        WeatherPoint.region_id == region.id,
                        WeatherPoint.timestamp == ts,
                        WeatherPoint.is_forecast == True
                    ).first()
                    
                    if existing:
                        # Update existing forecast
                        existing.temperature = temperature
                        existing.condition = daily_forecast.get('condition')
                    else:
                        # Create new forecast point
                        forecast_point = WeatherPoint(
                            region_id=region.id,
                            timestamp=ts,
                            temperature=temperature,
                            feels_like=temperature,  # Simplified
                            humidity=50,  # Default value
                            precipitation=daily_forecast.get('precipitation') / 96 if daily_forecast.get('precipitation') else 0,  # Distribute evenly
                            snow=0,  # Default value
                            snow_depth=0,  # Default value
                            wind_speed=5,  # Default value
                            wind_direction=0,  # Default value
                            pressure=1013,  # Default value
                            condition=daily_forecast.get('condition'),
                            cloud_cover=50,  # Default value
                            solar_radiation=None,
                            is_forecast=True
                        )
                        db.add(forecast_point)
        
        db.commit()
        logger.info(f"Generated forecasts for {region.code}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating forecasts for {region.code}: {str(e)}")

def update_weather_data(db: Session, days_back: int = 30):
    """
    Update weather data in the database
    
    Args:
        db: Database session
        days_back: Number of days to fetch data for (from today backwards)
    """
    try:
        # Fetch weather data from Meteostat
        fetch_weather_data(db, days_back=days_back)
        
        # Generate forecasts
        for region in db.query(Region).all():
            generate_forecasts(db, region)
            
        return True
    except Exception as e:
        logger.error(f"Error updating weather data: {str(e)}")
        return False 