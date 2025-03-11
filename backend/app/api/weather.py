from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd

from app.db.database import get_db
from app.models.weather import Region, WeatherPoint, DailyWeather, WeatherForecast
from app.etl.weather import update_weather_data

router = APIRouter()

@router.get("/regions")
async def get_regions(db: Session = Depends(get_db)):
    """Get all regions with weather data"""
    regions = db.query(Region).all()
    return regions

@router.get("/current/{region_code}")
async def get_current_weather(
    region_code: str,
    db: Session = Depends(get_db)
):
    """Get current weather for a region"""
    # Get the region
    region = db.query(Region).filter(Region.code == region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Get the most recent weather point
    weather = db.query(WeatherPoint).filter(
        WeatherPoint.region_id == region.id,
        WeatherPoint.is_forecast == False
    ).order_by(WeatherPoint.timestamp.desc()).first()
    
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return {
        "region": region,
        "weather": weather,
        "timestamp": weather.timestamp
    }

@router.get("/daily/{region_code}")
async def get_daily_weather(
    region_code: str,
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    """Get daily weather for a region within a date range"""
    # Get the region
    region = db.query(Region).filter(Region.code == region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Build the query
    query = db.query(DailyWeather).filter(DailyWeather.region_id == region.id)
    
    # Add date filters if provided
    if start_date:
        query = query.filter(DailyWeather.date >= start_date)
    if end_date:
        query = query.filter(DailyWeather.date <= end_date)
    
    # Execute the query and sort by date
    daily_weather = query.order_by(DailyWeather.date).all()
    
    # Convert daily_weather to a list of dictionaries and handle NaN values
    import math
    import json
    from sqlalchemy.inspection import inspect
    
    result_daily_weather = []
    for dw in daily_weather:
        # Get all columns from the model
        columns = inspect(dw.__class__).columns.keys()
        dw_dict = {}
        
        # Convert each column value, replacing NaN with None
        for col in columns:
            value = getattr(dw, col)
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                dw_dict[col] = None
            else:
                dw_dict[col] = value
        
        result_daily_weather.append(dw_dict)
    
    return {
        "region": region,
        "daily_weather": result_daily_weather
    }

@router.get("/time-series/{region_code}")
async def get_weather_time_series(
    region_code: str,
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily"),
    db: Session = Depends(get_db)
):
    """Get weather time series for a region within a time range"""
    # Get the region
    region = db.query(Region).filter(Region.code == region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Build the query for weather points
    query = db.query(WeatherPoint).filter(
        WeatherPoint.region_id == region.id,
        WeatherPoint.is_forecast == False
    )
    
    # Add time filters if provided
    if start_time:
        query = query.filter(WeatherPoint.timestamp >= start_time)
    if end_time:
        query = query.filter(WeatherPoint.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    weather_points = query.order_by(WeatherPoint.timestamp).all()
    
    # Convert to DataFrame for resampling if needed
    if interval != "15min" and weather_points:
        df = pd.DataFrame([{
            "timestamp": wp.timestamp,
            "temperature": wp.temperature,
            "humidity": wp.humidity,
            "precipitation": wp.precipitation,
            "wind_speed": wp.wind_speed,
            "pressure": wp.pressure,
            "condition": wp.condition
        } for wp in weather_points])
        
        # Set timestamp as index for resampling
        df.set_index("timestamp", inplace=True)
        
        # Resample based on requested interval
        if interval == "hourly":
            resampled = df.resample("1H").mean()
        elif interval == "daily":
            resampled = df.resample("1D").mean()
        else:
            # If invalid interval, just return original data
            resampled = df
        
        # Convert back to records
        weather_points = resampled.reset_index().to_dict(orient="records")
    
    return {
        "region": region,
        "weather_points": weather_points,
        "interval": interval
    }

@router.get("/forecast/{region_code}")
async def get_weather_forecast(
    region_code: str,
    days: int = Query(7, description="Number of days to forecast"),
    db: Session = Depends(get_db)
):
    """Get weather forecast for a region"""
    # Get the region
    region = db.query(Region).filter(Region.code == region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Get the most recent forecast date
    latest_forecast = db.query(WeatherForecast.forecast_date).filter(
        WeatherForecast.region_id == region.id
    ).order_by(WeatherForecast.forecast_date.desc()).first()
    
    if not latest_forecast:
        raise HTTPException(status_code=404, detail="Forecast data not found")
    
    # Get the forecast data for the requested number of days
    forecasts = db.query(WeatherForecast).filter(
        WeatherForecast.region_id == region.id,
        WeatherForecast.forecast_date == latest_forecast.forecast_date
    ).order_by(WeatherForecast.target_date).limit(days).all()
    
    return {
        "region": region,
        "forecast_date": latest_forecast.forecast_date,
        "forecasts": forecasts
    }

@router.get("/comparison/{region_code}")
async def get_forecast_comparison(
    region_code: str,
    target_date: date = Query(..., description="Date to compare forecast with actual"),
    db: Session = Depends(get_db)
):
    """Compare weather forecast with actual data for a specific date"""
    # Get the region
    region = db.query(Region).filter(Region.code == region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Get the actual daily weather
    actual = db.query(DailyWeather).filter(
        DailyWeather.region_id == region.id,
        DailyWeather.date == target_date
    ).first()
    
    if not actual:
        raise HTTPException(status_code=404, detail="Actual weather data not found for this date")
    
    # Get all forecasts for the target date
    forecasts = db.query(WeatherForecast).filter(
        WeatherForecast.region_id == region.id,
        WeatherForecast.target_date == target_date
    ).order_by(WeatherForecast.forecast_date).all()
    
    return {
        "region": region,
        "target_date": target_date,
        "actual": actual,
        "forecasts": forecasts
    }

@router.post("/update")
async def trigger_weather_update(db: Session = Depends(get_db)):
    """Manually trigger a weather data update"""
    try:
        update_weather_data(db)
        return {"status": "success", "message": "Weather data update completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating weather data: {str(e)}") 