import requests
import json
import matplotlib.pyplot as plt
import geopandas as gpd
from io import StringIO

# Request the Florida GeoJSON from our API
try:
    # Fetch the Florida GeoJSON data
    response = requests.get("http://localhost:8000/api/energy/state-geojson/FL")
    florida_geojson = response.json()
    
    # Convert the GeoJSON to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(florida_geojson["features"])
    
    # Set up the plot
    fig, ax = plt.figure(figsize=(10, 10)), plt.gca()
    
    # Plot the zones with different colors
    gdf.plot(
        ax=ax,
        column="zone_code",  # Color by zone code
        legend=True,
        cmap="tab10",
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7
    )
    
    # Customize the plot
    ax.set_title("Florida Energy Zones", fontsize=15)
    ax.set_axis_off()  # Turn off the axis
    
    # Add labels for each zone
    for idx, row in gdf.iterrows():
        # Get the centroid of the geometry
        centroid = row.geometry.centroid
        # Add a text label at the centroid
        ax.annotate(
            text=row["zone_code"],
            xy=(centroid.x, centroid.y),
            ha="center",
            fontsize=8,
            color="black",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.7)
        )
    
    # Save the plot
    output_path = "florida_zones_map.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Map saved to {output_path}")
    
except Exception as e:
    print(f"Error creating map: {str(e)}") 