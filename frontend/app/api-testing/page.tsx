"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { energyService } from '@/lib/services/energyService';
import { weatherService } from '@/lib/services/weatherService';
import Link from 'next/link';

// Reusable API Test Card component
interface ApiTestCardProps {
  title: string;
  description: string;
  endpoints: {
    name: string;
    action: () => Promise<any>;
    params?: string;
  }[];
}

const ApiTestCard: React.FC<ApiTestCardProps> = ({ title, description, endpoints }) => {
  const [results, setResults] = useState<{ [key: string]: any }>({});
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState<{ [key: string]: string }>({});

  const handleApiCall = async (name: string, action: () => Promise<any>) => {
    setLoading(prev => ({ ...prev, [name]: true }));
    setError(prev => ({ ...prev, [name]: '' }));

    try {
      const data = await action();
      setResults(prev => ({ ...prev, [name]: data }));
      console.log(`${name} response:`, data);
    } catch (err) {
      console.error(`Error calling ${name}:`, err);
      setError(prev => ({ ...prev, [name]: err instanceof Error ? err.message : 'Unknown error' }));
    } finally {
      setLoading(prev => ({ ...prev, [name]: false }));
    }
  };

  return (
    <Card className="w-full bg-stone-950/70 border-stone-800 text-white">
      <CardHeader>
        <CardTitle className="text-lg text-stone-100">{title}</CardTitle>
        <CardDescription className="text-stone-400">{description}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        {endpoints.map(endpoint => (
          <div key={endpoint.name} className="border border-stone-800 rounded-md p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium text-stone-200">{endpoint.name}</h3>
              <Button 
                variant="outline" 
                size="sm"
                className="border-stone-700 text-stone-300 hover:bg-stone-800 hover:text-stone-100"
                onClick={() => handleApiCall(endpoint.name, endpoint.action)}
                disabled={loading[endpoint.name]}
              >
                {loading[endpoint.name] ? 'Loading...' : 'Test API'}
              </Button>
            </div>
            
            {endpoint.params && (
              <div className="mb-2 text-xs text-stone-400 bg-stone-900 p-2 rounded-md">
                <code className="block whitespace-pre-wrap">{endpoint.params}</code>
              </div>
            )}
            
            {error[endpoint.name] && (
              <div className="mt-2 text-red-400 text-sm">
                Error: {error[endpoint.name]}
              </div>
            )}
            
            {results[endpoint.name] && (
              <div className="mt-2">
                <details className="group">
                  <summary className="cursor-pointer text-stone-300 text-sm flex items-center">
                    <span className="mr-2">View Response</span>
                    <span className="group-open:rotate-90 transition-transform">→</span>
                  </summary>
                  <pre className="mt-2 p-2 bg-stone-900/70 rounded-md overflow-auto max-h-80 text-xs text-stone-300">
                    {JSON.stringify(results[endpoint.name], null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

// Main API Testing Page
export default function ApiTestingPage() {
  // State to store available regions
  const [validZones, setValidZones] = useState<string[]>([]);
  const [validRegions, setValidRegions] = useState<string[]>([]);
  const [backendStatus, setBackendStatus] = useState<'loading' | 'connected' | 'error'>('loading');
  
  // Fetch valid zones and regions on component mount
  useEffect(() => {
    const fetchValidData = async () => {
      try {
        // Check if backend is running
        await fetch('http://localhost:8000/api/weather/regions')
          .then(res => {
            if (res.ok) setBackendStatus('connected');
            else setBackendStatus('error');
            return res.json();
          })
          .then(data => {
            if (data) setValidRegions(data.map((region: any) => region.code));
          })
          .catch(() => {
            setBackendStatus('error');
          });

        // Fetch zones
        const zones = await energyService.getZones();
        if (zones && zones.length > 0) {
          setValidZones(zones.map(zone => zone.code));
        }
      } catch (error) {
        console.error("Error fetching valid zones and regions:", error);
        setBackendStatus('error');
      }
    };
    
    fetchValidData();
  }, []);

  // Get current date and time strings for API parameters
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const dateString = now.toISOString().split('T')[0];
  const yesterdayString = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const startTimeString = oneWeekAgo.toISOString();
  const endTimeString = now.toISOString();

  // Get first valid zone and region codes (or fallback to defaults)
  const defaultZoneCode = validZones.length > 0 ? validZones[0] : 'FRCC';
  const defaultRegionCode = validRegions.length > 0 ? validRegions[0] : 'US-SE-ATL';

  return (
    <div className="min-h-dvh bg-black text-white">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-stone-900/10 rounded-full blur-3xl"></div>
        <div className="absolute top-40 -right-40 w-80 h-80 bg-stone-800/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-40 left-1/3 w-80 h-80 bg-stone-900/10 rounded-full blur-3xl"></div>
      </div>
      
      <div className="relative">
        {/* Header */}
        <header className="pt-8 px-8 pb-6 border-b border-stone-800">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-stone-100">API Testing Dashboard</h1>
                <p className="text-stone-400 mt-1">Test and visualize backend API endpoints</p>
              </div>
              <div className="flex items-center gap-4">
                <div className={`text-sm px-3 py-1 rounded ${
                  backendStatus === 'connected' 
                    ? 'bg-green-900/30 text-green-400' 
                    : backendStatus === 'error' 
                      ? 'bg-red-900/30 text-red-400' 
                      : 'bg-yellow-900/30 text-yellow-400'
                }`}>
                  {backendStatus === 'connected' 
                    ? 'Backend Connected' 
                    : backendStatus === 'error' 
                      ? 'Backend Error' 
                      : 'Connecting...'}
                </div>
                <Link href="/" className="text-stone-400 hover:text-stone-200 transition-colors">
                  Back to Dashboard
                </Link>
              </div>
            </div>
            
            {/* Available zones and regions */}
            <div className="mt-4 text-xs text-stone-400 space-y-1">
              <p>Backend Status: {backendStatus}</p>
              <p>Available Zones: {validZones.length > 0 ? validZones.join(', ') : 'None found'}</p>
              <p>Available Regions: {validRegions.length > 0 ? validRegions.join(', ') : 'None found'}</p>
              <p>Default Zone: {defaultZoneCode}</p>
              <p>Default Region: {defaultRegionCode}</p>
            </div>

            {backendStatus === 'error' && (
              <div className="mt-4 p-4 border border-red-800 bg-red-900/20 rounded-md text-red-300">
                <h3 className="font-medium mb-2">Backend Connection Issue</h3>
                <p className="text-sm">Make sure the backend server is running on http://localhost:8000</p>
                <p className="text-sm mt-2">Start the backend with: <code className="bg-black/40 px-2 py-1 rounded">cd backend && python main.py</code></p>
              </div>
            )}
          </div>
        </header>

        {/* Main content */}
        <main className="py-8 px-4 sm:px-8">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Regions API Card */}
            <ApiTestCard
              title="Weather Regions"
              description="Get regions available in the API"
              endpoints={[
                {
                  name: "Get Regions",
                  action: () => weatherService.getRegions()
                }
              ]}
            />

            {/* Daily Weather API Card */}
            <ApiTestCard
              title="Daily Weather"
              description="Get daily weather data for a region"
              endpoints={[
                {
                  name: "Get Daily Weather",
                  action: () => weatherService.getDailyWeather(defaultRegionCode, {
                    start_date: yesterdayString,
                    end_date: dateString
                  }),
                  params: `Region Code: ${defaultRegionCode}\nStart Date: ${yesterdayString}\nEnd Date: ${dateString}`
                }
              ]}
            />

            {/* Energy Zones API Card */}
            <ApiTestCard
              title="Energy Zones"
              description="Test zone-related API endpoints"
              endpoints={[
                {
                  name: "Get All Zones",
                  action: () => energyService.getZones()
                },
                {
                  name: "Get Zone Details",
                  action: () => energyService.getZoneDetails(defaultZoneCode),
                  params: `Zone Code: ${defaultZoneCode}`
                }
              ]}
            />

            {/* State GeoJSON API Card */}
            <ApiTestCard
              title="GeoJSON Data"
              description="Geographical data for visualization"
              endpoints={[
                {
                  name: "Get State GeoJSON",
                  action: () => energyService.getStateGeoJSON("FL"),
                  params: "State Code: FL"
                }
              ]}
            />
          </div>
        </main>
      </div>
    </div>
  );
} 