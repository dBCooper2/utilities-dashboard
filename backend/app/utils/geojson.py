import os
import json
import logging
from sqlalchemy.orm import Session
from app.models.energy import Zone

# Configure logging
logger = logging.getLogger(__name__)

def load_geojson(file_path):
    """
    Load GeoJSON data from a file
    
    Args:
        file_path: Path to the GeoJSON file
    
    Returns:
        GeoJSON data as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading GeoJSON file {file_path}: {str(e)}")
        return None

def import_zones_from_geojson(db: Session, file_path, iso_rto_mapping=None):
    """
    Import zones from a GeoJSON file
    
    Args:
        db: Database session
        file_path: Path to the GeoJSON file
        iso_rto_mapping: Dictionary mapping zone codes to ISO/RTO codes
    
    Returns:
        Number of zones imported
    """
    if not os.path.exists(file_path):
        logger.error(f"GeoJSON file not found: {file_path}")
        return 0
    
    # Load GeoJSON data
    geojson = load_geojson(file_path)
    if not geojson:
        return 0
    
    # Default ISO/RTO mapping if not provided
    if iso_rto_mapping is None:
        iso_rto_mapping = {
            # Florida (FRCC)
            "US-FLA-FMPP": "FRCC",
            "US-FLA-FPC": "FRCC",
            "US-FLA-FPL": "FRCC",
            "US-FLA-GVL": "FRCC",
            "US-FLA-HST": "FRCC",
            "US-FLA-JEA": "FRCC",
            "US-FLA-SEC": "FRCC",
            "US-FLA-TAL": "FRCC",
            "US-FLA-TEC": "FRCC",
            
            # Carolinas (SERC)
            "US-CAR-CPLE": "SERC",
            "US-CAR-CPLW": "SERC",
            "US-CAR-DUK": "SERC",
            "US-CAR-SC": "SERC",
            "US-CAR-SCEG": "SERC",
            
            # Tennessee and Central Southeast (SERC)
            "US-SE-SOCO": "SERC",
            "US-TEN-TVA": "SERC",
            
            # Kentucky and Midwest Connection
            "US-MIDW-LGEE": "MISO",
            
            # Arkansas and Central
            "US-CENT-SPA": "SPP",
            "US-CENT-SWPP": "SPP"
        }
    
    # Process features
    count = 0
    for feature in geojson.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        
        # Get zone code - check for both 'code' and 'zoneName' properties
        code = properties.get('code') or properties.get('zoneName')
        if not code:
            continue
        
        # Extract state from code (format: US-STATE-ZONE)
        state = None
        if code.startswith('US-') and len(code.split('-')) >= 2:
            state_code = code.split('-')[1]
            # Convert state codes to actual state names
            state_mapping = {
                'FLA': 'FL',
                'CAR': 'NC',  # Default to North Carolina for Carolinas
                'SE': 'GA',   # Default to Georgia for Southeast
                'TEN': 'TN',
                'MIDW': 'KY', # Default to Kentucky for Midwest
                'CENT': 'AR'  # Default to Arkansas for Central
            }
            state = state_mapping.get(state_code, state_code)
        
        # Check if zone already exists
        existing = db.query(Zone).filter(Zone.code == code).first()
        if existing:
            # Update existing zone
            existing.name = properties.get('name', properties.get('zoneName', existing.name))
            existing.state = properties.get('state', state or existing.state)
            existing.iso_rto = iso_rto_mapping.get(code, existing.iso_rto)
            existing.geojson = geometry
            count += 1
        else:
            # Create new zone
            zone = Zone(
                code=code,
                name=properties.get('name', properties.get('zoneName', code)),
                state=properties.get('state', state),
                iso_rto=iso_rto_mapping.get(code),
                geojson=geometry
            )
            db.add(zone)
            count += 1
    
    try:
        db.commit()
        logger.info(f"Imported {count} zones from GeoJSON")
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing zones from GeoJSON: {str(e)}")
        count = 0
    
    return count 

def generate_state_geojson(db: Session, state_code):
    """
    Generate GeoJSON for a specific state with its zones.
    
    Args:
        db: Database session
        state_code: State code (e.g., 'GA', 'FL', 'NC', etc.)
        
    Returns:
        GeoJSON data as a dictionary
    """
    # Get all zones for the specified state
    zones = db.query(Zone).filter(Zone.state == state_code).all()
    
    if not zones:
        logger.warning(f"No zones found for state {state_code}")
        return None
    
    # Create a FeatureCollection for the state
    state_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Add each zone as a feature
    for zone in zones:
        if not zone.geojson:
            logger.warning(f"Zone {zone.code} has no GeoJSON data")
            continue
            
        # Parse the zone's GeoJSON data
        try:
            # If zone.geojson is already a dict, use it directly
            if isinstance(zone.geojson, dict):
                zone_geojson = zone.geojson
            else:
                # Parse the JSON string
                zone_geojson = json.loads(zone.geojson)
                
            # Create a feature from the zone's GeoJSON
            feature = {
                "type": "Feature",
                "properties": {
                    "zone_id": zone.id,
                    "zone_code": zone.code,
                    "zone_name": zone.name,
                    "iso_rto": zone.iso_rto
                },
                "geometry": zone_geojson
            }
            
            # Add the feature to the state GeoJSON
            state_geojson["features"].append(feature)
            
        except Exception as e:
            logger.error(f"Error processing GeoJSON for zone {zone.code}: {str(e)}")
    
    # Check if we added any features
    if not state_geojson["features"]:
        logger.warning(f"No valid GeoJSON features found for state {state_code}")
        return None
        
    return state_geojson

def get_all_states(db: Session):
    """
    Get all unique states from the zones table
    
    Args:
        db: Database session
        
    Returns:
        List of state codes
    """
    states = db.query(Zone.state).distinct().all()
    return [state[0] for state in states if state[0]]  # Filter out None values

def generate_all_state_geojsons(db: Session):
    """
    Generate GeoJSON for all states with their zones
    
    Args:
        db: Database session
        
    Returns:
        Dictionary mapping state codes to their GeoJSON data
    """
    states = get_all_states(db)
    state_geojsons = {}
    
    for state in states:
        geojson = generate_state_geojson(db, state)
        if geojson:
            state_geojsons[state] = geojson
            
    return state_geojsons 

def calculate_centroid(geojson):
    """
    Calculate the centroid of a GeoJSON geometry.
    
    Supports Point, Polygon, and MultiPolygon geometry types.
    
    Args:
        geojson: A GeoJSON geometry object
        
    Returns:
        A [longitude, latitude] coordinate pair representing the centroid
    """
    logger.debug(f"Calculating centroid for GeoJSON: {str(geojson)[:50]}...")
    
    if not geojson:
        logger.warning("Empty GeoJSON provided")
        return None
    
    # Handle string GeoJSON
    if isinstance(geojson, str):
        try:
            geojson = json.loads(geojson)
        except Exception as e:
            logger.error(f"Error parsing GeoJSON string: {str(e)}")
            return None
    
    # If geojson is a complete feature with geometry property, extract the geometry
    if isinstance(geojson, dict) and "geometry" in geojson:
        geojson = geojson["geometry"]
    
    # Ensure we have the type property
    if not isinstance(geojson, dict) or "type" not in geojson:
        logger.warning(f"Invalid GeoJSON format: {str(geojson)[:50]}...")
        return None
    
    geometry_type = geojson["type"]
    logger.debug(f"GeoJSON geometry type: {geometry_type}")
    
    if geometry_type == "Point":
        # For Point, return the coordinates directly
        return geojson.get("coordinates")
    
    elif geometry_type == "Polygon":
        # For Polygon, calculate the centroid of the first (exterior) ring
        coordinates = geojson.get("coordinates", [[]])
        if not coordinates or not coordinates[0]:
            logger.warning("No coordinates found in Polygon GeoJSON")
            return None
        
        # Extract the exterior ring
        ring = coordinates[0]
        
        # Calculate centroid as the average of all coordinates
        sum_x = sum(coord[0] for coord in ring)
        sum_y = sum(coord[1] for coord in ring)
        count = len(ring)
        
        centroid = [sum_x / count, sum_y / count]
        logger.debug(f"Calculated Polygon centroid: {centroid}")
        return centroid
    
    elif geometry_type == "MultiPolygon":
        # For MultiPolygon, calculate the centroid of all polygons
        coordinates = geojson.get("coordinates", [])
        if not coordinates:
            logger.warning("No coordinates found in MultiPolygon GeoJSON")
            return None
        
        # Track the total area and weighted coordinates
        total_area = 0
        weighted_x = 0
        weighted_y = 0
        
        for polygon in coordinates:
            if not polygon or not polygon[0]:
                continue
                
            # Extract the exterior ring of this polygon
            ring = polygon[0]
            
            # Calculate simple centroid of this ring
            sum_x = sum(coord[0] for coord in ring)
            sum_y = sum(coord[1] for coord in ring)
            count = len(ring)
            
            # Simple area calculation (not geodesically accurate but sufficient for weighting)
            # Using a simple polygon area formula
            area = 0
            for i in range(len(ring) - 1):
                j = (i + 1) % len(ring)
                area += ring[i][0] * ring[j][1]
                area -= ring[j][0] * ring[i][1]
            area = abs(area) / 2
            
            # Weight the centroid by the polygon's area
            if area > 0:
                weighted_x += (sum_x / count) * area
                weighted_y += (sum_y / count) * area
                total_area += area
        
        # Return the weighted centroid
        if total_area > 0:
            centroid = [weighted_x / total_area, weighted_y / total_area]
            logger.debug(f"Calculated MultiPolygon centroid: {centroid}")
            return centroid
        else:
            logger.warning("Could not calculate area for MultiPolygon")
            return None
    
    # If it's another geometry type, try a fallback approach
    elif "coordinates" in geojson:
        coordinates = geojson.get("coordinates", [])
        if not coordinates:
            logger.warning(f"No coordinates found for geometry type {geometry_type}")
            return None
            
        # Flatten all coordinates and calculate average
        all_coords = []
        
        def extract_coords(coords):
            if not coords:
                return
            if isinstance(coords[0], (int, float)):
                all_coords.append(coords)
            else:
                for coord in coords:
                    extract_coords(coord)
        
        extract_coords(coordinates)
        
        if all_coords:
            sum_x = sum(coord[0] for coord in all_coords)
            sum_y = sum(coord[1] for coord in all_coords)
            count = len(all_coords)
            centroid = [sum_x / count, sum_y / count]
            logger.debug(f"Calculated fallback centroid for {geometry_type}: {centroid}")
            return centroid
    
    logger.warning(f"Unsupported geometry type: {geometry_type}")
    return None 