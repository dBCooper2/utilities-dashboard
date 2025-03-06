"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from "recharts";
import { ResortEnergyData } from "@/types";

interface LoadLossesChartProps {
  data: ResortEnergyData;
}

export default function LoadLossesChart({ data }: LoadLossesChartProps) {
  if (!data) return <div>No data available</div>;

  // Prepare chart data
  const chartData = data.load_data.map((loadPoint, index) => {
    return {
      time: new Date(loadPoint.timestamp).toLocaleTimeString(),
      load: loadPoint.value,
      losses: data.losses[index]?.value || 0,
      totalWithLosses: loadPoint.value + (data.losses[index]?.value || 0),
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Load with Losses</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" orientation="left" label={{ value: 'MW', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="load" 
                stackId="1" 
                fill="#8884d8" 
                stroke="#8884d8"
                yAxisId="left"
              />
              <Area 
                type="monotone" 
                dataKey="losses" 
                stackId="1" 
                fill="#82ca9d" 
                stroke="#82ca9d"
                yAxisId="left"
              />
              <Line
                type="monotone"
                dataKey="totalWithLosses"
                stroke="#ff7300"
                yAxisId="left"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
} 