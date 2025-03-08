'use client';

import React, { useState, ReactNode, useEffect } from 'react';
import WeatherDataChart from '../components/charts/WeatherDataChart';
import { useWeatherData } from '../hooks/useWeatherData';
import { CloudRainIcon, SunIcon, CloudIcon, WindIcon, DropletIcon } from 'lucide-react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'outline';
  className?: string;
}

interface SelectProps {
  children: ReactNode;
  value: string;
  onValueChange: (value: string) => void;
}

interface SelectTriggerProps {
  children: ReactNode;
  className?: string;
}

interface SelectValueProps {
  placeholder: string;
}

interface SelectContentProps {
  children: ReactNode;
}

interface SelectItemProps {
  value: string;
  children: ReactNode;
}

const Card: React.FC<CardProps> = ({ children, className = "" }) => (
  <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}>
    {children}
  </div>
);

const CardHeader: React.FC<CardHeaderProps> = ({ children, className = "" }) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>
    {children}
  </div>
);

const CardTitle: React.FC<CardTitleProps> = ({ children, className = "" }) => (
  <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>
    {children}
  </h3>
);

const CardDescription: React.FC<CardDescriptionProps> = ({ children, className = "" }) => (
  <p className={`text-sm text-muted-foreground ${className}`}>
    {children}
  </p>
);

const CardContent: React.FC<CardContentProps> = ({ children, className = "" }) => (
  <div className={`p-6 pt-0 ${className}`}>
    {children}
  </div>
);

