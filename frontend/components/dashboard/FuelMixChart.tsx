"use client"

import { useState, useEffect, useMemo } from "react"
import { Download, TrendingUp, TrendingDown } from "lucide-react"
import { Label, Pie, PieChart, Cell } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { Button } from "@/components/ui/button"
import { Toggle } from "@/components/ui/toggle"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Progress } from "@/components/ui/progress"

// Define types for fuel mix data
interface FuelMixData {
  fuelType: string;
  generation: number;
  fill: string;
  name: string;
}

interface FuelMixChartProps {
  region: string;
  theme: 'dark' | 'light';
  isMobile: boolean;
}

// Define fuel type colors and labels
const FUEL_COLORS: Record<string, { color: string; name: string }> = {
  // Monochrome grayscale palette for dark theme (from shadcn's midnight theme)
  "COL": { color: "#27272a", name: "Coal" },             // Zinc-800
  "NG": { color: "#3f3f46", name: "Natural Gas" },       // Zinc-700  
  "NUC": { color: "#52525b", name: "Nuclear" },          // Zinc-600
  "WND": { color: "#71717a", name: "Wind" },             // Zinc-500
  "SUN": { color: "#a1a1aa", name: "Solar" },            // Zinc-400
  "WAT": { color: "#d4d4d8", name: "Hydro" },            // Zinc-300
  "OIL": { color: "#e4e4e7", name: "Oil" },              // Zinc-200
  "OTH": { color: "#f4f4f5", name: "Other Renewables" }, // Zinc-100
};

// Define renewable fuel types
const RENEWABLE_FUEL_TYPES = ["WND", "SUN", "WAT", "OTH"];

