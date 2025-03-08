'use client';

import React from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register all Chart.js components
ChartJS.register(...registerables);

// Set default Chart.js options for black and white theme
ChartJS.defaults.color = '#E5E5E5'; // text color
ChartJS.defaults.borderColor = 'rgba(255, 255, 255, 0.2)'; // grid lines
ChartJS.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.1)';
ChartJS.defaults.plugins.tooltip!.backgroundColor = 'rgba(0, 0, 0, 0.8)';
ChartJS.defaults.plugins.tooltip!.titleColor = '#FFFFFF';
ChartJS.defaults.plugins.tooltip!.bodyColor = '#E5E5E5';
ChartJS.defaults.plugins.tooltip!.borderColor = 'rgba(255, 255, 255, 0.2)';
ChartJS.defaults.plugins.tooltip!.borderWidth = 1;
ChartJS.defaults.plugins.legend!.labels.color = '#E5E5E5';

export interface BaseChartProps {
  isLoading?: boolean;
  height?: string | number;
  width?: string | number;
  children?: React.ReactNode;
}

const BaseChart: React.FC<BaseChartProps> = ({
  isLoading = false,
  height = '100%',
  width = '100%',
  children,
}) => {
  if (isLoading) {
    return (
      <div
        className="flex items-center justify-center"
        style={{ height, width }}
      >
        <div className="animate-pulse flex space-x-2">
          <div className="h-2 w-2 bg-white rounded-full"></div>
          <div className="h-2 w-2 bg-white rounded-full"></div>
          <div className="h-2 w-2 bg-white rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="energy-chart-container"
      style={{ height, width }}
    >
      {children}
    </div>
  );
};

export default BaseChart; 