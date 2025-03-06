"use client";

import { useState, useEffect } from "react";
import { Container } from "@/components/ui/container";
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import LoadLossesChart from "@/components/charts/LoadLossesChart";
import LbmpChart from "@/components/charts/LbmpChart";
import InterfaceFlowsDiagram from "@/components/charts/InterfaceFlowsDiagram";
import InterRegionMap from "@/components/charts/InterRegionMap";
import EnergyMixChart from "@/components/charts/EnergyMixChart";
import { getDashboardData } from "@/services/api";
import { DashboardData } from "@/types";

export default function HomePage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{message: string, details?: string} | null>(null);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const dashboardData = await getDashboardData();
        setData(dashboardData);
        
        // Set first resort as default selection
        if (dashboardData.resort_data.length > 0) {
          setSelectedResort(dashboardData.resort_data[0].resort_id);
        }
      } catch (err) {
        console.error("Dashboard data fetch error:", err);
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setError({
          message: "Failed to load dashboard data",
          details: errorMessage
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <Container>
      <Card>
        <CardContent className="flex items-center justify-center min-h-[400px]">
          <div>Loading dashboard data...</div>
        </CardContent>
      </Card>
    </Container>
  );
  
  if (error) return (
    <Container>
      <Card>
        <CardHeader>
          <CardTitle className="text-destructive">Error Loading Dashboard</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-lg font-medium">{error.message}</div>
          {error.details && (
            <div className="p-4 bg-muted rounded-md overflow-auto">
              <pre className="text-sm">{error.details}</pre>
            </div>
          )}
          <button 
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </CardContent>
      </Card>
    </Container>
  );
  
  if (!data) return (
    <Container>
      <Card>
        <CardContent className="flex items-center justify-center min-h-[400px]">
          <div>No data available</div>
        </CardContent>
      </Card>
    </Container>
  );

  const selectedResortData = data.resort_data.find(
    r => r.resort_id === selectedResort
  );

  return (
    <Container>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Energy Market Dashboard for Ski Resort Regions
          </h1>
          <p className="text-muted-foreground mt-2">
            View real-time energy market data for regions with ski resorts
          </p>
        </div>
        
        <div className="mb-6">
          <label htmlFor="resort-select" className="block text-sm font-medium mb-2">
            Select Ski Resort:
          </label>
          <Select 
            value={selectedResort || ""} 
            onValueChange={setSelectedResort}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a resort" />
            </SelectTrigger>
            <SelectContent>
              {data.resort_data.map((resort) => (
                <SelectItem key={resort.resort_id} value={resort.resort_id}>
                  {resort.resort_name} ({resort.region})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Top row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <LoadLossesChart data={selectedResortData!} />
          <LbmpChart data={selectedResortData!} />
        </div>
        
        {/* Middle row */}
        <div className="mb-6">
          <EnergyMixChart data={selectedResortData!} />
        </div>
        
        {/* Bottom row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InterfaceFlowsDiagram data={data.interface_flows} />
          <InterRegionMap data={data.resort_data} />
        </div>
      </div>
    </Container>
  );
}