const FuelMixChart = ({ region, theme, isMobile }: FuelMixChartProps) => {
  // State for chart data and loading
  const [fuelMixData, setFuelMixData] = useState<FuelMixData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRenewablesOnly, setShowRenewablesOnly] = useState(false);
  const [trendsData, setTrendsData] = useState<{ percentage: number, isUp: boolean } | null>(null);
  const [isoRto, setIsoRto] = useState<string>("SERC"); // Default ISO/RTO
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [apiCallInProgress, setApiCallInProgress] = useState(false);

  // Calculate total megawatts generation
  const totalMW = useMemo(() => {
    return fuelMixData.reduce((total, fuel) => total + fuel.generation, 0);
  }, [fuelMixData]);

  // Determine the appropriate ISO/RTO based on the selected region
  useEffect(() => {
    // Reset data when region changes
    setFuelMixData([]);
    setIsLoading(true);
    setError(null);
    
    // This is a simplified mapping. In a real app, you'd have a more complete mapping
    const regionToIsoRtoMap: Record<string, string> = {
      "FL": "FRCC",
      "GA": "SERC",
      "NC": "SERC",
      "SC": "SERC",
      "TN": "SERC",
      "AL": "SERC",
      "MS": "SERC",
      "southeast": "SERC" // Default for entire southeast
    };

    setIsoRto(regionToIsoRtoMap[region] || "SERC");
  }, [region]);

  // Fetch fuel mix data from the API
  useEffect(() => {
    const fetchFuelMixData = async () => {
      setIsLoading(true);
      setApiCallInProgress(true);
      setLoadingProgress(0);
      setError(null);
      
      try {
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setLoadingProgress(prev => {
            const newProgress = prev + 10;
            // Cap at 90% until data is actually loaded
            return newProgress > 90 ? 90 : newProgress;
          });
        }, 300);
        
        // Set the endpoint based on whether we're showing all fuels or just renewables
        const endpoint = showRenewablesOnly 
          ? `/api/energy/renewable-fuel-mix?iso_rto=${isoRto}` 
          : `/api/energy/fuel-mix?iso_rto=${isoRto}`;
        
        // Add state parameter if a specific state is selected
        const stateParam = region !== "southeast" ? `&state=${region}` : "";
        
        // Use a daily interval to get today's data
        const url = `${endpoint}${stateParam}&interval=daily&agg_func=sum`;
        
        console.log(`Fetching data from: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Received fuel mix data:", data);
        
        // Process the data for the chart
        const fuelMixData: FuelMixData[] = [];
        
        // Process different data structure based on endpoint
        if (showRenewablesOnly) {
          const renewableData = data.renewable_fuel_mix_data;
          
          // Process each fuel type
          for (const [fuelType, timestamps] of Object.entries(renewableData)) {
            // Get the most recent data point (last key in timestamps object)
            const timestampKeys = Object.keys(timestamps as Record<string, number>);
            if (timestampKeys.length > 0) {
              const latestTimestamp = timestampKeys[timestampKeys.length - 1];
              const generation = (timestamps as Record<string, number>)[latestTimestamp];
              
              fuelMixData.push({
                fuelType,
                generation,
                fill: FUEL_COLORS[fuelType]?.color || "#999999",
                name: FUEL_COLORS[fuelType]?.name || fuelType
              });
            }
          }
        } else {
          // Process all fuel types
          const allFuelData = data.fuel_mix_data;
          
          // Process each fuel type
          for (const [fuelType, timestamps] of Object.entries(allFuelData)) {
            // Get the most recent data point
            const timestampKeys = Object.keys(timestamps as Record<string, number>);
            if (timestampKeys.length > 0) {
              const latestTimestamp = timestampKeys[timestampKeys.length - 1];
              const generation = (timestamps as Record<string, number>)[latestTimestamp];
              
              fuelMixData.push({
                fuelType,
                generation,
                fill: FUEL_COLORS[fuelType]?.color || "#999999",
                name: FUEL_COLORS[fuelType]?.name || fuelType
              });
            }
          }
        }
        
        // Sort by generation descending
        fuelMixData.sort((a, b) => b.generation - a.generation);
        
        // Set trends data based on API response
        setTrendsData({
          isUp: data.trends?.isUp ?? false,
          percentage: data.trends?.percentage ?? 0
        });
        
        setFuelMixData(fuelMixData);
        
        // Clear interval and set final progress
        clearInterval(progressInterval);
        setLoadingProgress(100);
      } catch (err) {
        console.error("Error fetching fuel mix data:", err);
        setError("Failed to load fuel mix data. Please try again later.");
        setLoadingProgress(100);
        
        // Provide sample data for development and when API is not available
        const sampleData: FuelMixData[] = [
          { fuelType: "NG", generation: 800, fill: FUEL_COLORS["NG"].color, name: FUEL_COLORS["NG"].name },
          { fuelType: "COL", generation: 500, fill: FUEL_COLORS["COL"].color, name: FUEL_COLORS["COL"].name },
          { fuelType: "NUC", generation: 1000, fill: FUEL_COLORS["NUC"].color, name: FUEL_COLORS["NUC"].name },
          { fuelType: "WND", generation: 200, fill: FUEL_COLORS["WND"].color, name: FUEL_COLORS["WND"].name },
          { fuelType: "SUN", generation: 150, fill: FUEL_COLORS["SUN"].color, name: FUEL_COLORS["SUN"].name },
          { fuelType: "WAT", generation: 300, fill: FUEL_COLORS["WAT"].color, name: FUEL_COLORS["WAT"].name },
          { fuelType: "OIL", generation: 50, fill: FUEL_COLORS["OIL"].color, name: FUEL_COLORS["OIL"].name },
          { fuelType: "OTH", generation: 120, fill: FUEL_COLORS["OTH"].color, name: FUEL_COLORS["OTH"].name },
        ];
        
        // Filter for renewables only if needed
        const filteredData = showRenewablesOnly 
          ? sampleData.filter(item => RENEWABLE_FUEL_TYPES.includes(item.fuelType))
          : sampleData;
          
        setFuelMixData(filteredData);
        
        // Set simulated trend data
        setTrendsData({
          percentage: 3.2,
          isUp: true
        });
      } finally {
        setTimeout(() => {
          setIsLoading(false);
          setApiCallInProgress(false);
          setLoadingProgress(0);
        }, 500); // Short delay to ensure progress bar completes smoothly
      }
    };

    fetchFuelMixData();
  }, [region, isoRto, showRenewablesOnly]);

  // Download CSV function
  const downloadCSV = async (isHistorical: boolean) => {
    try {
      // In a real app, you would fetch historical data from the API
      // For this example, we'll simulate a CSV download
      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Fuel Type,Generation (MW),Timestamp\n";
      
      if (isHistorical) {
        // Simulate historical data
        const now = new Date();
        for (let i = 30; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split('T')[0];
          
          fuelMixData.forEach(fuel => {
            // Randomly vary the generation for historical data
            const randomFactor = 0.8 + Math.random() * 0.4; // 80% to 120% of current value
            csvContent += `${fuel.name},${Math.round(fuel.generation * randomFactor)},${dateStr}\n`;
          });
        }
      } else {
        // Current data
        const dateStr = new Date().toISOString().split('T')[0];
        fuelMixData.forEach(fuel => {
          csvContent += `${fuel.name},${fuel.generation},${dateStr}\n`;
        });
      }
      
      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `fuel-mix-${isHistorical ? 'historical' : 'current'}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Error downloading CSV:", err);
      alert("Failed to download CSV. Please try again later.");
    }
  };

  // Chart configuration
  const chartConfig: ChartConfig = useMemo(() => {
    const config: ChartConfig = {
      generation: {
        label: "Generation",
      },
    };
    
    // Add each fuel type to the config
    fuelMixData.forEach(fuel => {
      config[fuel.fuelType] = {
        label: fuel.name,
        color: fuel.fill,
      };
    });
    
    return config;
  }, [fuelMixData]);

  return (
    <Card className="flex flex-col">
      <CardHeader className={`${isMobile ? 'pt-2 pb-1' : 'pt-3 pb-2'}`}>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className={`text-lg font-medium ${
              theme === 'dark' ? 'text-stone-100' : 'text-stone-900'
            }`}>
              Fuel Mix Chart
            </CardTitle>
            <CardDescription className={theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}>
              {region === 'southeast' 
                ? 'Entire Southeast Region' 
                : `State: ${region}`
              } - {new Date().toLocaleDateString()}
            </CardDescription>
          </div>
          <div className="flex gap-1">
            <Button 
              size="sm" 
              variant={theme === 'dark' ? 'outline' : 'secondary'}
              className={`h-7 px-2 ${
                theme === 'dark' 
                  ? 'border-stone-700 text-stone-300 hover:bg-stone-800' 
                  : 'text-stone-700 hover:bg-stone-200'
              }`}
              onClick={() => downloadCSV(false)}
              disabled={isLoading}
            >
              <Download className="h-3.5 w-3.5 mr-1" />
              <span className="text-xs">Current</span>
            </Button>
            <Button 
              size="sm" 
              variant={theme === 'dark' ? 'outline' : 'secondary'}
              className={`h-7 px-2 ${
                theme === 'dark' 
                  ? 'border-stone-700 text-stone-300 hover:bg-stone-800' 
                  : 'text-stone-700 hover:bg-stone-200'
              }`}
              onClick={() => downloadCSV(true)}
              disabled={isLoading}
            >
              <Download className="h-3.5 w-3.5 mr-1" />
              <span className="text-xs">Historical</span>
            </Button>
          </div>
        </div>
        <div className="flex justify-between items-center mt-2">
          <ToggleGroup type="single" value={showRenewablesOnly ? "renewables" : "all"}>
            <ToggleGroupItem 
              value="all" 
              aria-label="Show all fuels"
              onClick={() => setShowRenewablesOnly(false)}
              className={`h-7 px-2 text-xs ${
                theme === 'dark'
                  ? 'text-stone-300 hover:bg-stone-800'
                  : 'text-stone-700 hover:bg-stone-200'
              }`}
              disabled={isLoading}
            >
              All Fuels
            </ToggleGroupItem>
            <ToggleGroupItem 
              value="renewables" 
              aria-label="Show renewables only"
              onClick={() => setShowRenewablesOnly(true)}
              className={`h-7 px-2 text-xs ${
                theme === 'dark'
                  ? 'text-stone-300 hover:bg-stone-800'
                  : 'text-stone-700 hover:bg-stone-200'
              }`}
              disabled={isLoading}
            >
              Renewables Only
            </ToggleGroupItem>
          </ToggleGroup>
          
          <Card className={`border ${
            theme === 'dark'
              ? 'bg-stone-900/50 border-stone-800' 
              : 'bg-stone-100/50 border-stone-200'
          } p-2 rounded-md`}>
            <div className="text-xs font-medium">
              Total Generation
            </div>
            <div className={`text-lg font-bold ${
              theme === 'dark' ? 'text-stone-100' : 'text-stone-900'
            }`}>
              {isLoading ? '...' : `${Math.round(totalMW).toLocaleString()} MW`}
            </div>
          </Card>
        </div>
      </CardHeader>
      
      <CardContent className={`flex-1 px-1 ${isMobile ? 'pb-1' : 'pb-2'} ${isLoading ? 'flex items-center justify-center flex-col' : ''}`}>
        {isLoading ? (
          <>
            <div className={`text-sm mb-4 ${theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}`}>
              Loading fuel mix data...
            </div>
            <div className="w-[80%] max-w-[300px]">
              <Progress value={loadingProgress} className={theme === 'dark' ? 'bg-stone-800' : 'bg-stone-200'} />
            </div>
          </>
        ) : error ? (
          <div className={`text-sm ${theme === 'dark' ? 'text-red-400' : 'text-red-500'}`}>
            {error}
          </div>
        ) : (
          <ChartContainer
            config={chartConfig}
            className={`mx-auto aspect-square ${isMobile ? 'max-h-[220px]' : 'max-h-[320px]'}`}
          >
            <PieChart>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <Pie
                data={fuelMixData}
                dataKey="generation"
                nameKey="fuelType"
                innerRadius={isMobile ? 50 : 70}
                outerRadius={isMobile ? 80 : 110}
                strokeWidth={2}
                stroke={theme === 'dark' ? '#121212' : '#ffffff'}
              >
                {fuelMixData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
                <Label
                  content={({ viewBox }) => {
                    if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                      return (
                        <text
                          x={viewBox.cx}
                          y={viewBox.cy}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className={theme === 'dark' ? 'fill-stone-100' : 'fill-stone-900'}
                        >
                          <tspan
                            x={viewBox.cx}
                            y={viewBox.cy}
                            className={`text-2xl font-bold ${isMobile ? 'text-lg' : 'text-2xl'}`}
                          >
                            {Math.round(totalMW).toLocaleString()}
                          </tspan>
                          <tspan
                            x={viewBox.cx}
                            y={(viewBox.cy || 0) + (isMobile ? 18 : 24)}
                            className={`${isMobile ? 'text-xs' : 'text-sm'} ${theme === 'dark' ? 'fill-stone-400' : 'fill-stone-500'}`}
                          >
                            MW
                          </tspan>
                        </text>
                      )
                    }
                    return null;
                  }}
                />
              </Pie>
            </PieChart>
          </ChartContainer>
        )}
      </CardContent>
      
      <CardFooter className={`flex-col gap-2 text-sm pt-0 ${isMobile ? 'pb-2' : 'pb-3'}`}>
        {apiCallInProgress && (
          <div className="w-full mt-1 mb-2">
            <Progress value={loadingProgress} className={`h-1 ${theme === 'dark' ? 'bg-stone-800' : 'bg-stone-200'}`} />
          </div>
        )}
        
        {trendsData && !isLoading && (
          <div className={`flex items-center gap-2 text-xs font-medium leading-none ${
            trendsData.isUp 
              ? theme === 'dark' ? 'text-green-400' : 'text-green-600'
              : theme === 'dark' ? 'text-red-400' : 'text-red-600'
          }`}>
            {trendsData.isUp ? 'Up' : 'Down'} by {trendsData.percentage.toFixed(1)}% this month
            {trendsData.isUp 
              ? <TrendingUp className="h-3.5 w-3.5" />
              : <TrendingDown className="h-3.5 w-3.5" />
            }
          </div>
        )}
        <div className={`leading-none text-xs ${theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}`}>
          {isLoading 
            ? 'Loading fuel mix data...'
            : showRenewablesOnly 
              ? 'Showing renewable energy sources only'
              : 'Showing all energy sources by fuel type'
          }
        </div>
      </CardFooter>
    </Card>
  )
}

export default FuelMixChart; 