'use client';

import React from 'react';
import { Pie } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface FuelMixChartProps extends BaseChartProps {
  data?: {
    fuel_type: string;
    percentage: number;
    is_renewable: boolean;
  }[];
}

const FuelMixChart: React.FC<FuelMixChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : [
        { fuel_type: 'Coal', percentage: 25, is_renewable: false },
        { fuel_type: 'Natural Gas', percentage: 35, is_renewable: false },
        { fuel_type: 'Nuclear', percentage: 20, is_renewable: false },
        { fuel_type: 'Wind', percentage: 10, is_renewable: true },
        { fuel_type: 'Solar', percentage: 6, is_renewable: true },
        { fuel_type: 'Hydro', percentage: 4, is_renewable: true },
      ];

  // Sort data to group renewables together
  const sortedData = [...sampleData].sort((a, b) => {
    if (a.is_renewable && !b.is_renewable) return -1;
    if (!a.is_renewable && b.is_renewable) return 1;
    return 0;
  });

  // Color palette - black and white shades
  const getColor = (index: number, isRenewable: boolean) => {
    const renewableColors = [
      'rgba(255, 255, 255, 0.95)',  // white
      'rgba(230, 230, 230, 0.9)',   // light gray
      'rgba(200, 200, 200, 0.9)',   // lighter gray
      'rgba(180, 180, 180, 0.9)',   // light gray
    ];
    
    const nonRenewableColors = [
      'rgba(70, 70, 70, 0.9)',      // dark gray
      'rgba(100, 100, 100, 0.9)',   // medium gray
      'rgba(130, 130, 130, 0.9)',   // medium-light gray
      'rgba(160, 160, 160, 0.9)',   // light gray
    ];
    
    return isRenewable 
      ? renewableColors[index % renewableColors.length]
      : nonRenewableColors[index % nonRenewableColors.length];
  };

  const chartData = {
    labels: sortedData.map(d => d.fuel_type),
    datasets: [
      {
        data: sortedData.map(d => d.percentage),
        backgroundColor: sortedData.map((d, i) => getColor(i, d.is_renewable)),
        borderColor: sortedData.map(d => d.is_renewable 
          ? 'rgba(255, 255, 255, 1)' 
          : 'rgba(100, 100, 100, 1)'
        ),
        borderWidth: 1,
        hoverOffset: 10,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          boxWidth: 12,
          padding: 15,
          font: {
            size: 11,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => `${context.label}: ${context.parsed}%`,
        },
      },
    },
  };

  return (
    <BaseChart isLoading={isLoading} height={height} width={width}>
      <Pie data={chartData} options={chartOptions} />
    </BaseChart>
  );
};

export default FuelMixChart; 