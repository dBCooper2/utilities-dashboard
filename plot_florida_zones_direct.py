import json
import folium
import os
import webbrowser
import psycopg2
from psycopg2.extras import Json, DictCursor

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="energy_dashboard",
    user="postgres",
    password="postgres"
)

# Use DictCursor to return results as dictionaries
cursor = conn.cursor(cursor_factory=DictCursor)

# Get all zones in Florida
cursor.execute("SELECT id, code, name, state, iso_rto, geojson FROM zones WHERE state = 'FL'")
zones = cursor.fetchall()

# Create GeoJSON features
features = []
for zone in zones:
    # Skip if no GeoJSON data
    if not zone['geojson']:
        continue
        
    # Create a GeoJSON feature for this zone
    feature = {
        "type": "Feature",
        "properties": {
            "zone_id": zone['id'],
            "zone_code": zone['code'],
            "zone_name": zone['name'],
            "iso_rto": zone['iso_rto']
        },
        "geometry": zone['geojson']
    }
    features.append(feature)

# Create a GeoJSON FeatureCollection
florida_geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Create a map centered on Florida
map_center = [28.0, -83.0]  # Approximate center of Florida
florida_map = folium.Map(location=map_center, zoom_start=7)

# Generate a list of distinct colors for the zones
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
          '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']

# Add GeoJSON data to the map
for i, feature in enumerate(florida_geojson['features']):
    color = colors[i % len(colors)]
    folium.GeoJson(
        feature,
        name=feature['properties']['zone_code'],
        style_function=lambda x, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        },
        tooltip=folium.Tooltip(feature['properties']['zone_code'])
    ).add_to(florida_map)

# Add a layer control panel to the map
folium.LayerControl().add_to(florida_map)

# Save the map as an HTML file
html_file = 'florida_zones_map.html'
florida_map.save(html_file)
print(f"Map saved as {html_file}")

# Also save the GeoJSON for debugging
with open('florida_zones.json', 'w') as f:
    json.dump(florida_geojson, f, indent=2)
print(f"GeoJSON saved as florida_zones.json")

# Close the database connection
cursor.close()
conn.close()

# Open the map in the default web browser
webbrowser.open('file://' + os.path.realpath(html_file)) 