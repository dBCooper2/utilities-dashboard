import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_daily_forecast(historical_df, normals_df, target_date):
    """
    Generate a daily weather forecast for a specific date
    
    Args:
        historical_df: DataFrame with historical daily weather data
        normals_df: DataFrame with climate normals
        target_date: Date to forecast for
    
    Returns:
        Dictionary with forecast data
    """
    try:
        # Convert target_date to datetime if it's not already
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        # Get month and day
        month = target_date.month
        day = target_date.day
        
        # Get climate normal for this day
        normal = None
        if normals_df is not None and not normals_df.empty:
            normal_row = normals_df[(normals_df['month'] == month) & (normals_df['day'] == day)]
            if not normal_row.empty:
                normal = normal_row.iloc[0]
        
        # Get recent historical data (last 30 days)
        recent_cutoff = target_date - timedelta(days=30)
        recent_data = historical_df[historical_df.index >= recent_cutoff]
        
        # Get seasonal historical data (same month, previous years)
        seasonal_data = historical_df[
            (historical_df.index.month == month) & 
            ((historical_df.index.day >= day - 7) & (historical_df.index.day <= day + 7))
        ]
        
        # Initialize forecast with climate normals if available
        if normal is not None:
            forecast = {
                'temperature_min': normal['temperature_min'],
                'temperature_max': normal['temperature_max'],
                'temperature_avg': normal['temperature_avg'],
                'precipitation': normal['precipitation'],
                'condition': estimate_condition(normal['temperature_avg'], normal['precipitation'])
            }
        else:
            # Use seasonal averages if normals not available
            if not seasonal_data.empty:
                forecast = {
                    'temperature_min': seasonal_data['temperature_min'].mean(),
                    'temperature_max': seasonal_data['temperature_max'].mean(),
                    'temperature_avg': seasonal_data['temperature_avg'].mean(),
                    'precipitation': seasonal_data['precipitation'].mean(),
                    'condition': estimate_condition(
                        seasonal_data['temperature_avg'].mean(), 
                        seasonal_data['precipitation'].mean()
                    )
                }
            else:
                # Use recent data if seasonal not available
                if not recent_data.empty:
                    forecast = {
                        'temperature_min': recent_data['temperature_min'].mean(),
                        'temperature_max': recent_data['temperature_max'].mean(),
                        'temperature_avg': recent_data['temperature_avg'].mean(),
                        'precipitation': recent_data['precipitation'].mean(),
                        'condition': estimate_condition(
                            recent_data['temperature_avg'].mean(), 
                            recent_data['precipitation'].mean()
                        )
                    }
                else:
                    # No data available
                    logger.warning(f"No data available for forecast on {target_date}")
                    return None
        
        # Blend with recent trends if available
        if not recent_data.empty:
            # Calculate recent temperature anomaly (difference from normal)
            if normal is not None:
                temp_anomaly = recent_data['temperature_avg'].mean() - normal['temperature_avg']
                precip_ratio = max(0, recent_data['precipitation'].mean() / max(0.1, normal['precipitation']))
            else:
                temp_anomaly = 0
                precip_ratio = 1
            
            # Apply anomaly to forecast (with dampening)
            forecast['temperature_min'] += temp_anomaly * 0.7
            forecast['temperature_max'] += temp_anomaly * 0.7
            forecast['temperature_avg'] += temp_anomaly * 0.7
            forecast['precipitation'] *= min(3, max(0.3, precip_ratio * 0.7 + 0.3))
            
            # Update condition based on adjusted values
            forecast['condition'] = estimate_condition(
                forecast['temperature_avg'], 
                forecast['precipitation']
            )
        
        # Apply persistence for very short-term forecasts (1-2 days)
        days_ahead = (target_date - datetime.now().date()).days
        if days_ahead <= 2 and not recent_data.empty:
            # Get most recent day
            most_recent = recent_data.iloc[-1]
            
            # Blend with persistence (more weight for closer days)
            persistence_weight = max(0, 1 - days_ahead * 0.4)
            forecast_weight = 1 - persistence_weight
            
            forecast['temperature_min'] = forecast['temperature_min'] * forecast_weight + most_recent['temperature_min'] * persistence_weight
            forecast['temperature_max'] = forecast['temperature_max'] * forecast_weight + most_recent['temperature_max'] * persistence_weight
            forecast['temperature_avg'] = forecast['temperature_avg'] * forecast_weight + most_recent['temperature_avg'] * persistence_weight
            forecast['precipitation'] = forecast['precipitation'] * forecast_weight + most_recent['precipitation'] * persistence_weight
            
            # Update condition
            forecast['condition'] = estimate_condition(
                forecast['temperature_avg'], 
                forecast['precipitation']
            )
        
        return forecast
    
    except Exception as e:
        logger.error(f"Error generating daily forecast: {str(e)}")
        return None

