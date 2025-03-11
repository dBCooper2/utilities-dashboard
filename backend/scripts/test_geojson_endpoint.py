#!/usr/bin/env python
"""
Script to test the GeoJSON endpoint.
"""

import os
import sys
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_geojson_endpoint():
    """Test the GeoJSON endpoint"""
    url = "http://localhost:8000/api/energy/zone-interfaces-geojson"
    
    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Error accessing endpoint: {response.status_code}")
            return
        
        # Parse response
        data = response.json()
        
        # Check if it's a valid GeoJSON
        if data.get("type") != "FeatureCollection":
            logger.error("Invalid GeoJSON: not a FeatureCollection")
            return
        
        features = data.get("features", [])
        logger.info(f"Found {len(features)} features")
        
        # Print the first feature
        if features:
            logger.info(f"First feature: {json.dumps(features[0], indent=2)}")
        
        return data
    except Exception as e:
        logger.error(f"Error testing endpoint: {str(e)}")
        return None

if __name__ == "__main__":
    test_geojson_endpoint() 