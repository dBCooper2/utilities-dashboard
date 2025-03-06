"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { ResortEnergyData } from "@/types";

interface EnergyMixChartProps {
  data: ResortEnergyData;
}

// Color palette for different energy sources
const COLORS = {
  Coal: "#8884d8",
  "Natural Gas": "#82ca9d",
  Nuclear: "#ffc658",
  Hydro: "#0088FE",
  Wind: "#00C49F",
  Solar: "#FFBB28",
  Biomass: "#FF8042",
  Geothermal: "#A569BD",
  Oil: "#E74C3C"
};

export default function EnergyMixChart({ data }: EnergyMixChartProps) {
  if (!data || !data.energy_mix) return <div>No energy mix data available</div>;

  // Prepare data for pie chart
  const chartData = data.energy_mix.map(item => ({
    name: item.source,
    value: item.percentage
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Energy Source Mix</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[entry.name as keyof typeof COLORS] || `hsl(${index * 45}, 70%, 60%)`} 
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
} 