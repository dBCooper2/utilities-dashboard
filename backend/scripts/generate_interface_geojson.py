#!/usr/bin/env python
"""
Script to generate GeoJSON for zone interfaces.

This script calculates centroids for zones and creates a GeoJSON file
with LineString features representing the interfaces between zones.
"""

import os
import sys
import json
import logging
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.energy import Zone, ZoneInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def generate_interface_geojson(db: Session, output_file="zone_interfaces.geojson"):
    """
    Generate GeoJSON for zone interfaces
    
    Args:
        db: Database session
        output_file: Path to the output GeoJSON file
    """
    # Get all interfaces
    interfaces = db.query(ZoneInterface).filter(ZoneInterface.is_active == 1).all()
    logger.info(f"Found {len(interfaces)} zone interfaces")
    
    # Build GeoJSON features
    features = []
    
    for interface in interfaces:
        # Get zones
        from_zone = interface.from_zone
        to_zone = interface.to_zone
        
        if not from_zone or not to_zone:
            logger.warning(f"Missing zones for interface {interface.id}")
            continue
            
        logger.info(f"Processing interface {interface.id}: {from_zone.code} -> {to_zone.code}")
        
        if not from_zone.geojson or not to_zone.geojson:
            logger.warning(f"Missing GeoJSON for zones in interface {interface.id} ({interface.name})")
            continue
        
        # Calculate centroids
        try:
            # Extract centroids using the improved function
            from_centroid = calculate_centroid(from_zone.geojson)
            to_centroid = calculate_centroid(to_zone.geojson)
            
            if not from_centroid:
                logger.warning(f"Failed to calculate centroid for zone {from_zone.code}")
                continue
            
            if not to_centroid:
                logger.warning(f"Failed to calculate centroid for zone {to_zone.code}")
                continue
            
            logger.info(f"Calculated centroids: {from_zone.code}={from_centroid}, {to_zone.code}={to_centroid}")
            
            # Create LineString feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [from_centroid, to_centroid]
                },
                "properties": {
                    "id": interface.id,
                    "name": interface.name,
                    "capacity": interface.capacity,
                    "from_zone_id": from_zone.id,
                    "from_zone_code": from_zone.code,
                    "to_zone_id": to_zone.id,
                    "to_zone_code": to_zone.code,
                    "from_iso": from_zone.iso_rto,
                    "to_iso": to_zone.iso_rto,
                    "is_inter_iso": from_zone.iso_rto != to_zone.iso_rto
                }
            }
            
            features.append(feature)
            logger.info(f"Added feature for interface {interface.id}")
        except Exception as e:
            logger.error(f"Error creating feature for interface {interface.id}: {str(e)}")
    
    logger.info(f"Created {len(features)} GeoJSON features")
    
    # Create GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Write to file
    with open(output_file, "w") as f:
        json.dump(geojson, f, indent=2)
    
    logger.info(f"Wrote GeoJSON to {output_file}")
    
    return geojson

def main():
    """Main function"""
    # Get database session
    db = SessionLocal()
    
    try:
        # Generate GeoJSON
        generate_interface_geojson(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 