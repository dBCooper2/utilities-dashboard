import pandas as pd
from typing import List, Dict, Any, Callable, Union, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

def resample_time_series(
    data: List[Dict[str, Any]],
    timestamp_field: str = "timestamp",
    value_fields: Union[List[str], str] = None,
    interval: str = "15min",
    agg_func: str = "mean",
    custom_agg: Optional[Dict[str, Callable]] = None
) -> List[Dict[str, Any]]:
    """
    Resample time series data to a different interval
    
    Args:
        data: List of data points as dictionaries
        timestamp_field: Name of the timestamp field
        value_fields: Names of the value fields to aggregate (if None, all fields except timestamp are aggregated)
        interval: Time interval for resampling: 15min, hourly, daily, weekly, monthly
        agg_func: Aggregation function: mean, sum, min, max
        custom_agg: Custom aggregation functions for specific fields
    
    Returns:
        Resampled data as a list of dictionaries
    """
    if not data:
        return []
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Set timestamp as index for resampling
    df.set_index(timestamp_field, inplace=True)
    
    # Determine value fields if not specified
    if value_fields is None:
        value_fields = list(df.columns)
    elif isinstance(value_fields, str):
        value_fields = [value_fields]
    
    # Map interval string to pandas frequency
    freq_map = {
        "15min": "15min",
        "hourly": "1H",
        "daily": "1D",
        "weekly": "1W",
        "monthly": "1M"
    }
    
    freq = freq_map.get(interval, "15min")
    
    # Map aggregation function string to pandas function
    agg_map = {
        "mean": "mean",
        "sum": "sum",
        "min": "min",
        "max": "max",
        "count": "count",
        "median": "median",
        "first": "first",
        "last": "last"
    }
    
    # Determine aggregation function
    pd_agg_func = agg_map.get(agg_func, "mean")
    
    # Create aggregation dictionary for each field
    agg_dict = {field: pd_agg_func for field in value_fields}
    
    # Override with custom aggregation functions if provided
    if custom_agg:
        agg_dict.update(custom_agg)
    
    try:
        # Resample based on requested interval and aggregation
        resampled = df.resample(freq).agg(agg_dict)
        
        # Convert back to records
        return resampled.reset_index().to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error resampling time series data: {str(e)}")
        # If resampling fails, return original data
        df.reset_index(inplace=True)
        return df.to_dict(orient="records")

def aggregate_grouped_time_series(
    grouped_data: Dict[str, Dict[str, Any]],
    interval: str = "15min",
    agg_func: str = "mean"
) -> Dict[str, Dict[str, Any]]:
    """
    Resample grouped time series data to a different interval
    
    Args:
        grouped_data: Dictionary of group_id -> {timestamp -> value}
        interval: Time interval for resampling: 15min, hourly, daily, weekly, monthly
        agg_func: Aggregation function: mean, sum, min, max
    
    Returns:
        Resampled grouped data
    """
    if not grouped_data:
        return {}
    
    # Map interval string to pandas frequency
    freq_map = {
        "15min": "15min",
        "hourly": "1H",
        "daily": "1D",
        "weekly": "1W",
        "monthly": "1M"
    }
    
    freq = freq_map.get(interval, "15min")
    
    # Map aggregation function string to pandas function
    agg_map = {
        "mean": "mean",
        "sum": "sum",
        "min": "min",
        "max": "max"
    }
    
    pd_agg_func = agg_map.get(agg_func, "mean")
    
    result = {}
    
    # Process each group
    for group_id, data in grouped_data.items():
        try:
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index", columns=["value"])
            df.index = pd.DatetimeIndex(df.index)
            
            # Resample based on requested interval
            resampled = df.resample(freq).agg(pd_agg_func)
            
            # Convert back to dictionary
            result[group_id] = resampled["value"].to_dict()
        except Exception as e:
            logger.error(f"Error resampling grouped time series for {group_id}: {str(e)}")
            result[group_id] = data
    
    return result 