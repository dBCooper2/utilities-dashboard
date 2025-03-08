'use client';

import React from 'react';
import { Bar } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface ZonalDataChartProps extends BaseChartProps {
  data?: {
    zone_name: string;
    load_mw: number;
    price: number;
    renewable_percentage: number;
  }[];
}

const ZonalDataChart: React.FC<ZonalDataChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : [
        { zone_name: 'ZONE_A', load_mw: 18500, price: 42.75, renewable_percentage: 12 },
        { zone_name: 'ZONE_B', load_mw: 12300, price: 38.50, renewable_percentage: 28 },
        { zone_name: 'ZONE_C', load_mw: 9800, price: 45.20, renewable_percentage: 8 },
        { zone_name: 'ZONE_D', load_mw: 15200, price: 40.10, renewable_percentage: 18 },
        { zone_name: 'ZONE_E', load_mw: 7500, price: 36.80, renewable_percentage: 35 },
        { zone_name: 'ZONE_F', load_mw: 5200, price: 39.90, renewable_percentage: 22 },
      ];

  // Normalize data for easier comparison
  const maxLoad = Math.max(...sampleData.map(d => d.load_mw));
  const maxPrice = Math.max(...sampleData.map(d => d.price));
  
  const chartData = {
    labels: sampleData.map(d => d.zone_name),
    datasets: [
      {
        label: 'Load (% of Peak)',
        data: sampleData.map(d => (d.load_mw / maxLoad) * 100),
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'rgba(255, 255, 255, 1)',
        borderWidth: 1,
        yAxisID: 'y',
      },
      {
        label: 'Price (% of Peak)',
        data: sampleData.map(d => (d.price / maxPrice) * 100),
        backgroundColor: 'rgba(180, 180, 180, 0.8)',
        borderColor: 'rgba(180, 180, 180, 1)',
        borderWidth: 1,
        yAxisID: 'y',
      },
      {
        label: 'Renewable %',
        data: sampleData.map(d => d.renewable_percentage),
        backgroundColor: 'rgba(120, 120, 120, 0.8)',
        borderColor: 'rgba(120, 120, 120, 1)',
        borderWidth: 1,
        yAxisID: 'y',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: {
          display: false,
        },
        title: {
          display: true,
          text: 'Zone',
        },
      },
      y: {
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Percentage',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          callback: (value: any) => `${value}%`,
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            const dataIndex = context.dataIndex;
            
            if (label === 'Load (% of Peak)') {
              const actualLoad = sampleData[dataIndex].load_mw;
              return `Load: ${actualLoad.toLocaleString()} MW (${value.toFixed(1)}% of Peak)`;
            } else if (label === 'Price (% of Peak)') {
              const actualPrice = sampleData[dataIndex].price;
              return `Price: $${actualPrice.toFixed(2)}/MWh (${value.toFixed(1)}% of Peak)`;
            } else {
              return `${label}: ${value.toFixed(1)}%`;
            }
          },
        },
      },
      legend: {
        position: 'top' as const,
        labels: {
          boxWidth: 12,
          padding: 10,
          font: {
            size: 11,
          },
        },
      },
    },
  };

  return (
    <BaseChart isLoading={isLoading} height={height} width={width}>
      <Bar data={chartData} options={chartOptions} />
    </BaseChart>
  );
};

export default ZonalDataChart; 