'use client';

import React from 'react';
import { Line } from 'react-chartjs-2';
import BaseChart, { BaseChartProps } from './BaseChart';
import { WeatherData } from '../../services/weatherService';

interface WeatherDataChartProps extends BaseChartProps {
  data?: WeatherData[];
  loadData?: number[];
  renewableOutput?: number[];
}

const WeatherDataChart: React.FC<WeatherDataChartProps> = ({
  data = [],
  loadData = [],
  renewableOutput = [],
  isLoading = false,
  height = '100%',
  width = '100%',
}) => {
  // Generate sample data if no data is provided
  const sampleData = data.length > 0
    ? data.map((item, index) => ({
        timestamp: item.timestamp,
        temperature: item.temperature,
        load_mw: loadData[index] || 15000 + Math.random() * 5000, // Use real load if available or mock
        renewable_output_mw: renewableOutput[index] || 5000 + Math.random() * 3000, // Use real renewable or mock
        wind_speed: item.wind_speed || 0,
        precipitation: item.precipitation || 0,
        cloud_cover: item.cloud_cover || 0
      }))
    : Array(24).fill(0).map((_, i) => {
        // Create time-dependent data
        const hour = i;
        
        // Temperature curve - coolest at early morning, warmest in afternoon
        const baseTemp = 60; // Base temperature in F
        const tempRange = 20; // Range of temperature variation
        const tempPeak = 15; // Hour of peak temperature (3 PM)
        const tempOffset = Math.abs(hour - tempPeak);
        const temperature = baseTemp + (tempRange - (tempOffset * 1.5));
        
        // Load tends to follow temperature with peaks in morning and evening
        const baseLoad = 15000; // Base load in MW
        const morningPeak = hour === 8 ? 3000 : hour === 7 || hour === 9 ? 2000 : hour === 6 || hour === 10 ? 1000 : 0;
        const eveningPeak = hour === 19 ? 4000 : hour === 18 || hour === 20 ? 3000 : hour === 17 || hour === 21 ? 1500 : 0;
        const tempFactor = Math.max(0, (temperature - 65) * 100); // AC load when hot
        const load = baseLoad + morningPeak + eveningPeak + tempFactor + (Math.random() * 300);
        
        // Wind is stronger at night, weaker during day
        const baseWind = 10; // Base wind speed in mph
        const dayFactor = hour >= 8 && hour <= 18 ? -3 : 3;
        const wind_speed = baseWind + dayFactor + (Math.random() * 5 - 2.5);
        
        // Simulate cloud cover (higher in morning, clearing through day)
        const baseClouds = hour < 12 ? 50 : 30;
        const cloud_cover = Math.max(0, Math.min(100, baseClouds + (Math.random() * 30 - 15)));
        
        // Precipitation is random with higher chance in morning
        const precipChance = hour < 10 ? 0.3 : 0.1;
        const precipitation = Math.random() < precipChance ? Math.random() * 0.5 : 0;
        
        // Renewable output based on wind and solar
        const windOutput = 2000 * (wind_speed / 15); // Wind scales with wind speed
        const solarBase = hour >= 6 && hour <= 18 ? 3000 * Math.sin(Math.PI * (hour - 6) / 12) : 0;
        const solarOutput = solarBase * (1 - (cloud_cover / 100) * 0.8); // Solar reduced by cloud cover
        const renewable_output_mw = windOutput + solarOutput;
        
        return {
          timestamp: new Date(new Date().setHours(hour, 0, 0, 0)).toISOString(),
          temperature,
          load_mw: load,
          renewable_output_mw,
          wind_speed,
          precipitation,
          cloud_cover
        };
      });

  const chartData = {
    labels: sampleData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Temperature (°F)',
        data: sampleData.map(d => d.temperature),
        borderColor: 'rgba(255, 255, 255, 0.9)',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        pointRadius: 2,
        pointBackgroundColor: 'rgba(255, 255, 255, 1)',
        pointBorderColor: '#000000',
        yAxisID: 'y-temp',
        hidden: false,
      },
      {
        label: 'Load (MW)',
        data: sampleData.map(d => d.load_mw),
        borderColor: 'rgba(200, 200, 200, 0.9)',
        backgroundColor: 'rgba(200, 200, 200, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: 'y-load',
        hidden: false,
      },
      {
        label: 'Renewable Output (MW)',
        data: sampleData.map(d => d.renewable_output_mw),
        borderColor: 'rgba(150, 150, 150, 0.9)',
        backgroundColor: 'rgba(150, 150, 150, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: 'y-load',
        hidden: false,
      },
      {
        label: 'Wind Speed (mph)',
        data: sampleData.map(d => d.wind_speed),
        borderColor: 'rgba(100, 100, 100, 0.9)',
        borderDash: [5, 5],
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        pointRadius: 0,
        yAxisID: 'y-wind',
        hidden: true,
      },
      {
        label: 'Precipitation (in)',
        data: sampleData.map(d => d.precipitation),
        borderColor: 'rgba(110, 150, 200, 0.9)',
        borderDash: [5, 5],
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        pointRadius: 0,
        yAxisID: 'y-precip',
        hidden: true,
      },
      {
        label: 'Cloud Cover (%)',
        data: sampleData.map(d => d.cloud_cover),
        borderColor: 'rgba(80, 80, 80, 0.9)',
        borderDash: [2, 2],
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        pointRadius: 0,
        yAxisID: 'y-clouds',
        hidden: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      'y-temp': {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Temperature (°F)',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      'y-load': {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'MW',
        },
        grid: {
          display: false,
        },
      },
      'y-wind': {
        type: 'linear' as const,
        display: false,
        position: 'right' as const,
        min: 0,
        max: 30,
        title: {
          display: true,
          text: 'Wind Speed (mph)',
        },
      },
      'y-precip': {
        type: 'linear' as const,
        display: false,
        position: 'right' as const,
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'Precipitation (in)',
        },
      },
      'y-clouds': {
        type: 'linear' as const,
        display: false,
        position: 'right' as const,
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Cloud Cover (%)',
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
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            
            if (label === 'Temperature (°F)') {
              return `${label}: ${value.toFixed(1)}°F`;
            } else if (label === 'Load (MW)' || label === 'Renewable Output (MW)') {
              return `${label}: ${value.toLocaleString()} MW`;
            } else if (label === 'Wind Speed (mph)') {
              return `${label}: ${value.toFixed(1)} mph`;
            } else if (label === 'Precipitation (in)') {
              return `${label}: ${value.toFixed(2)} in`;
            } else if (label === 'Cloud Cover (%)') {
              return `${label}: ${value.toFixed(0)}%`;
            } else {
              return `${label}: ${value}`;
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
        onClick: function(e: any, legendItem: any, legend: any) {
          const index = legendItem.datasetIndex;
          const chart = legend.chart;
          const meta = chart.getDatasetMeta(index);
          
          // Toggle the visibility
          meta.hidden = !meta.hidden;
          
          // Show/hide related axes when toggling datasets
          if (index === 3) { // Wind Speed
            chart.options.scales['y-wind'].display = !meta.hidden;
          } else if (index === 4) { // Precipitation
            chart.options.scales['y-precip'].display = !meta.hidden;
          } else if (index === 5) { // Cloud Cover
            chart.options.scales['y-clouds'].display = !meta.hidden;
          }
          
          chart.update();
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

export default WeatherDataChart; 