from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import logging
import os
import json

from app.db.database import get_db
from app.models.energy import Zone, LBMP, Load, FuelMix, InterfaceFlow, ZoneInterface, ZoneInterfaceFlow
from app.etl.energy import update_energy_data
from app.utils.geojson import generate_state_geojson, get_all_states, generate_all_state_geojsons, calculate_centroid
from app.utils.time_aggregation import resample_time_series, aggregate_grouped_time_series

# Configure logging
logger = logging.getLogger(__name__)

# Define renewable fuel types
RENEWABLE_FUEL_TYPES = ["WND", "SUN", "WAT", "OTH"]  # Wind, Solar, Hydro, Other renewables

def is_renewable(fuel_type: str) -> bool:
    """
    Check if a fuel type is considered renewable
    
    Args:
        fuel_type: The fuel type code (e.g., WND, SUN, NG, COL)
        
    Returns:
        True if the fuel type is considered renewable (Wind, Solar, Hydro, Other renewables)
    """
    return fuel_type in RENEWABLE_FUEL_TYPES

router = APIRouter()

@router.get("/zones")
async def get_zones(
    state: Optional[str] = Query(None, description="Filter by state"),
    iso_rto: Optional[str] = Query(None, description="Filter by ISO/RTO"),
    db: Session = Depends(get_db)
):
    """Get all zones with optional filters"""
    query = db.query(Zone)
    
    if state:
        query = query.filter(Zone.state == state)
    if iso_rto:
        query = query.filter(Zone.iso_rto == iso_rto)
    
    zones = query.all()
    return zones

@router.get("/zone/{zone_code}")
async def get_zone_details(
    zone_code: str,
    db: Session = Depends(get_db)
):
    """Get details for a specific zone"""
    zone = db.query(Zone).filter(Zone.code == zone_code).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    return zone

