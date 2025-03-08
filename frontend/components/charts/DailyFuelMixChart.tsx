'use client';

import React from 'react';
import { Bar } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';

interface DailyFuelMixChartProps extends BaseChartProps {
  data?: {
    timestamp: string;
    fuel_type: string;
    percentage: number;
  }[];
}

const DailyFuelMixChart: React.FC<DailyFuelMixChartProps> = ({
  data = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Define fuel types and their order
  const fuelTypes = ['Nuclear', 'Coal', 'Natural Gas', 'Hydro', 'Wind', 'Solar'];
  
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data
    : Array(24).fill(0).flatMap((_, hour) => {
        // Create time-dependent data with different fuel percentages based on time of day
        let nuclear = 20; // Constant base
        let coal = 25 - Math.floor(hour / 8) * 5; // Decreases throughout the day
        let naturalGas = 20 + Math.floor(hour / 4) * 5; // Increases to meet peak demand
        
        // Solar increases during daylight hours
        let solar = hour >= 6 && hour <= 18 
          ? 15 * Math.sin(Math.PI * (hour - 6) / 12) 
          : 0;
        
        // Wind varies with some randomness
        let wind = 10 + Math.sin(hour / 6 * Math.PI) * 3 + Math.random() * 5;
        
        // Hydro makes up the difference
        let hydro = 100 - nuclear - coal - naturalGas - solar - wind;
        hydro = Math.max(0, hydro); // Ensure no negative values
        
        return fuelTypes.map(type => {
          let percentage;
          switch(type) {
            case 'Nuclear': percentage = nuclear; break;
            case 'Coal': percentage = coal; break;
            case 'Natural Gas': percentage = naturalGas; break;
            case 'Hydro': percentage = hydro; break;
            case 'Wind': percentage = wind; break;
            case 'Solar': percentage = solar; break;
            default: percentage = 0;
          }
          
          return {
            timestamp: new Date(new Date().setHours(hour, 0, 0, 0)).toISOString(),
            fuel_type: type,
            percentage
          };
        });
      });

  // Group by hour for stacked chart
  const hours = Array.from(new Set(sampleData.map(d => 
    new Date(d.timestamp).getHours()
  ))).sort((a, b) => a - b);
  
  // Generate data for each fuel type
  const datasets = fuelTypes.map((fuelType, index) => {
    // Use monochrome palette with different shades
    const shades = [
      'rgba(255, 255, 255, 0.9)', // White - for solar
      'rgba(200, 200, 200, 0.9)', // Light gray - for wind
      'rgba(160, 160, 160, 0.9)', // Medium light gray - for hydro
      'rgba(120, 120, 120, 0.9)', // Medium gray - for natural gas
      'rgba(80, 80, 80, 0.9)',    // Medium dark gray - for coal
      'rgba(40, 40, 40, 0.9)',    // Dark gray - for nuclear
    ];
    
    return {
      label: fuelType,
      data: hours.map(hour => {
        const hourData = sampleData.filter(d => 
          new Date(d.timestamp).getHours() === hour && 
          d.fuel_type === fuelType
        );
        return hourData.length > 0 ? hourData[0].percentage : 0;
      }),
      backgroundColor: shades[fuelTypes.length - 1 - index],
      borderColor: 'rgba(0, 0, 0, 0.8)',
      borderWidth: 0.5,
    };
  });

  const chartData = {
    labels: hours.map(h => `${h}:00`),
    datasets,
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        stacked: true,
        title: {
          display: true,
          text: 'Hour of Day',
        },
        grid: {
          display: false,
        },
      },
      y: {
        stacked: true,
        title: {
          display: true,
          text: 'Percentage (%)',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        min: 0,
        max: 100,
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value.toFixed(1)}%`;
          },
        },
      },
      legend: {
        position: 'bottom' as const,
        labels: {
          boxWidth: 12,
          padding: 15,
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

export default DailyFuelMixChart; 