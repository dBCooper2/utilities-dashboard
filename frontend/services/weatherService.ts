import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002';

export interface WeatherData {
  id?: number;
  zone_id: number;
  zone_name?: string;
  zone_display_name?: string;
  timestamp: string;
  temperature: number;
  humidity?: number;
  wind_speed?: number;
  wind_direction?: number;
  precipitation?: number;
  cloud_cover?: number;
  is_forecast: boolean;
  created_at?: string;
}

export interface WeatherParams {
  zone_name?: string;
  start_date?: string;
  end_date?: string;
  is_forecast?: boolean;
  limit?: number;
}

/**
 * Fetch latest weather data for all zones
 */
export const fetchLatestWeatherData = async (is_forecast: boolean = false): Promise<WeatherData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/weather/latest`, {
      params: { is_forecast }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching latest weather data:', error);
    throw error;
  }
};

/**
 * Fetch weather data with optional filters
 */
export const fetchWeatherData = async (params: WeatherParams): Promise<WeatherData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/weather`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching weather data:', error);
    throw error;
  }
};

/**
 * Fetch weather forecast data
 */
export const fetchWeatherForecast = async (zone_name?: string, limit?: number): Promise<WeatherData[]> => {
  try {
    const params: WeatherParams = {
      is_forecast: true,
      limit: limit || 24
    };
    
    if (zone_name) {
      params.zone_name = zone_name;
    }
    
    const response = await axios.get(`${API_BASE_URL}/weather/forecast`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching weather forecast:', error);
    throw error;
  }
};

/**
 * Fetch weather data for a specific zone
 */
export const fetchWeatherByZone = async (
  zone_name: string, 
  params: Omit<WeatherParams, 'zone_name'> = {}
): Promise<WeatherData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/weather/zone/${zone_name}`, { params });
    return response.data;
  } catch (error) {
    console.error(`Error fetching weather data for zone ${zone_name}:`, error);
    throw error;
  }
}; 