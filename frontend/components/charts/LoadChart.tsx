'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface LoadChartProps extends BaseChartProps {
  data?: {
    timestamp: string;
    load_mw: number;
    losses_mw?: number;
    zone: string;
  }[];
}

const LoadChart: React.FC<LoadChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : Array(24).fill(0).map((_, i) => {
        // Create a time-dependent load curve with peak around 3-6 PM
        const hour = i;
        const baseline = 15000; // Base load in MW
        const peakTime = 16; // 4 PM peak
        const peakOffset = Math.abs(hour - peakTime);
        const peakFactor = Math.max(0, 8000 - peakOffset * 900);
        const randomFactor = Math.random() * 300;
        
        const load = baseline + peakFactor + randomFactor;
        const losses = load * 0.03 + Math.random() * 50; // 3% losses plus some random variation
        
        return {
          timestamp: new Date(new Date().setHours(hour, 0, 0, 0)).toISOString(),
          load_mw: load,
          losses_mw: losses,
          zone: 'SAMPLE'
        };
      });

  const chartData = {
    labels: sampleData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Load (MW)',
        data: sampleData.map(d => d.load_mw),
        borderColor: 'rgba(255, 255, 255, 0.9)', // white
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        pointRadius: 2,
        pointBackgroundColor: 'rgba(255, 255, 255, 0.9)',
        pointBorderColor: '#000000',
        pointHoverRadius: 5,
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'Losses (MW)',
        data: sampleData.map(d => d.losses_mw || 0),
        borderColor: 'rgba(180, 180, 180, 0.8)', // light gray
        backgroundColor: 'rgba(180, 180, 180, 0.1)',
        borderWidth: 1.5,
        pointRadius: 1,
        pointBackgroundColor: 'rgba(180, 180, 180, 0.8)',
        pointBorderColor: '#000000',
        pointHoverRadius: 3,
        fill: true,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Load (MW)',
        },
        grid: {
          drawOnChartArea: true,
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Losses (MW)',
        },
        grid: {
          drawOnChartArea: false,
        },
        min: 0,
      },
      x: {
        grid: {
          display: false,
        },
        title: {
          display: true,
          text: 'Hour',
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const datasetLabel = context.dataset.label || '';
            const value = context.parsed.y;
            return `${datasetLabel}: ${value.toLocaleString()} MW`;
          },
        },
      },
    },
  };

  return (
    <BaseChart isLoading={isLoading} height={height} width={width}>
      <Line data={chartData} options={chartOptions} />
    </BaseChart>
  );
};

export default LoadChart; 