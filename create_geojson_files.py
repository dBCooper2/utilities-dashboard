#!/usr/bin/env python3
"""
Script to create GeoJSON files for the frontend.

This script generates:
1. A GeoJSON file for the entire southeast region with state lines and zones
2. Individual GeoJSON files for each state with their zones

All files are saved to the frontend/public directory for easy access.
"""

import os
import json
import logging
import copy
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
SOUTHEAST_REGIONS_PATH = "southeast_regions.geojson"
ZONE_INTERFACES_PATH = "zone_interfaces.geojson"
OUTPUT_DIR = "frontend/public/geojson"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_geojson(file_path):
    """Load GeoJSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading GeoJSON file {file_path}: {str(e)}")
        return None

def save_geojson(geojson_data, file_path):
    """Save GeoJSON data to a file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(geojson_data, f, indent=2)
        logger.info(f"Saved GeoJSON to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving GeoJSON to {file_path}: {str(e)}")
        return False

def extract_states_from_zones(zones_geojson):
    """
    Extract state information from zone properties.
    
    Returns a set of state codes found in the zones data.
    """
    states = set()
    
    for feature in zones_geojson.get("features", []):
        properties = feature.get("properties", {})
        zone_name = properties.get("zoneName", "")
        
        # Parse state code from zone name if possible
        # Example: US-CAR-CPLE -> CAR (Carolina)
        # Example: US-FLA-FPL -> FLA (Florida)
        if "-" in zone_name:
            parts = zone_name.split("-")
            if len(parts) >= 2:
                region_code = parts[1]
                if region_code == "CAR":
                    # Carolina regions could be NC or SC, need more specific parsing
                    if "NC" in zone_name or "DUK" in zone_name:
                        states.add("NC")
                    if "SC" in zone_name:
                        states.add("SC")
                elif region_code == "FLA":
                    states.add("FL")
                elif region_code == "TEN":
                    states.add("TN")
                elif region_code == "SE":
                    # Southeast regions could cross states
                    if "SOCO" in zone_name:
                        states.add("GA")
                        states.add("AL")
                    if "ATL" in zone_name:
                        states.add("GA")
                    if "CHA" in zone_name:
                        states.add("NC")
                    if "MIA" in zone_name:
                        states.add("FL")
                elif region_code == "CENT":
                    if "SPA" in zone_name:
                        states.add("AR")
                    if "SWPP" in zone_name:
                        states.add("KS")
                        states.add("OK")
                elif region_code == "MIDW":
                    if "LGEE" in zone_name:
                        states.add("KY")
    
    logger.info(f"Extracted states: {', '.join(sorted(states))}")
    return states

def filter_zones_by_state(zones_geojson, state_code):
    """
    Filter zones by state code.
    
    Returns a GeoJSON with only zones belonging to the specified state.
    """
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for feature in zones_geojson.get("features", []):
        properties = feature.get("properties", {})
        zone_name = properties.get("zoneName", "")
        
        # Check if this zone belongs to the specified state
        include = False
        
        if state_code == "NC":
            include = "-CAR-" in zone_name and ("NC" in zone_name or "DUK" in zone_name)
        elif state_code == "SC":
            include = "-CAR-" in zone_name and "SC" in zone_name
        elif state_code == "FL":
            include = "-FLA-" in zone_name or "MIA" in zone_name
        elif state_code == "TN":
            include = "-TEN-" in zone_name
        elif state_code == "GA":
            include = "SOCO" in zone_name or "ATL" in zone_name
        elif state_code == "AL":
            include = "SOCO" in zone_name
        elif state_code == "AR":
            include = "SPA" in zone_name
        elif state_code == "KS" or state_code == "OK":
            include = "SWPP" in zone_name
        elif state_code == "KY":
            include = "LGEE" in zone_name
        
        if include:
            filtered_geojson["features"].append(copy.deepcopy(feature))
    
    logger.info(f"Filtered {len(filtered_geojson['features'])} zones for state {state_code}")
    return filtered_geojson

