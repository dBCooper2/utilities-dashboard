import { useState, useEffect } from 'react';
import { 
  WeatherData, 
  WeatherParams,
  fetchWeatherData, 
  fetchWeatherForecast, 
  fetchLatestWeatherData,
  fetchWeatherByZone
} from '../services/weatherService';

interface UseWeatherDataReturn {
  currentWeather: WeatherData | null;
  forecastData: WeatherData[];
  isLoading: boolean;
  error: Error | null;
  refreshData: (zoneName?: string) => Promise<void>;
  useMockData: boolean;
}

export const useWeatherData = (
  zoneName?: string,
  fetchForecast: boolean = true,
  limit: number = 24
): UseWeatherDataReturn => {
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(null);
  const [forecastData, setForecastData] = useState<WeatherData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [useMockData, setUseMockData] = useState<boolean>(false);

  const generateMockData = (zone: string = 'nyiso_nyc') => {
    const now = new Date();
    
    // Generate mock current weather
    const mockCurrent: WeatherData = {
      id: 1,
      zone_id: 1,
      zone_name: zone,
      zone_display_name: getZoneDisplayName(zone),
      timestamp: now.toISOString(),
      temperature: 65 + Math.random() * 15,
      humidity: 40 + Math.random() * 40,
      wind_speed: 5 + Math.random() * 15,
      wind_direction: Math.random() * 360,
      precipitation: Math.random() < 0.3 ? Math.random() * 0.5 : 0,
      cloud_cover: Math.random() * 100,
      is_forecast: false,
      created_at: now.toISOString()
    };
    
    // Generate mock forecast
    const mockForecast: WeatherData[] = Array(24).fill(0).map((_, i) => {
      const hour = new Date(now);
      hour.setHours(hour.getHours() + i);
      
      // Temperature curve - coolest at early morning, warmest in afternoon
      const hourOfDay = hour.getHours();
      const tempOffset = Math.abs(hourOfDay - 15); // Warmest at 3 PM
      const temp = 60 + (20 - (tempOffset * 1.5));
      
      // Wind is stronger at night
      const windSpeed = 10 + (hourOfDay < 6 || hourOfDay > 18 ? 5 : -2) + (Math.random() * 6 - 3);
      
      // Cloud cover
      const cloudCover = Math.max(0, Math.min(100, 
        hourOfDay < 12 ? 50 + (Math.random() * 30 - 15) : 30 + (Math.random() * 30 - 15)
      ));
      
      // Precipitation
      const precipChance = 0.1 + (cloudCover / 100) * 0.4;
      const precip = Math.random() < precipChance ? Math.random() * 0.5 : 0;
      
      return {
        id: i + 2,
        zone_id: 1,
        zone_name: zone,
        zone_display_name: getZoneDisplayName(zone),
        timestamp: hour.toISOString(),
        temperature: temp,
        humidity: 40 + Math.random() * 40,
        wind_speed: Math.max(0, windSpeed),
        wind_direction: Math.random() * 360,
        precipitation: precip,
        cloud_cover: cloudCover,
        is_forecast: true,
        created_at: now.toISOString()
      };
    });
    
    return { current: mockCurrent, forecast: mockForecast };
  };
  
  const getZoneDisplayName = (zoneName: string): string => {
    const zoneMap: Record<string, string> = {
      'nyiso_nyc': 'New York City',
      'nyiso_west': 'Western NY',
      'pjm_east': 'PJM East',
      'isone_boston': 'Boston',
      'caiso_la': 'Los Angeles'
    };
    return zoneMap[zoneName] || zoneName;
  };

  const fetchData = async (zone?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch current weather
      const currentData = await fetchLatestWeatherData(false);
      
      if (currentData && currentData.length > 0) {
        // Filter by zone if specified
        const zoneData = zone 
          ? currentData.find(data => data.zone_name === zone) 
          : currentData[0]; // Default to first zone
          
        if (zoneData) {
          setCurrentWeather(zoneData);
        }
      }
      
      // Fetch forecast data if requested
      if (fetchForecast) {
        const forecast = await fetchWeatherForecast(zone || zoneName, limit);
        setForecastData(forecast);
      }
      
      setUseMockData(false);
    } catch (err) {
      console.error('Error in useWeatherData:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch weather data'));
      
      // Fall back to mock data
      const { current, forecast } = generateMockData(zone || zoneName);
      setCurrentWeather(current);
      setForecastData(forecast);
      setUseMockData(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data on mount and when dependencies change
  useEffect(() => {
    fetchData(zoneName);
  }, [zoneName, fetchForecast, limit]);

  // Function to manually refresh the data
  const refreshData = async (zone?: string) => {
    await fetchData(zone || zoneName);
  };

  return {
    currentWeather,
    forecastData,
    isLoading,
    error,
    refreshData,
    useMockData
  };
}; 