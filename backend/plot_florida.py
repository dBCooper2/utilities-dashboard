import os
import json
import folium
import requests
from folium.features import GeoJsonTooltip

# Set up the map centered on Florida
florida_map = folium.Map(
    location=[27.6648, -81.5158],  # Center of Florida
    zoom_start=7,
    control_scale=True
)

# Colors for the different zones
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Request the Florida GeoJSON from our API
try:
    # You may need to update the URL if your Docker setup uses a different port
    # If running on the host, use http://localhost:8000
    # If running from inside the container, use http://backend:8000
    response = requests.get("http://localhost:8000/api/energy/state-geojson/FL")
    florida_geojson = response.json()
    
    # Add the GeoJSON data to the map
    folium.GeoJson(
        florida_geojson,
        name="Florida Zones",
        style_function=lambda feature, color=colors: {
            'fillColor': colors[feature['properties']['zone_id'] % len(colors)],
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        },
        tooltip=GeoJsonTooltip(
            fields=['zone_name', 'zone_code', 'iso_rto'],
            aliases=['Zone Name:', 'Zone Code:', 'ISO/RTO:'],
            localize=True
        )
    ).add_to(florida_map)
    
    # Add layer control
    folium.LayerControl().add_to(florida_map)
    
    # Save the map to an HTML file
    output_path = "florida_zones_map.html"
    florida_map.save(output_path)
    print(f"Map saved to {os.path.abspath(output_path)}")
    
except Exception as e:
    print(f"Error creating map: {str(e)}") 