const Badge: React.FC<BadgeProps> = ({ children, variant = "default", className = "" }) => {
  const variantClasses = variant === "outline" ? "border border-input bg-background" : "bg-primary text-primary-foreground";
  return (
    <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${variantClasses} ${className}`}>
      {children}
    </div>
  );
};

const Select: React.FC<SelectProps> = ({ children, value, onValueChange }) => {
  return (
    <div className="relative">
      <select 
        value={value} 
        onChange={(e) => onValueChange(e.target.value)}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm"
      >
        {children}
      </select>
    </div>
  );
};

const SelectTrigger: React.FC<SelectTriggerProps> = ({ children, className = "" }) => (
  <div className={className}>{children}</div>
);

const SelectValue: React.FC<SelectValueProps> = ({ placeholder }) => (
  <span>{placeholder}</span>
);

const SelectContent: React.FC<SelectContentProps> = ({ children }) => (
  <>{children}</>
);

const SelectItem: React.FC<SelectItemProps> = ({ value, children }) => (
  <option value={value}>{children}</option>
);

// Helper function to determine which weather icon to show
const getWeatherIcon = (temp: number, cloudCover: number = 0, precipitation: number = 0, windSpeed: number = 0) => {
  if (precipitation > 0.1) {
    return <CloudRainIcon className="h-8 w-8 text-blue-400" />;
  } else if (cloudCover > 70) {
    return <CloudIcon className="h-8 w-8 text-gray-400" />;
  } else if (cloudCover > 30) {
    return <CloudIcon className="h-8 w-8 text-gray-300" />;
  } else if (windSpeed > 15) {
    return <WindIcon className="h-8 w-8 text-gray-300" />;
  } else {
    return <SunIcon className="h-8 w-8 text-yellow-400" />;
  }
};

// Helper function to get a description of the weather
const getWeatherDescription = (temp: number, cloudCover: number = 0, precipitation: number = 0, windSpeed: number = 0) => {
  if (precipitation > 0.2) {
    return 'Heavy Rain';
  } else if (precipitation > 0.05) {
    return 'Light Rain';
  } else if (cloudCover > 70) {
    return 'Overcast';
  } else if (cloudCover > 30) {
    return 'Partly Cloudy';
  } else if (windSpeed > 15) {
    return 'Windy';
  } else {
    return 'Clear';
  }
};

const WeatherForecast: React.FC = () => {
  const [selectedZone, setSelectedZone] = useState<string>('US-FLA-FPL');
  const { currentWeather, forecastData, isLoading, error, useMockData } = useWeatherData(selectedZone);

  // For demo purposes, generate some fake load data that correlates with temperature
  const loadData = forecastData.map(weather => 
    15000 + (Math.max(0, weather.temperature - 60) * 200) + (Math.random() * 1000)
  );
  
  // Generate renewable output based on weather conditions
  const renewableOutput = forecastData.map(weather => {
    const solarComponent = Math.max(0, 3000 * (1 - (weather.cloud_cover || 0) / 100));
    const windComponent = (weather.wind_speed || 0) * 200;
    return solarComponent + windComponent + 2000; // Base renewable + calculated
  });

  const handleZoneChange = (value: string) => {
    setSelectedZone(value);
  };

  // Get a user-friendly display name for the zone
  const getZoneDisplayName = (zoneName: string) => {
    const zoneDisplayNames: Record<string, string> = {
      'US-FLA-FPL': 'Florida Power & Light',
      'US-FLA-FPC': 'Florida Power Corp.',
      'US-FLA-JEA': 'Jacksonville Electric',
      'US-FLA-TAL': 'Tallahassee',
      'US-CAR-DUK': 'Duke Energy Carolinas',
      'US-CAR-SC': 'South Carolina',
      'US-SE-SOCO': 'Southern Company',
      'US-TEN-TVA': 'Tennessee Valley Authority'
    };
    return zoneDisplayNames[zoneName] || zoneName;
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Southeastern Weather Forecast</h2>
        <Select value={selectedZone} onValueChange={handleZoneChange}>
          <SelectTrigger className="w-[220px]">
            <SelectValue placeholder="Select Region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="US-FLA-FPL">Florida - Miami</SelectItem>
            <SelectItem value="US-FLA-FPC">Florida - Orlando</SelectItem>
            <SelectItem value="US-FLA-JEA">Florida - Jacksonville</SelectItem>
            <SelectItem value="US-FLA-TAL">Florida - Tallahassee</SelectItem>
            <SelectItem value="US-CAR-DUK">Carolinas - Charlotte</SelectItem>
            <SelectItem value="US-CAR-SC">South Carolina</SelectItem>
            <SelectItem value="US-SE-SOCO">Southeast - Atlanta</SelectItem>
            <SelectItem value="US-TEN-TVA">Tennessee</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {useMockData && (
        <div className="bg-amber-900/20 border border-amber-800 rounded-md p-3 mb-2">
          <p className="text-amber-300 text-sm">
            <strong>Note:</strong> Using mock data because the backend API is unavailable. Real Meteostat data will be displayed when connected.
          </p>
        </div>
      )}

      {isLoading ? (
        <Card className="p-6">
          <div className="flex items-center justify-center h-40">
            <p>Loading weather data...</p>
          </div>
        </Card>
      ) : error && !useMockData ? (
        <Card className="p-6">
          <div className="flex items-center justify-center h-40">
            <p className="text-red-500">Error loading weather data. Please try again.</p>
          </div>
        </Card>
      ) : (
        <>
          {/* Current Weather Card */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-2">
              <CardTitle>Current Conditions</CardTitle>
              <CardDescription>
                {getZoneDisplayName(selectedZone)} - {new Date(currentWeather?.timestamp || Date.now()).toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getWeatherIcon(
                    currentWeather?.temperature || 70, 
                    currentWeather?.cloud_cover, 
                    currentWeather?.precipitation, 
                    currentWeather?.wind_speed
                  )}
                  <div>
                    <h3 className="text-3xl font-bold">{Math.round(currentWeather?.temperature || 0)}°F</h3>
                    <p className="text-gray-400">
                      {getWeatherDescription(
                        currentWeather?.temperature || 70, 
                        currentWeather?.cloud_cover, 
                        currentWeather?.precipitation, 
                        currentWeather?.wind_speed
                      )}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <DropletIcon className="h-5 w-5 text-blue-400" />
                    <span>{currentWeather?.humidity || 0}% Humidity</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <WindIcon className="h-5 w-5 text-gray-400" />
                    <span>{Math.round(currentWeather?.wind_speed || 0)} mph</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CloudIcon className="h-5 w-5 text-gray-400" />
                    <span>{Math.round(currentWeather?.cloud_cover || 0)}% Clouds</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CloudRainIcon className="h-5 w-5 text-blue-400" />
                    <span>{(currentWeather?.precipitation || 0).toFixed(2)}" Precip</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 flex space-x-2">
                <Badge variant="outline" className="bg-gray-800">
                  Expected Load: {Math.round((loadData[0] || 0) / 1000)}K MW
                </Badge>
                <Badge variant="outline" className="bg-gray-800">
                  Renewable: {Math.round((renewableOutput[0] || 0) / 1000)}K MW
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Forecast Chart */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-2">
              <CardTitle>24-Hour Southeast Forecast</CardTitle>
              <CardDescription>Temperature and related energy metrics in the Southeast</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <WeatherDataChart
                  data={forecastData}
                  loadData={loadData}
                  renewableOutput={renewableOutput}
                  isLoading={isLoading}
                />
              </div>
              <div className="mt-4 text-sm text-gray-400">
                <p>Toggle chart lines by clicking the legend items. The chart shows relationships between weather conditions and energy usage in the Southeastern US.</p>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default WeatherForecast; 