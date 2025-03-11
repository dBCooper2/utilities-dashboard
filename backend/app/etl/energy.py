import os
import logging
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.energy import Zone, LBMP, Load, FuelMix, InterfaceFlow

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Get API key from environment
EIA_API_KEY = os.getenv("EIA_API_KEY")

def fetch_energy_data(db: Session, days_back: int = 30):
    """
    Fetch energy data from EIA API
    
    Args:
        db: Database session
        days_back: Number of days to fetch data for (from today backwards)
    """
    if not EIA_API_KEY:
        logger.error("EIA API key not found in environment variables")
        return
    
    # Get all zones from the database
    zones = db.query(Zone).all()
    
    if not zones:
        logger.warning("No zones found in the database")
        return
    
    # Set time period
    end = datetime.now()
    start = end - timedelta(days=days_back)
    
    # Format dates for API
    start_str = start.strftime("%Y-%m-%dT00")
    end_str = end.strftime("%Y-%m-%dT00")
    
    # Fetch data for each zone
    for zone in zones:
        logger.info(f"Fetching energy data for {zone.code} ({zone.name})")
        
        # Fetch LBMP data
        fetch_lbmp_data(db, zone, start_str, end_str)
        
        # Fetch load data
        fetch_load_data(db, zone, start_str, end_str)
    
    # Fetch fuel mix data for each ISO/RTO
    iso_rtos = set(zone.iso_rto for zone in zones)
    for iso_rto in iso_rtos:
        logger.info(f"Fetching fuel mix data for {iso_rto}")
        fetch_fuel_mix_data(db, iso_rto, start_str, end_str)
    
    # Fetch interface flow data between ISO/RTOs
    for from_iso in iso_rtos:
        for to_iso in iso_rtos:
            if from_iso != to_iso:
                logger.info(f"Fetching interface flow data from {from_iso} to {to_iso}")
                fetch_interface_flow_data(db, from_iso, to_iso, start_str, end_str)

def fetch_lbmp_data(db: Session, zone: Zone, start_str: str, end_str: str):
    """Fetch LBMP data from EIA API"""
    try:
        # Build API URL
        url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key={EIA_API_KEY}&frequency=hourly&data[0]=value&facets[type][]=LBMP&facets[respondent][]={zone.code}&start={start_str}&end={end_str}&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Error fetching LBMP data for {zone.code}: {response.status_code}")
            return
        
        # Parse response
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.error(f"Invalid response format for LBMP data for {zone.code}")
            return
        
        # Get the maximum ID from the database to start our counter
        max_id = db.query(func.max(LBMP.id)).scalar() or 0
        counter = max_id + 1
        
        # Convert to DataFrame for easier handling of missing values
        df = pd.DataFrame(data["response"]["data"])
        
        # Handle missing or invalid values
        if not df.empty:
            # Drop rows with missing crucial data
            df = df.dropna(subset=['period', 'value'])
            
            # Handle any remaining NaN values
            df = df.fillna({
                'value': df['value'].median(),  # Use median for price values
                'congestion': 0,                # Use 0 for missing congestion
                'losses': 0                     # Use 0 for missing losses
            })
        
        # Process each row
        for _, row in df.iterrows():
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(row["period"])
            except (ValueError, TypeError):
                continue
            
            # Check if data already exists
            existing = db.query(LBMP).filter(
                LBMP.zone_id == zone.id,
                LBMP.timestamp == timestamp,
                LBMP.type == "DA"  # Assume Day Ahead for now
            ).first()
            
            if existing:
                continue
            
            # Create new LBMP record
            lbmp = LBMP(
                id=counter,  # Set explicit ID
                zone_id=zone.id,
                timestamp=timestamp,
                type="DA",  # Assume Day Ahead for now
                price=row["value"],
                congestion=row.get("congestion", 0),  # Default to 0 if not available
                losses=row.get("losses", 0)  # Default to 0 if not available
            )
            
            db.add(lbmp)
            counter += 1
        
        db.commit()
        logger.info(f"Added LBMP data for {zone.code}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing LBMP data for {zone.code}: {str(e)}")