def generate_weekly_forecast(historical_df, normals_df, start_date, days=7):
    """
    Generate a weekly weather forecast
    
    Args:
        historical_df: DataFrame with historical daily weather data
        normals_df: DataFrame with climate normals
        start_date: Start date for the forecast
        days: Number of days to forecast
    
    Returns:
        Dictionary with forecast data for each day
    """
    try:
        # Convert start_date to datetime if it's not already
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Generate forecast for each day
        forecasts = {}
        for i in range(days):
            target_date = start_date + timedelta(days=i)
            daily_forecast = generate_daily_forecast(historical_df, normals_df, target_date)
            
            if daily_forecast:
                forecasts[target_date] = daily_forecast
        
        # Apply smoothing to the forecast
        if len(forecasts) > 1:
            dates = sorted(forecasts.keys())
            
            # Smooth temperature with a 3-day moving average
            for i in range(1, len(dates) - 1):
                prev_date = dates[i - 1]
                curr_date = dates[i]
                next_date = dates[i + 1]
                
                for field in ['temperature_min', 'temperature_max', 'temperature_avg']:
                    forecasts[curr_date][field] = (
                        forecasts[prev_date][field] * 0.25 +
                        forecasts[curr_date][field] * 0.5 +
                        forecasts[next_date][field] * 0.25
                    )
            
            # Ensure min <= avg <= max
            for date in dates:
                forecasts[date]['temperature_avg'] = min(
                    forecasts[date]['temperature_max'],
                    max(forecasts[date]['temperature_min'], forecasts[date]['temperature_avg'])
                )
        
        return forecasts
    
    except Exception as e:
        logger.error(f"Error generating weekly forecast: {str(e)}")
        return {}

def estimate_condition(temperature, precipitation):
    """
    Estimate weather condition based on temperature and precipitation
    
    Args:
        temperature: Average temperature in Celsius
        precipitation: Precipitation in mm
    
    Returns:
        Condition code (integer)
    """
    # Condition codes (simplified):
    # 1: Clear/Sunny
    # 2: Partly Cloudy
    # 3: Cloudy
    # 4: Rain
    # 5: Thunderstorm
    # 6: Snow
    # 7: Fog
    
    # Default to partly cloudy
    condition = 2
    
    # Check for precipitation
    if precipitation is None or pd.isna(precipitation):
        return condition
    
    if precipitation > 10:
        # Heavy rain or snow
        if temperature is not None and not pd.isna(temperature) and temperature < 2:
            return 6  # Snow
        else:
            return 5  # Thunderstorm
    elif precipitation > 1:
        # Light rain or snow
        if temperature is not None and not pd.isna(temperature) and temperature < 2:
            return 6  # Snow
        else:
            return 4  # Rain
    elif precipitation > 0.1:
        # Very light rain or mostly cloudy
        return 3  # Cloudy
    
    # Check temperature for clear vs partly cloudy
    if temperature is not None and not pd.isna(temperature):
        if temperature > 25:
            return 1  # Clear/Sunny
    
    return condition 