def create_state_boundary_feature(state_code):
    """
    Create a simple feature representing a state boundary.
    
    This is a placeholder - in a real implementation, you would use actual state boundary data.
    """
    # These are approximate bounding boxes for each state
    state_bounds = {
        "NC": [[-84.3, 33.8], [-75.5, 36.6]],  # North Carolina
        "SC": [[-83.4, 32.0], [-78.5, 35.2]],  # South Carolina
        "FL": [[-87.6, 24.5], [-80.0, 31.0]],  # Florida
        "TN": [[-90.3, 34.9], [-81.6, 36.7]],  # Tennessee
        "GA": [[-85.6, 30.3], [-80.8, 35.0]],  # Georgia
        "AL": [[-88.5, 30.1], [-84.9, 35.0]],  # Alabama
        "AR": [[-94.6, 33.0], [-89.6, 36.5]],  # Arkansas
        "KS": [[-102.0, 37.0], [-94.6, 40.0]], # Kansas
        "OK": [[-103.0, 33.6], [-94.4, 37.0]], # Oklahoma
        "KY": [[-89.6, 36.5], [-82.0, 39.1]]   # Kentucky
    }
    
    if state_code not in state_bounds:
        logger.warning(f"No boundary data for state {state_code}")
        return None
    
    # Create a simple polygon from the bounding box
    sw, ne = state_bounds[state_code]
    coordinates = [
        [
            [sw[0], sw[1]],
            [sw[0], ne[1]],
            [ne[0], ne[1]],
            [ne[0], sw[1]],
            [sw[0], sw[1]]
        ]
    ]
    
    return {
        "type": "Feature",
        "properties": {
            "state": state_code,
            "name": state_code
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates
        }
    }

def create_state_geojson(zones_geojson, state_code):
    """
    Create a GeoJSON file for a specific state with its zones.
    
    Returns a GeoJSON with state boundary and zones for the specified state.
    """
    # Create a new GeoJSON
    state_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Add state boundary
    state_boundary = create_state_boundary_feature(state_code)
    if state_boundary:
        state_geojson["features"].append(state_boundary)
    
    # Filter zones by state
    state_zones = filter_zones_by_state(zones_geojson, state_code)
    
    # Add zones to the GeoJSON
    state_geojson["features"].extend(copy.deepcopy(state_zones["features"]))
    
    logger.info(f"Created GeoJSON for state {state_code} with {len(state_geojson['features'])} features")
    return state_geojson

def create_southeast_geojson(zones_geojson, states):
    """
    Create a GeoJSON file for the entire southeast region with state boundaries and zones.
    
    Returns a GeoJSON with state boundaries and all zones.
    """
    # Create a new GeoJSON
    southeast_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Add state boundaries
    for state_code in states:
        state_boundary = create_state_boundary_feature(state_code)
        if state_boundary:
            southeast_geojson["features"].append(state_boundary)
    
    # Add all zones
    southeast_geojson["features"].extend(copy.deepcopy(zones_geojson["features"]))
    
    logger.info(f"Created GeoJSON for southeast region with {len(southeast_geojson['features'])} features")
    return southeast_geojson

def main():
    """Main function to generate GeoJSON files."""
    logger.info("Starting GeoJSON generation")
    
    # Load southeast regions
    logger.info(f"Loading zones from {SOUTHEAST_REGIONS_PATH}")
    zones_geojson = load_geojson(SOUTHEAST_REGIONS_PATH)
    if not zones_geojson:
        logger.error("Failed to load southeast regions GeoJSON")
        return
    
    # Also copy the zone interfaces file to the output directory
    try:
        shutil.copy(ZONE_INTERFACES_PATH, os.path.join(OUTPUT_DIR, "zone_interfaces.geojson"))
        logger.info(f"Copied {ZONE_INTERFACES_PATH} to {OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"Error copying zone interfaces file: {str(e)}")
    
    # Extract states from zones
    states = extract_states_from_zones(zones_geojson)
    
    # Create GeoJSON for each state
    for state_code in states:
        state_geojson = create_state_geojson(zones_geojson, state_code)
        output_path = os.path.join(OUTPUT_DIR, f"{state_code.lower()}_zones.geojson")
        save_geojson(state_geojson, output_path)
    
    # Create GeoJSON for the entire southeast region
    southeast_geojson = create_southeast_geojson(zones_geojson, states)
    output_path = os.path.join(OUTPUT_DIR, "southeast_zones.geojson")
    save_geojson(southeast_geojson, output_path)
    
    logger.info("GeoJSON generation complete")

if __name__ == "__main__":
    main() 