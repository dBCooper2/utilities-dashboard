"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from "recharts";
import { ResortEnergyData } from "@/types";

interface LbmpChartProps {
  data: ResortEnergyData;
}

export default function LbmpChart({ data }: LbmpChartProps) {
  if (!data) return <div>No data available</div>;

  // Prepare chart data
  const chartData = data.load_data.map((loadPoint, index) => {
    return {
      load: loadPoint.value,
      price: data.lbmp_data[index]?.value || 0,
      time: new Date(loadPoint.timestamp).toLocaleTimeString(),
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Load vs. LBPM (Price)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
              margin={{
                top: 20,
                right: 20,
                bottom: 20,
                left: 20,
              }}
            >
              <CartesianGrid />
              <XAxis 
                type="number" 
                dataKey="load" 
                name="Load" 
                unit=" MW" 
                label={{ value: 'Load (MW)', position: 'insideBottomRight', offset: -5 }} 
              />
              <YAxis 
                type="number" 
                dataKey="price" 
                name="Price" 
                unit=" $/MWh" 
                label={{ value: 'Price ($/MWh)', angle: -90, position: 'insideLeft' }} 
              />
              <ZAxis type="category" dataKey="time" name="Time" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter name="Load vs Price" data={chartData} fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
} 