"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResortEnergyData } from "@/types";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

interface InterRegionMapProps {
  data: ResortEnergyData[];
}

const geoUrl = "https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json";

export default function InterRegionMap({ data }: InterRegionMapProps) {
  if (!data || data.length === 0) return <div>No data available</div>;

  // Find max load for scaling
  const maxLoad = Math.max(...data.map(resort => {
    const lastLoadPoint = resort.load_data[resort.load_data.length - 1];
    return lastLoadPoint ? lastLoadPoint.value : 0;
  }));

  // Scale for marker size based on load
  const sizeScale = scaleLinear().domain([0, maxLoad]).range([4, 20]);

  // Extract coordinates from first weather point for demo
  const resortMarkers = data.map(resort => {
    // Extract latitude and longitude from resort data
    // Note: In a real app, you would have these as proper fields
    const lat = parseFloat(resort.resort_name.split(':')[1]?.trim() || "40");
    const long = parseFloat(resort.resort_name.split(':')[2]?.trim() || "-100");
    
    const lastLoadPoint = resort.load_data[resort.load_data.length - 1];
    const load = lastLoadPoint ? lastLoadPoint.value : 0;
    
    return {
      name: resort.resort_name.split(':')[0]?.trim() || resort.resort_name,
      resort_name: resort.resort_name,
      coordinates: [long, lat],
      size: sizeScale(load),
      load: load
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Inter-Region Energy Exchange</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80 w-full">
          <ComposableMap
            projectionConfig={{
              scale: 160,
              rotation: [-11, 0, 0],
            }}
          >
            <Geographies geography={geoUrl}>
              {({ geographies }) => 
                geographies.map(geo => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    className="fill-muted stroke-foreground/10"
                  />
                ))
              }
            </Geographies>
            
            {resortMarkers.map((marker, i) => (
              <Marker key={i} coordinates={marker.coordinates}>
                <circle 
                  r={marker.size} 
                  className="fill-primary fill-opacity-80 stroke-white"
                />
                <text
                  textAnchor="middle"
                  y={marker.size + 10}
                  className="text-[8px] fill-foreground font-medium"
                >
                  {marker.name}
                </text>
              </Marker>
            ))}
          </ComposableMap>
        </div>
      </CardContent>
    </Card>
  );
} 