def fetch_load_data(db: Session, zone: Zone, start_str: str, end_str: str):
    """Fetch load data from EIA API"""
    try:
        # Build API URL
        url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key={EIA_API_KEY}&frequency=hourly&data[0]=value&facets[type][]=D&facets[respondent][]={zone.code}&start={start_str}&end={end_str}&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Error fetching load data for {zone.code}: {response.status_code}")
            return
        
        # Parse response
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.error(f"Invalid response format for load data for {zone.code}")
            return
        
        # Get the maximum ID from the database to start our counter
        max_id = db.query(func.max(Load.id)).scalar() or 0
        counter = max_id + 1
        
        # Convert to DataFrame for easier handling of missing values
        df = pd.DataFrame(data["response"]["data"])
        
        # Handle missing or invalid values
        if not df.empty:
            # Drop rows with missing crucial data
            df = df.dropna(subset=['period', 'value'])
            
            # Handle any remaining NaN values
            df = df.fillna({
                'value': df['value'].median(),  # Use median for load values
                'with_losses': None             # Keep as NULL if missing
            })
            
            # If with_losses is not provided, estimate it as 1.05 * value
            if 'with_losses' not in df.columns:
                df['with_losses'] = df['value'] * 1.05
        
        # Process each row
        for _, row in df.iterrows():
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(row["period"])
            except (ValueError, TypeError):
                continue
            
            # Check if data already exists
            existing = db.query(Load).filter(
                Load.zone_id == zone.id,
                Load.timestamp == timestamp,
                Load.type == "D"  # Demand
            ).first()
            
            if existing:
                continue
            
            # Create new load record
            load = Load(
                id=counter,  # Set explicit ID
                zone_id=zone.id,
                timestamp=timestamp,
                type="D",  # Demand
                value=row["value"],
                with_losses=row.get("with_losses", row["value"] * 1.05)  # Estimate if not available
            )
            
            db.add(load)
            counter += 1
        
        db.commit()
        logger.info(f"Added load data for {zone.code}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing load data for {zone.code}: {str(e)}")

def fetch_fuel_mix_data(db: Session, iso_rto: str, start_str: str, end_str: str):
    """Fetch fuel mix data from EIA API"""
    try:
        # Build API URL
        url = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
        
        # Set parameters
        params = {
            "api_key": EIA_API_KEY,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": iso_rto,
            "facets[fueltype][]": ["COL", "NG", "NUC", "WND", "SUN", "OIL", "WAT", "OTH"],
            "start": start_str,
            "end": end_str,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": 0,
            "length": 5000,
        }
        
        # Make API request
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Error fetching fuel mix data for {iso_rto}: {response.status_code}")
            return
        
        # Parse response
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.warning(f"No fuel mix data found for {iso_rto}")
            return
        
        # Process each data point
        for item in data["response"]["data"]:
            # Parse timestamp
            timestamp = datetime.strptime(item["period"], "%Y-%m-%dT%H")
            
            # Get fuel type
            fuel_type = item.get("fueltype", "OTH")
            
            # Check if data already exists
            existing = db.query(FuelMix).filter(
                FuelMix.iso_rto == iso_rto,
                FuelMix.timestamp == timestamp,
                FuelMix.fuel_type == fuel_type
            ).first()
            
            if existing:
                continue
            
            # Create new FuelMix record
            fuel_mix = FuelMix(
                iso_rto=iso_rto,
                state=None,  # No state-specific data from this endpoint
                timestamp=timestamp,
                fuel_type=fuel_type,
                generation=item.get("value")
            )
            
            db.add(fuel_mix)
        
        db.commit()
        logger.info(f"Added fuel mix data for {iso_rto}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching fuel mix data for {iso_rto}: {str(e)}")

def fetch_interface_flow_data(db: Session, from_iso: str, to_iso: str, start_str: str, end_str: str):
    """Fetch interface flow data from EIA API"""
    try:
        # Build API URL
        url = "https://api.eia.gov/v2/electricity/rto/interchange-data/data/"
        
        # Set parameters
        params = {
            "api_key": EIA_API_KEY,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": from_iso,
            "facets[fromba][]": from_iso,
            "facets[toba][]": to_iso,
            "start": start_str,
            "end": end_str,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": 0,
            "length": 5000,
        }
        
        # Make API request
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Error fetching interface flow data from {from_iso} to {to_iso}: {response.status_code}")
            return
        
        # Parse response
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.warning(f"No interface flow data found from {from_iso} to {to_iso}")
            return
        
        # Process each data point
        for item in data["response"]["data"]:
            # Parse timestamp
            timestamp = datetime.strptime(item["period"], "%Y-%m-%dT%H")
            
            # Check if data already exists
            existing = db.query(InterfaceFlow).filter(
                InterfaceFlow.from_iso_rto == from_iso,
                InterfaceFlow.to_iso_rto == to_iso,
                InterfaceFlow.timestamp == timestamp
            ).first()
            
            if existing:
                continue
            
            # Create new InterfaceFlow record
            flow = InterfaceFlow(
                timestamp=timestamp,
                from_iso_rto=from_iso,
                to_iso_rto=to_iso,
                value=item.get("value")
            )
            
            db.add(flow)
        
        db.commit()
        logger.info(f"Added interface flow data from {from_iso} to {to_iso}")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching interface flow data from {from_iso} to {to_iso}: {str(e)}")

def update_energy_data(db: Session, days_back: int = 30):
    """
    Update energy data from EIA API
    
    Args:
        db: Database session
        days_back: Number of days to fetch data for (from today backwards)
    """
    try:
        # Fetch energy data
        fetch_energy_data(db, days_back=days_back)
        return True
    except Exception as e:
        logger.error(f"Error updating energy data: {str(e)}")
        return False 