export interface LoadDataPoint {
  timestamp: string;
  value: number;
}

export interface PriceDataPoint {
  timestamp: string;
  value: number;  // $/MWh
}

export interface WeatherData {
  temperature: number | null;
  precipitation: number | null;
  wind_speed: number | null;
  timestamp: string;
}

export interface EnergyMixItem {
  source: string;
  percentage: number;
}

export interface ResortEnergyData {
  resort_id: string;
  resort_name: string;
  region: string;
  load_data: LoadDataPoint[];
  losses: LoadDataPoint[];
  lbmp_data: PriceDataPoint[];
  energy_mix: EnergyMixItem[];
  weather: WeatherData;
}

export interface InterfaceFlow {
  from_region: string;
  to_region: string;
  power_flow: number;  // MW
  scheduled_flow: number;  // MW
  transfer_limit: number | null;  // MW
  timestamp: string;
}

export interface DashboardData {
  resort_data: ResortEnergyData[];
  interface_flows: InterfaceFlow[];
  timestamp: string;
} 