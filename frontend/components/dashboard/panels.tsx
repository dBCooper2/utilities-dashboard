import { ReactNode } from "react";
import { 
  ChartBarIcon,
  ChartPieIcon,
  ArrowPathIcon,
  BoltIcon,
  PresentationChartLineIcon,
  FireIcon,
  ArrowsUpDownIcon,
  MapPinIcon,
  CloudIcon
} from "@heroicons/react/24/outline";

export interface PanelData {
  id: string;
  title: string;
  description: string;
  icon: ReactNode;
}

export const panels: PanelData[] = [
  {
    id: "day-ahead-market",
    title: "Day-Ahead Market Zonal LMBP",
    description: "View zonal pricing data from the day-ahead market",
    icon: <ChartBarIcon className="h-5 w-5" />,
  },
  {
    id: "fuel-mix-chart",
    title: "Fuel Mix Chart",
    description: "Visualize the current generation mix by fuel type",
    icon: <ChartPieIcon className="h-5 w-5" />,
  },
  {
    id: "interface-data",
    title: "Interface Data",
    description: "Monitor interface data across the grid",
    icon: <ArrowPathIcon className="h-5 w-5" />,
  },
  {
    id: "load-with-losses",
    title: "Load with Losses",
    description: "Track load with transmission and distribution losses",
    icon: <BoltIcon className="h-5 w-5" />,
  },
  {
    id: "load-vs-lmbp",
    title: "Load vs. LMBP",
    description: "Compare load profiles against locational marginal prices",
    icon: <PresentationChartLineIcon className="h-5 w-5" />,
  },
  {
    id: "daily-fuel-mix",
    title: "Daily Fuel Mix",
    description: "View daily generation by fuel type",
    icon: <FireIcon className="h-5 w-5" />,
  },
  {
    id: "interface-flows",
    title: "Interface Flows",
    description: "Visualize power flows across interfaces",
    icon: <ArrowsUpDownIcon className="h-5 w-5" />,
  },
  {
    id: "zonal-data",
    title: "Zonal Data",
    description: "Access detailed zonal information",
    icon: <MapPinIcon className="h-5 w-5" />,
  },
  {
    id: "weather-data",
    title: "Weather Data",
    description: "Check weather conditions affecting the grid",
    icon: <CloudIcon className="h-5 w-5" />,
  },
]; 