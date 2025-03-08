'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  LineChart, 
  BarChart3, 
  PieChart,
  Zap, 
  ArrowRightLeft,
  CloudSun,
  Grid
} from 'lucide-react';

// Import chart components
import PriceChart from './charts/PriceChart';
import FuelMixChart from './charts/FuelMixChart';
import LoadChart from './charts/LoadChart';
import InterfaceFlowChart from './charts/InterfaceFlowChart';

// Import new chart components
import LoadVsPriceChart from './charts/LoadVsPriceChart';
import DailyFuelMixChart from './charts/DailyFuelMixChart';
import ZonalDataChart from './charts/ZonalDataChart';
import WeatherDataChart from './charts/WeatherDataChart';

const DashboardPanels: React.FC = () => {
  const [expandedPanel, setExpandedPanel] = useState(0);

  const panels = [
    {
      id: 0,
      title: 'Day-Ahead Market Zonal LMBP',
      description: 'View locational marginal prices across different zones for day-ahead market planning.',
      icon: <LineChart className="h-5 w-5 text-white" />,
      actionLabel: 'View Prices',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/day-ahead-prices',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Locational Marginal Pricing by zone</p>
          <div className="h-56 energy-chart-container">
            <PriceChart />
          </div>
        </div>
      ),
    },
    {
      id: 1,
      title: 'Fuel Mix Chart',
      description: 'Analyze the composition of energy generation sources across different regions.',
      icon: <PieChart className="h-5 w-5 text-white" />,
      actionLabel: 'View Chart',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/fuel-mix',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Energy generation by fuel type</p>
          <div className="h-56 energy-chart-container">
            <FuelMixChart />
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: 'Interface Data',
      description: 'Monitor energy flow between different zones and regions in the grid.',
      icon: <ArrowRightLeft className="h-5 w-5 text-white" />,
      actionLabel: 'View Flows',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/interface-data',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Interface flow between zones</p>
          <div className="h-56 energy-chart-container">
            <InterfaceFlowChart />
          </div>
        </div>
      ),
    },
    {
      id: 3,
      title: 'Load with Losses',
      description: 'Track electricity load and transmission losses across the system.',
      icon: <Zap className="h-5 w-5 text-white" />,
      actionLabel: 'View Load',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/load-data',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Load and transmission losses over time</p>
          <div className="h-56 energy-chart-container">
            <LoadChart />
          </div>
        </div>
      ),
    },
    {
      id: 4,
      title: 'Load vs. LMBP',
      description: 'Compare electricity demand against price variations to identify patterns.',
      icon: <BarChart3 className="h-5 w-5 text-white" />,
      actionLabel: 'Compare Data',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/load-vs-price',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Correlation between load and price</p>
          <div className="h-56 energy-chart-container">
            <LoadVsPriceChart />
          </div>
        </div>
      ),
    },
    {
      id: 5,
      title: 'Daily Fuel Mix',
      description: 'View daily changes in energy generation sources and their proportions.',
      icon: <PieChart className="h-5 w-5 text-white" />,
      actionLabel: 'View Daily Mix',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/daily-fuel-mix',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Fuel mix changes over time</p>
          <div className="h-56 energy-chart-container">
            <DailyFuelMixChart />
          </div>
        </div>
      ),
    },
    {
      id: 6,
      title: 'Zonal Data',
      description: 'Explore detailed data for specific energy zones in the southeastern US.',
      icon: <Grid className="h-5 w-5 text-white" />,
      actionLabel: 'View Zones',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/zonal-data',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Zonal metrics and comparison</p>
          <div className="h-56 energy-chart-container">
            <ZonalDataChart />
          </div>
        </div>
      ),
    },
    {
      id: 7,
      title: 'Weather Data',
      description: 'See how weather conditions affect energy demand and production.',
      icon: <CloudSun className="h-5 w-5 text-white" />,
      actionLabel: 'View Weather',
      gradientColor: 'from-white/10',
      linkPath: '/dashboard/weather-data',
      content: (
        <div className="w-full h-full">
          <p className="mb-4 text-sm text-gray-300">Weather conditions and energy impact</p>
          <div className="h-56 energy-chart-container">
            <WeatherDataChart />
          </div>
        </div>
      ),
    },
  ];

  const handlePanelClick = (id: number) => {
    setExpandedPanel(id === expandedPanel ? -1 : id);
  };

  return (
    <div className="flex flex-1 space-x-2 overflow-x-auto py-4 px-1 items-center justify-center">
      {panels.map((panel) => (
        <div
          key={panel.id}
          className={`energy-panel flex h-[450px] cursor-pointer ${
            expandedPanel === panel.id 
              ? 'energy-panel-expanded' 
              : 'energy-panel-collapsed'
          }`}
          onClick={() => handlePanelClick(panel.id)}
        >
          {/* Gradient background effect */}
          <div 
            className={`energy-panel-gradient ${panel.gradientColor}`}
          />
          
          {/* Glass shine effect */}
          {expandedPanel === panel.id && (
            <div className="energy-panel-shine" />
          )}
          
          {/* Collapsed state */}
          {expandedPanel !== panel.id && (
            <div className="flex flex-col justify-center items-center w-full">
              <div className="flex flex-col items-center justify-center h-full">
                <span className="transform -rotate-90 whitespace-nowrap text-sm font-medium tracking-wide text-gray-300 opacity-90">
                  {panel.title}
                </span>
              </div>
            </div>
          )}
          
          {/* Expanded state */}
          {expandedPanel === panel.id && (
            <div className="flex flex-col p-5 h-full w-full overflow-hidden animate-fadeIn">
              <div className="flex items-center mb-3">
                <div className="p-2 rounded-lg bg-zinc-800/50 mr-3">
                  {panel.icon}
                </div>
                <h3 className="text-lg font-medium text-white">{panel.title}</h3>
              </div>
              
              <p className="text-gray-300 mb-5 text-sm leading-relaxed">
                {panel.description}
              </p>
              
              <div className="flex-1">
                {panel.content}
              </div>
              
              <div className="mt-auto pt-3">
                <Link href={panel.linkPath} className="flex items-center space-x-2 bg-zinc-800 hover:bg-zinc-700 px-4 py-2 rounded-lg text-sm transition-colors duration-300">
                  <span>{panel.actionLabel}</span>
                  <span className="w-4 h-4 ml-2">{panel.icon}</span>
                </Link>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default DashboardPanels; 