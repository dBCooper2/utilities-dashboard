import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def interpolate_to_15min(hourly_df, daily_df=None, normals_df=None):
    """
    Interpolate hourly weather data to 15-minute intervals
    
    Args:
        hourly_df: DataFrame with hourly weather data
        daily_df: DataFrame with daily weather data (optional)
        normals_df: DataFrame with climate normals (optional)
    
    Returns:
        DataFrame with 15-minute weather data
    """
    if hourly_df.empty:
        return pd.DataFrame()
    
    # Create a 15-minute time range
    start_time = hourly_df.index.min()
    end_time = hourly_df.index.max()
    time_range = pd.date_range(start=start_time, end=end_time, freq='15min')
    
    # Create an empty DataFrame with the time range
    df_15min = pd.DataFrame(index=time_range)
    
    # Interpolate numeric columns
    numeric_columns = ['temperature', 'feels_like', 'humidity', 'precipitation', 
                       'snow', 'wind_speed', 'pressure', 'cloud_cover']
    
    for col in numeric_columns:
        if col in hourly_df.columns:
            # Use cubic spline interpolation for temperature and feels_like
            if col in ['temperature', 'feels_like']:
                df_15min[col] = hourly_df[col].reindex(df_15min.index).interpolate(method='cubic')
            # Use linear interpolation for other numeric columns
            else:
                df_15min[col] = hourly_df[col].reindex(df_15min.index).interpolate(method='linear')
    
    # Handle non-numeric columns (forward fill)
    non_numeric_columns = ['wind_direction', 'condition']
    for col in non_numeric_columns:
        if col in hourly_df.columns:
            df_15min[col] = hourly_df[col].reindex(df_15min.index).ffill()
    
    # Apply constraints from daily data if available
    if daily_df is not None and not daily_df.empty:
        # Ensure temperature stays within daily min/max bounds
        for date, row in daily_df.iterrows():
            # Convert date to datetime
            date_start = datetime.combine(date, datetime.min.time())
            date_end = date_start + timedelta(days=1)
            
            # Get mask for this date
            mask = (df_15min.index >= date_start) & (df_15min.index < date_end)
            
            # Apply min/max constraints
            if 'temperature' in df_15min.columns and 'temperature_min' in row and 'temperature_max' in row:
                if not pd.isna(row['temperature_min']) and not pd.isna(row['temperature_max']):
                    # Clip temperatures to daily min/max
                    df_15min.loc[mask, 'temperature'] = df_15min.loc[mask, 'temperature'].clip(
                        lower=row['temperature_min'], upper=row['temperature_max']
                    )
            
            # Distribute daily precipitation if available
            if 'precipitation' in df_15min.columns and 'precipitation' in row:
                if not pd.isna(row['precipitation']) and row['precipitation'] > 0:
                    # Get sum of interpolated precipitation for the day
                    day_sum = df_15min.loc[mask, 'precipitation'].sum()
                    
                    if day_sum > 0:
                        # Scale to match daily total
                        scale_factor = row['precipitation'] / day_sum
                        df_15min.loc[mask, 'precipitation'] *= scale_factor
                    else:
                        # If no precipitation in hourly data but daily shows precipitation,
                        # distribute evenly across the day
                        df_15min.loc[mask, 'precipitation'] = row['precipitation'] / len(df_15min.loc[mask])
    
    # Apply diurnal patterns based on climate normals if available
    if normals_df is not None and not normals_df.empty:
        # Create a lookup dictionary for normals by month and day
        normals_lookup = {}
        for _, row in normals_df.iterrows():
            key = (row['month'], row['day'])
            normals_lookup[key] = row
        
        # Apply diurnal temperature patterns
        for idx, _ in df_15min.iterrows():
            month, day = idx.month, idx.day
            hour = idx.hour + idx.minute / 60  # Hour as float (e.g., 14.5 for 14:30)
            
            # Get climate normal for this day
            normal = normals_lookup.get((month, day))
            
            if normal is not None and 'temperature' in df_15min.columns:
                # Get daily min/max from normals
                normal_min = normal.get('temperature_min')
                normal_max = normal.get('temperature_max')
                
                if not pd.isna(normal_min) and not pd.isna(normal_max):
                    # Calculate typical diurnal pattern (sinusoidal)
                    # Minimum temperature typically occurs around 6 AM
                    # Maximum temperature typically occurs around 3 PM
                    min_hour = 6
                    max_hour = 15
                    
                    # Calculate where in the diurnal cycle this hour falls
                    if hour < min_hour:
                        # Late night to early morning (decreasing to minimum)
                        factor = 0.5 + 0.5 * np.cos(np.pi * (hour + 24 - max_hour) / (min_hour + 24 - max_hour))
                    elif hour < max_hour:
                        # Morning to afternoon (increasing to maximum)
                        factor = 0.5 - 0.5 * np.cos(np.pi * (hour - min_hour) / (max_hour - min_hour))
                    else:
                        # Afternoon to evening (decreasing from maximum)
                        factor = 0.5 + 0.5 * np.cos(np.pi * (hour - max_hour) / (min_hour + 24 - max_hour))
                    
                    # Get the actual temperature from interpolation
                    actual_temp = df_15min.at[idx, 'temperature']
                    
                    # Blend with diurnal pattern (70% actual, 30% pattern)
                    pattern_temp = normal_min + factor * (normal_max - normal_min)
                    df_15min.at[idx, 'temperature'] = 0.7 * actual_temp + 0.3 * pattern_temp
    
    # Ensure no negative values for certain fields
    for col in ['precipitation', 'snow', 'humidity', 'cloud_cover']:
        if col in df_15min.columns:
            df_15min[col] = df_15min[col].clip(lower=0)
    
    # Cap humidity and cloud cover at 100%
    for col in ['humidity', 'cloud_cover']:
        if col in df_15min.columns:
            df_15min[col] = df_15min[col].clip(upper=100)
    
    return df_15min 