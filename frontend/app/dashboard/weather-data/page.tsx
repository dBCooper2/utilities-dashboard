'use client';

import WeatherForecast from '../../../components/WeatherForecast';

export default function WeatherDataPage() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Weather Data</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Weather conditions and their impact on energy demand and production
        </p>
      </div>
      
      <WeatherForecast />
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">About Weather and Energy</h2>
        <p className="mb-4">
          Weather conditions significantly impact both energy demand and production:
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Temperature drives heating and cooling loads</li>
          <li>Wind speed directly affects wind power generation</li>
          <li>Cloud coverage impacts solar output</li>
          <li>Precipitation can affect hydroelectric generation</li>
          <li>Extreme weather events can disrupt transmission and distribution</li>
        </ul>
        <p className="mt-4">
          The forecast data visualizes these relationships, showing how changes in weather
          conditions correlate with changes in system load and renewable energy production.
        </p>
      </div>
    </div>
  );
} 