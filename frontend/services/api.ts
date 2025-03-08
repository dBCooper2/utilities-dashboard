import axios from 'axios';

// Create an axios instance with the base URL from environment variables
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods for zones
export const zonesApi = {
  getAllZones: () => api.get('/zones'),
  getZoneByName: (zoneName: string) => api.get(`/zones/${zoneName}`),
  getZonesByRegion: (region: string) => api.get(`/zones/region/${region}`),
};

// API methods for load data
export const loadApi = {
  getLoadData: (params?: Record<string, any>) => api.get('/load', { params }),
  getLatestLoadData: (params?: Record<string, any>) => api.get('/load/latest', { params }),
  getLoadByZone: (zoneName: string, params?: Record<string, any>) => 
    api.get(`/load/zone/${zoneName}`, { params }),
};

// API methods for fuel mix data
export const fuelMixApi = {
  getFuelMixData: (params?: Record<string, any>) => api.get('/fuel-mix', { params }),
  getLatestFuelMixData: (params?: Record<string, any>) => api.get('/fuel-mix/latest', { params }),
  getFuelMixByZone: (zoneName: string, params?: Record<string, any>) => 
    api.get(`/fuel-mix/zone/${zoneName}`, { params }),
  getRenewableFuelMixData: (params?: Record<string, any>) => api.get('/fuel-mix/renewable', { params }),
};

// API methods for weather data
export const weatherApi = {
  getWeatherData: (params?: Record<string, any>) => api.get('/weather', { params }),
  getLatestWeatherData: (params?: Record<string, any>) => api.get('/weather/latest', { params }),
  getWeatherByZone: (zoneName: string, params?: Record<string, any>) => 
    api.get(`/weather/zone/${zoneName}`, { params }),
  getWeatherForecast: (params?: Record<string, any>) => api.get('/weather/forecast', { params }),
};

// API methods for interface flow data
export const interfaceApi = {
  getInterfaceFlowData: (params?: Record<string, any>) => api.get('/interface', { params }),
  getLatestInterfaceFlowData: (params?: Record<string, any>) => api.get('/interface/latest', { params }),
  getInterfaceFlowByZone: (zoneName: string, params?: Record<string, any>) => 
    api.get(`/interface/zone/${zoneName}`, { params }),
};

export default api; 