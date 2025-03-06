"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, Sankey, Tooltip, Rectangle } from "recharts";
import { InterfaceFlow } from "@/types";

interface InterfaceFlowsDiagramProps {
  data: InterfaceFlow[];
}

export default function InterfaceFlowsDiagram({ data }: InterfaceFlowsDiagramProps) {
  if (!data || data.length === 0) return <div>No interface flow data available</div>;

  // Process data for Sankey diagram
  const regions = new Set<string>();
  data.forEach(flow => {
    regions.add(flow.from_region);
    regions.add(flow.to_region);
  });

  const nodesArray = Array.from(regions).map((name, index) => ({
    name,
    value: name
  }));

  // Map region names to node indices
  const regionToIndex = {} as Record<string, number>;
  nodesArray.forEach((node, index) => {
    regionToIndex[node.name] = index;
  });

  // Create links for Sankey diagram
  const linksArray = data.map(flow => ({
    source: regionToIndex[flow.from_region],
    target: regionToIndex[flow.to_region],
    value: flow.power_flow,
    uv: flow.power_flow // For tooltip display
  }));

  const sankeyData = {
    nodes: nodesArray,
    links: linksArray
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Interface Flows (Region Transfers)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <Sankey
              data={sankeyData}
              nodePadding={50}
              nodeWidth={10}
              linkCurvature={0.5}
              link={{ stroke: "#999" }}
              node={
                <Rectangle 
                  fill="hsl(var(--primary))"
                  fillOpacity={0.9}
                />
              }
            >
              <Tooltip 
                formatter={(value, name) => [`${value} MW`, `Region: ${name}`]}
              />
            </Sankey>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
} 