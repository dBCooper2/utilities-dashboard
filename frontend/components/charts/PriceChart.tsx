'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface PriceChartProps extends BaseChartProps {
  data?: {
    timestamp: string;
    price: number;
    zone: string;
  }[];
}

const PriceChart: React.FC<PriceChartProps> = ({ 
  data = [],
  isLoading = false,
  height = '100%', 
  width = '100%' 
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0 ? data : Array(24).fill(0).map((_, i) => ({
    timestamp: new Date(new Date().setHours(i, 0, 0, 0)).toISOString(),
    price: Math.random() * 50 + 20, // Random price between 20 and 70
    zone: 'SAMPLE'
  }));

  const chartData = {
    labels: sampleData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'LMP Price ($/MWh)',
        data: sampleData.map(d => d.price),
        borderColor: 'rgba(255, 255, 255, 0.9)',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: 'rgba(255, 255, 255, 1)',
        pointBorderColor: '#000000',
        pointHoverRadius: 5,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(75, 85, 99, 0.2)',
        },
        ticks: {
          callback: (value: any) => `$${value}`,
        },
        title: {
          display: true,
          text: '$/MWh',
        },
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
          label: (context: any) => `$${context.parsed.y.toFixed(2)} / MWh`,
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

export default PriceChart; 