@router.get("/lbmp/{zone_code}")
async def get_lbmp_data(
    zone_code: str,
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    type: str = Query("DA", description="LBMP type: DA (Day Ahead) or RT (Real Time)"),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get LBMP data for a zone within a time range
    
    This endpoint returns Locational Based Marginal Price data for the specified zone.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, min, max).
    """
    # Get the zone
    zone = db.query(Zone).filter(Zone.code == zone_code).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Build the query
    query = db.query(LBMP).filter(
        LBMP.zone_id == zone.id,
        LBMP.type == type
    )
    
    # Add time filters if provided
    if start_time:
        query = query.filter(LBMP.timestamp >= start_time)
    if end_time:
        query = query.filter(LBMP.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    lbmp_data = query.order_by(LBMP.timestamp).all()
    
    # Convert to list of dictionaries for resampling
    data = [{
        "timestamp": ld.timestamp,
        "price": ld.price,
        "congestion": ld.congestion,
        "losses": ld.losses
    } for ld in lbmp_data]
    
    # Resample if needed and if data exists
    if interval != "15min" and data:
        data = resample_time_series(
            data=data,
            timestamp_field="timestamp",
            value_fields=["price", "congestion", "losses"],
            interval=interval,
            agg_func=agg_func
        )
    
    return {
        "zone": zone,
        "lbmp_data": data,
        "type": type,
        "interval": interval,
        "aggregation": agg_func
    }

@router.get("/load/{zone_code}")
async def get_load_data(
    zone_code: str,
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    type: str = Query("D", description="Load type: D (Demand), F (Forecast), etc."),
    include_losses: bool = Query(False, description="Include load with losses"),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, sum, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get load data for a zone within a time range
    
    This endpoint returns load data for the specified zone.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, sum, min, max).
    """
    # Get the zone
    zone = db.query(Zone).filter(Zone.code == zone_code).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Build the query
    query = db.query(Load).filter(
        Load.zone_id == zone.id,
        Load.type == type
    )
    
    # Add time filters if provided
    if start_time:
        query = query.filter(Load.timestamp >= start_time)
    if end_time:
        query = query.filter(Load.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    load_data = query.order_by(Load.timestamp).all()
    
    # Convert to list of dictionaries for resampling
    data = []
    for ld in load_data:
        item = {
            "timestamp": ld.timestamp,
            "value": ld.value
        }
        if include_losses:
            item["with_losses"] = ld.with_losses
        data.append(item)
    
    # Resample if needed and if data exists
    if interval != "15min" and data:
        value_fields = ["value"]
        if include_losses:
            value_fields.append("with_losses")
            
        data = resample_time_series(
            data=data,
            timestamp_field="timestamp",
            value_fields=value_fields,
            interval=interval,
            agg_func=agg_func
        )
    
    return {
        "zone": zone,
        "load_data": data,
        "type": type,
        "interval": interval,
        "aggregation": agg_func,
        "include_losses": include_losses
    }

@router.get("/fuel-mix")
async def get_fuel_mix(
    iso_rto: str = Query(..., description="ISO/RTO code (SERC, FRCC, PJM, MISO, SPP)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    fuel_types: List[str] = Query(None, description="Filter by fuel types (COL, NG, NUC, WND, SUN, etc.)"),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, sum, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get fuel mix data within a time range
    
    This endpoint returns fuel mix data for the specified ISO/RTO and optional state.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, sum, min, max).
    """
    # Build the query
    query = db.query(FuelMix).filter(FuelMix.iso_rto == iso_rto)
    
    # Add filters if provided
    if state:
        query = query.filter(FuelMix.state == state)
    if start_time:
        query = query.filter(FuelMix.timestamp >= start_time)
    if end_time:
        query = query.filter(FuelMix.timestamp <= end_time)
    if fuel_types:
        query = query.filter(FuelMix.fuel_type.in_(fuel_types))
    
    # Execute the query and sort by timestamp
    fuel_mix_data = query.order_by(FuelMix.timestamp).all()
    
    # Group data by fuel type and timestamp
    fuel_data = {}
    for fm in fuel_mix_data:
        ts = fm.timestamp.isoformat()
        if fm.fuel_type not in fuel_data:
            fuel_data[fm.fuel_type] = {}
        fuel_data[fm.fuel_type][ts] = fm.generation
    
    # Resample if needed and if data exists
    if interval != "15min" and fuel_mix_data:
        fuel_data = aggregate_grouped_time_series(
            grouped_data=fuel_data,
            interval=interval,
            agg_func=agg_func
        )
    
    return {
        "iso_rto": iso_rto,
        "state": state,
        "fuel_mix_data": fuel_data,
        "interval": interval,
        "aggregation": agg_func
    }

@router.get("/renewable-fuel-mix")
async def get_renewable_fuel_mix(
    iso_rto: str = Query(..., description="ISO/RTO code (SERC, FRCC, PJM, MISO, SPP)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    include_details: bool = Query(True, description="Include details for each renewable fuel type"),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, sum, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get renewable fuel mix data within a time range
    
    This endpoint returns only renewable fuel mix data (Wind, Solar, Hydro, and other renewables)
    for the specified ISO/RTO and optional state.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, sum, min, max).
    """
    # Build the query
    query = db.query(FuelMix).filter(
        FuelMix.iso_rto == iso_rto,
        FuelMix.fuel_type.in_(RENEWABLE_FUEL_TYPES)
    )
    
    # Add filters if provided
    if state:
        query = query.filter(FuelMix.state == state)
    if start_time:
        query = query.filter(FuelMix.timestamp >= start_time)
    if end_time:
        query = query.filter(FuelMix.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    fuel_mix_data = query.order_by(FuelMix.timestamp).all()
    
    # Group data by fuel type and timestamp
    fuel_data = {}
    total_data = {}
    
    for fm in fuel_mix_data:
        ts = fm.timestamp.isoformat()
        
        # Store data by fuel type
        if fm.fuel_type not in fuel_data:
            fuel_data[fm.fuel_type] = {}
        fuel_data[fm.fuel_type][ts] = fm.generation
        
        # Store total renewable data
        if ts not in total_data:
            total_data[ts] = 0
        total_data[ts] += fm.generation
    
    # Resample if needed and if data exists
    if interval != "15min" and fuel_mix_data:
        fuel_data = aggregate_grouped_time_series(
            grouped_data=fuel_data,
            interval=interval,
            agg_func=agg_func
        )
        
        # Create a dictionary for total data to use with the aggregation function
        total_data_dict = {"total": total_data}
        total_data_agg = aggregate_grouped_time_series(
            grouped_data=total_data_dict,
            interval=interval,
            agg_func=agg_func
        )
        total_data = total_data_agg["total"] if "total" in total_data_agg else {}
    
    result = {
        "iso_rto": iso_rto,
        "state": state,
        "interval": interval,
        "aggregation": agg_func,
        "total_renewable": total_data
    }
    
    # Include individual renewable fuel type data if requested
    if include_details:
        result["renewable_fuel_mix_data"] = fuel_data
    
    return result

@router.get("/is-renewable")
async def is_fuel_type_renewable(fuel_type: str):
    """
    Check if a fuel type is considered renewable
    
    Returns True if the fuel type is considered renewable (Wind, Solar, Hydro, Other renewables)
    """
    return {"fuel_type": fuel_type, "is_renewable": is_renewable(fuel_type)}

@router.get("/interface-flow")
async def get_interface_flow(
    from_iso_rto: str = Query(..., description="From ISO/RTO code"),
    to_iso_rto: str = Query(..., description="To ISO/RTO code"),
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    interval: str = Query("15min", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, sum, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get interface flow data between regions within a time range
    
    This endpoint returns power flow data between the specified ISO/RTOs.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, sum, min, max).
    """
    # Build the query
    query = db.query(InterfaceFlow).filter(
        InterfaceFlow.from_iso_rto == from_iso_rto,
        InterfaceFlow.to_iso_rto == to_iso_rto
    )
    
    # Add time filters if provided
    if start_time:
        query = query.filter(InterfaceFlow.timestamp >= start_time)
    if end_time:
        query = query.filter(InterfaceFlow.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    flow_data = query.order_by(InterfaceFlow.timestamp).all()
    
    # Convert to list of dictionaries for resampling
    data = [{
        "timestamp": fd.timestamp,
        "value": fd.value
    } for fd in flow_data]
    
    # Resample if needed and if data exists
    if interval != "15min" and data:
        data = resample_time_series(
            data=data,
            timestamp_field="timestamp",
            value_fields=["value"],
            interval=interval,
            agg_func=agg_func
        )
    
    return {
        "from_iso_rto": from_iso_rto,
        "to_iso_rto": to_iso_rto,
        "flow_data": data,
        "interval": interval,
        "aggregation": agg_func
    }

@router.post("/update")
async def trigger_energy_update(db: Session = Depends(get_db)):
    """Manually trigger an energy data update"""
    try:
        update_energy_data(db)
        return {"status": "success", "message": "Energy data update completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating energy data: {str(e)}")

@router.get("/states")
async def get_all_state_codes(db: Session = Depends(get_db)):
    """Get all available state codes for states with zones"""
    states = get_all_states(db)
    return {"states": states}

@router.get("/state-geojson/{state_code}")
async def get_state_geojson(
    state_code: str,
    db: Session = Depends(get_db)
):
    """
    Get GeoJSON for a specific state with its zones
    
    This endpoint returns a GeoJSON FeatureCollection where each feature represents a zone
    within the specified state. The GeoJSON can be used directly by frontend mapping libraries
    like Mapbox GL JS or Leaflet to display state boundaries with zone divisions.
    """
    geojson = generate_state_geojson(db, state_code)
    
    if not geojson:
        raise HTTPException(status_code=404, detail=f"No GeoJSON data found for state {state_code}")
    
    return geojson

@router.get("/all-state-geojsons")
async def get_all_state_geojsons(db: Session = Depends(get_db)):
    """
    Get GeoJSON for all states with their zones
    
    This endpoint returns a dictionary where each key is a state code and the value
    is a GeoJSON FeatureCollection for that state.
    """
    state_geojsons = generate_all_state_geojsons(db)
    
    if not state_geojsons:
        raise HTTPException(status_code=404, detail="No GeoJSON data found for any states")
    
    return state_geojsons

@router.get("/zone-geojson/{zone_id}")
async def get_zone_geojson(
    zone_id: str,
    db: Session = Depends(get_db)
):
    """
    Get raw GeoJSON for a specific zone
    
    This endpoint returns the raw GeoJSON data for a specific zone as stored in the database.
    This is useful for debugging or direct visualization of a single zone.
    """
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone with ID {zone_id} not found")
    
    if not zone.geojson:
        raise HTTPException(status_code=404, detail=f"No GeoJSON data found for zone {zone_id}")
    
    return zone.geojson

@router.get("/zone-interfaces")
async def get_zone_interfaces(
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get zone interfaces with optional filters
    
    This endpoint returns zone interface data, which represents connections between
    individual zones. This is more granular than the interface flow between ISOs/RTOs.
    """
    query = db.query(ZoneInterface)
    
    if zone_id:
        # Get interfaces where the zone is either the source or destination
        query = query.filter((ZoneInterface.from_zone_id == zone_id) | (ZoneInterface.to_zone_id == zone_id))
    
    if is_active:
        query = query.filter(ZoneInterface.is_active == 1)
    
    interfaces = query.all()
    
    # Transform data to include zone names
    result = []
    for interface in interfaces:
        result.append({
            "id": interface.id,
            "name": interface.name,
            "from_zone": {
                "id": interface.from_zone.id,
                "code": interface.from_zone.code,
                "name": interface.from_zone.name,
                "iso_rto": interface.from_zone.iso_rto
            },
            "to_zone": {
                "id": interface.to_zone.id,
                "code": interface.to_zone.code,
                "name": interface.to_zone.name,
                "iso_rto": interface.to_zone.iso_rto
            },
            "capacity": interface.capacity,
            "is_active": interface.is_active == 1
        })
    
    return result

@router.get("/zone-interface-flow/{interface_id}")
async def get_zone_interface_flow(
    interface_id: int,
    start_time: datetime = Query(None, description="Start timestamp"),
    end_time: datetime = Query(None, description="End timestamp"),
    interval: str = Query("hourly", description="Time interval: 15min, hourly, daily, weekly, monthly"),
    agg_func: str = Query("mean", description="Aggregation function: mean, sum, min, max"),
    db: Session = Depends(get_db)
):
    """
    Get flow data for a specific zone interface
    
    This endpoint returns power flow data for a specific zone-to-zone interface.
    The data can be aggregated to different time intervals (15min, hourly, daily, weekly, monthly)
    using different aggregation functions (mean, sum, min, max).
    """
    # Check if interface exists
    interface = db.query(ZoneInterface).filter(ZoneInterface.id == interface_id).first()
    
    if not interface:
        raise HTTPException(status_code=404, detail=f"Zone interface with ID {interface_id} not found")
    
    # Build the query
    query = db.query(ZoneInterfaceFlow).filter(ZoneInterfaceFlow.interface_id == interface_id)
    
    # Add time filters if provided
    if start_time:
        query = query.filter(ZoneInterfaceFlow.timestamp >= start_time)
    if end_time:
        query = query.filter(ZoneInterfaceFlow.timestamp <= end_time)
    
    # Execute the query and sort by timestamp
    flow_data = query.order_by(ZoneInterfaceFlow.timestamp).all()
    
    # Convert to list of dictionaries for resampling
    data = [{
        "timestamp": fd.timestamp,
        "value": fd.value,
        "congestion": fd.congestion
    } for fd in flow_data]
    
    # Resample if needed and if data exists
    if interval != "hourly" and data:
        data = resample_time_series(
            data=data,
            timestamp_field="timestamp",
            value_fields=["value", "congestion"],
            interval=interval,
            agg_func=agg_func
        )
    
    interface_details = {
        "id": interface.id,
        "name": interface.name,
        "from_zone": {
            "id": interface.from_zone.id,
            "code": interface.from_zone.code,
            "name": interface.from_zone.name,
            "iso_rto": interface.from_zone.iso_rto
        },
        "to_zone": {
            "id": interface.to_zone.id,
            "code": interface.to_zone.code,
            "name": interface.to_zone.name,
            "iso_rto": interface.to_zone.iso_rto
        },
        "capacity": interface.capacity
    }
    
    return {
        "interface": interface_details,
        "flow_data": data,
        "interval": interval,
        "aggregation": agg_func
    }

@router.get("/zone-interfaces-geojson")
async def get_zone_interfaces_geojson():
    """
    Get GeoJSON for zone interfaces.
    
    Returns a GeoJSON FeatureCollection with LineString features representing the interfaces between zones.
    Each feature has properties with information about the interface.
    """
    logger.info("Getting zone interfaces GeoJSON")
    
    # Return a minimal GeoJSON response for testing
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-78.08, 35.18],
                        [-82.60, 35.60]
                    ]
                },
                "properties": {
                    "id": 1,
                    "name": "Test Interface"
                }
            }
        ]
    }

@router.get("/test-centroid/{zone_id}")
async def test_centroid_calculation(
    zone_id: int,
    db: Session = Depends(get_db)
):
    """
    Test endpoint to verify centroid calculation for a zone
    
    This endpoint returns the centroid coordinates for a specific zone.
    """
    # Get the zone
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone with ID {zone_id} not found")
    
    if not zone.geojson:
        raise HTTPException(status_code=404, detail=f"No GeoJSON data found for zone {zone_id}")
    
    # Calculate centroid
    centroid = calculate_centroid(zone.geojson)
    
    return {
        "zone_id": zone.id,
        "zone_code": zone.code,
        "centroid": centroid,
        "geojson_type": zone.geojson.get("type") if isinstance(zone.geojson, dict) else "unknown"
    }

@router.get("/test-json")
async def test_json():
    """
    Test endpoint that returns a simple JSON response.
    """
    logger.info("Test JSON endpoint called")
    return {"message": "This is a test JSON response"} 