'use client';

import React from 'react';
import { Scatter } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface LoadVsPriceChartProps extends BaseChartProps {
  data?: {
    load_mw: number;
    price: number;
    timestamp: string;
    zone: string;
  }[];
}

const LoadVsPriceChart: React.FC<LoadVsPriceChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : Array(24).fill(0).map((_, i) => {
        // Create time-dependent data
        const hour = i;
        const baseLoad = 15000; // Base load in MW
        const peakTime = 16; // 4 PM peak
        const peakOffset = Math.abs(hour - peakTime);
        const peakFactor = Math.max(0, 8000 - peakOffset * 900);
        const loadRandomFactor = Math.random() * 500;
        
        const load = baseLoad + peakFactor + loadRandomFactor;
        
        // Price tends to follow load but with some randomness
        const basePrice = 30; // Base price in $/MWh
        const loadFactor = load / 10000; // Normalize load to affect price
        const priceRandomFactor = Math.random() * 15;
        const price = basePrice + (loadFactor * 20) + priceRandomFactor;
        
        return {
          load_mw: load,
          price: price,
          timestamp: new Date(new Date().setHours(hour, 0, 0, 0)).toISOString(),
          zone: 'SAMPLE'
        };
      });

  const chartData = {
    datasets: [
      {
        label: 'Load vs Price',
        data: sampleData.map(d => ({
          x: d.load_mw,
          y: d.price,
        })),
        backgroundColor: 'rgba(255, 255, 255, 0.7)',
        borderColor: 'rgba(255, 255, 255, 0.9)',
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBorderWidth: 1,
        pointBorderColor: 'rgba(0, 0, 0, 0.8)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Load (MW)',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        min: sampleData.length > 0 ? Math.min(...sampleData.map(d => d.load_mw)) * 0.9 : 0,
      },
      y: {
        title: {
          display: true,
          text: 'Price ($/MWh)',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        min: sampleData.length > 0 ? Math.min(...sampleData.map(d => d.price)) * 0.9 : 0,
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const point = context.raw;
            return `Load: ${point.x.toLocaleString()} MW, Price: $${point.y.toFixed(2)}/MWh`;
          },
        },
      },
      legend: {
        display: false,
      },
    },
  };

  return (
    <BaseChart isLoading={isLoading} height={height} width={width}>
      <Scatter data={chartData} options={chartOptions} />
    </BaseChart>
  );
};

export default LoadVsPriceChart; 