import requests
import json
import folium
import random
import webbrowser
import os

# Make a request to get the Florida GeoJSON data
response = requests.get('http://localhost:8000/api/energy/state-geojson/FL')
if response.status_code != 200:
    print(f"Error fetching data: {response.status_code}")
    exit(1)

florida_geojson = response.json()

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

# Open the map in the default web browser
webbrowser.open('file://' + os.path.realpath(html_file)) 