import requests
import json
import os

# Request the Florida GeoJSON from our API
try:
    # Fetch the Florida GeoJSON data
    print("Fetching Florida GeoJSON data...")
    response = requests.get("http://localhost:8000/api/energy/state-geojson/FL")
    florida_geojson = response.json()
    
    # Print summary of the GeoJSON data
    features_count = len(florida_geojson.get("features", []))
    print(f"Received GeoJSON data with {features_count} features (zones)")
    
    # Print detailed info about each zone
    print("\nZones in Florida:")
    for i, feature in enumerate(florida_geojson.get("features", [])):
        properties = feature.get("properties", {})
        print(f"  {i+1}. {properties.get('zone_code')} - {properties.get('zone_name')} (ISO/RTO: {properties.get('iso_rto')})")
    
    # Save the GeoJSON to a file
    output_path = "/app/florida_zones.geojson"
    with open(output_path, "w") as f:
        json.dump(florida_geojson, f, indent=2)
    
    print(f"\nGeoJSON data saved to {output_path}")
    
except Exception as e:
    print(f"Error: {str(e)}") 