'use client';

import React from 'react';
import { Bar } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface InterfaceFlowChartProps extends BaseChartProps {
  data?: {
    timestamp: string;
    from_zone: string;
    to_zone: string;
    flow_mw: number;
  }[];
}

const InterfaceFlowChart: React.FC<InterfaceFlowChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : [
        { from_zone: 'ZONE_A', to_zone: 'ZONE_B', flow_mw: 1200, timestamp: new Date().toISOString() },
        { from_zone: 'ZONE_A', to_zone: 'ZONE_C', flow_mw: 800, timestamp: new Date().toISOString() },
        { from_zone: 'ZONE_B', to_zone: 'ZONE_D', flow_mw: 500, timestamp: new Date().toISOString() },
        { from_zone: 'ZONE_C', to_zone: 'ZONE_A', flow_mw: -350, timestamp: new Date().toISOString() },
        { from_zone: 'ZONE_D', to_zone: 'ZONE_A', flow_mw: -600, timestamp: new Date().toISOString() },
        { from_zone: 'ZONE_D', to_zone: 'ZONE_C', flow_mw: 250, timestamp: new Date().toISOString() },
      ];

  // Process data to get unique zone pairs and their flow values
  const interfacePairs = sampleData.map(d => `${d.from_zone} ➝ ${d.to_zone}`);
  const flowValues = sampleData.map(d => d.flow_mw);

  const chartData = {
    labels: interfacePairs,
    datasets: [
      {
        label: 'Flow (MW)',
        data: flowValues,
        backgroundColor: flowValues.map(value => 
          value >= 0 
            ? 'rgba(255, 255, 255, 0.8)' // white for positive flows
            : 'rgba(100, 100, 100, 0.8)'  // gray for negative flows
        ),
        borderColor: flowValues.map(value => 
          value >= 0 
            ? 'rgba(255, 255, 255, 1)' 
            : 'rgba(100, 100, 100, 1)'
        ),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y' as const,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Flow (MW)',
        },
        grid: {
          color: 'rgba(75, 85, 99, 0.2)',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Interface',
        },
        grid: {
          display: false,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.parsed.x;
            return `Flow: ${value.toLocaleString()} MW`;
          },
          title: (tooltipItems: any) => {
            return tooltipItems[0].label;
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

export default InterfaceFlowChart; 