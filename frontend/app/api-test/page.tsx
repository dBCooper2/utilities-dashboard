'use client';

import React, { useState } from 'react';
import { FiChevronDown, FiChevronRight, FiClock, FiRefreshCw } from 'react-icons/fi';

const endpoints = [
  {
    name: 'Zones',
    endpoint: '/zones',
    description: 'Get all energy zones in the southeastern US',
    params: [],
  },
  {
    name: 'Load Data',
    endpoint: '/load',
    description: 'Get load data with optional filtering',
    params: [
      { name: 'zone_name', type: 'string', required: false, description: 'Zone name (e.g., US-FLA-FPL)' },
      { name: 'start_date', type: 'datetime', required: false, description: 'Start date (ISO format)' },
      { name: 'end_date', type: 'datetime', required: false, description: 'End date (ISO format)' },
      { name: 'is_day_ahead', type: 'boolean', required: false, description: 'Whether to get day-ahead data' },
      { name: 'is_forecast', type: 'boolean', required: false, description: 'Whether to get forecast data' },
      { name: 'limit', type: 'integer', required: false, description: 'Maximum number of records to return', default: '100' },
    ],
  },
  {
    name: 'Latest Load Data',
    endpoint: '/load/latest',
    description: 'Get the latest load data for all zones',
    params: [
      { name: 'is_day_ahead', type: 'boolean', required: false, description: 'Whether to get day-ahead data' },
    ],
  },
  {
    name: 'Fuel Mix Data',
    endpoint: '/fuel-mix',
    description: 'Get fuel mix data with optional filtering',
    params: [
      { name: 'zone_name', type: 'string', required: false, description: 'Zone name (e.g., US-FLA-FPL)' },
      { name: 'fuel_type', type: 'string', required: false, description: 'Fuel type (e.g., COL, NG, NUC)' },
      { name: 'is_renewable', type: 'boolean', required: false, description: 'Whether to get renewable fuel data' },
      { name: 'start_date', type: 'datetime', required: false, description: 'Start date (ISO format)' },
      { name: 'end_date', type: 'datetime', required: false, description: 'End date (ISO format)' },
      { name: 'is_forecast', type: 'boolean', required: false, description: 'Whether to get forecast data' },
      { name: 'limit', type: 'integer', required: false, description: 'Maximum number of records to return', default: '100' },
    ],
  },
  {
    name: 'Weather Data',
    endpoint: '/weather',
    description: 'Get weather data with optional filtering',
    params: [
      { name: 'zone_name', type: 'string', required: false, description: 'Zone name (e.g., US-FLA-FPL)' },
      { name: 'start_date', type: 'datetime', required: false, description: 'Start date (ISO format)' },
      { name: 'end_date', type: 'datetime', required: false, description: 'End date (ISO format)' },
      { name: 'is_forecast', type: 'boolean', required: false, description: 'Whether to get forecast data' },
      { name: 'limit', type: 'integer', required: false, description: 'Maximum number of records to return', default: '100' },
    ],
  },
  {
    name: 'Interface Flow Data',
    endpoint: '/interface',
    description: 'Get interface flow data with optional filtering',
    params: [
      { name: 'from_zone_name', type: 'string', required: false, description: 'Source zone name (e.g., US-FLA-FPL)' },
      { name: 'to_zone_name', type: 'string', required: false, description: 'Destination zone name (e.g., US-FLA-FPC)' },
      { name: 'start_date', type: 'datetime', required: false, description: 'Start date (ISO format)' },
      { name: 'end_date', type: 'datetime', required: false, description: 'End date (ISO format)' },
      { name: 'is_day_ahead', type: 'boolean', required: false, description: 'Whether to get day-ahead data' },
      { name: 'is_forecast', type: 'boolean', required: false, description: 'Whether to get forecast data' },
      { name: 'limit', type: 'integer', required: false, description: 'Maximum number of records to return', default: '100' },
    ],
  },
];

const APITestPage: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState(endpoints[0]);
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  const [params, setParams] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleEndpoint = (name: string) => {
    if (expandedEndpoint === name) {
      setExpandedEndpoint(null);
    } else {
      setExpandedEndpoint(name);
      const endpoint = endpoints.find((e) => e.name === name);
      if (endpoint) {
        setSelectedEndpoint(endpoint);
        // Reset params
        setParams({});
      }
    }
  };

  const handleParamChange = (paramName: string, value: string) => {
    setParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  const buildQueryString = () => {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        queryParams.append(key, value);
      }
    });
    return queryParams.toString();
  };

  const handleTestAPI = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const queryString = buildQueryString();
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${selectedEndpoint.endpoint}${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'An error occurred');
      }
      
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">API Testing</h1>
          <p className="text-gray-400">
            Test the energy dashboard API endpoints and view response data
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Endpoints List */}
          <div className="lg:col-span-3 bg-gray-900 bg-opacity-60 backdrop-blur-md rounded-xl p-4 border border-gray-800">
            <h2 className="text-xl font-semibold text-white mb-4">Endpoints</h2>
            <ul className="space-y-2">
              {endpoints.map((endpoint) => (
                <li key={endpoint.name}>
                  <button
                    className={`w-full text-left flex items-center px-3 py-2 rounded-lg transition-colors ${
                      expandedEndpoint === endpoint.name
                        ? 'bg-blue-900 bg-opacity-30 text-blue-400'
                        : 'text-gray-300 hover:bg-gray-800'
                    }`}
                    onClick={() => toggleEndpoint(endpoint.name)}
                  >
                    {expandedEndpoint === endpoint.name ? (
                      <FiChevronDown className="mr-2 flex-shrink-0" />
                    ) : (
                      <FiChevronRight className="mr-2 flex-shrink-0" />
                    )}
                    <span>{endpoint.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Request Panel */}
          <div className="lg:col-span-9 bg-gray-900 bg-opacity-60 backdrop-blur-md rounded-xl p-6 border border-gray-800">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">{selectedEndpoint.name}</h2>
              <div className="flex items-center mb-4">
                <span className="text-blue-400 font-mono mr-2">GET</span>
                <span className="text-gray-300 font-mono">{selectedEndpoint.endpoint}</span>
              </div>
              <p className="text-gray-400">{selectedEndpoint.description}</p>
            </div>

            {selectedEndpoint.params.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-medium text-white mb-3">Parameters</h3>
                <div className="space-y-4">
                  {selectedEndpoint.params.map((param) => (
                    <div key={param.name} className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                      <div className="md:col-span-3">
                        <label
                          htmlFor={param.name}
                          className="block text-sm font-medium text-gray-300"
                        >
                          {param.name}
                          {param.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                      </div>
                      <div className="md:col-span-4">
                        <input
                          type={param.type === 'datetime' ? 'datetime-local' : 'text'}
                          id={param.name}
                          name={param.name}
                          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={param.default || ''}
                          onChange={(e) => handleParamChange(param.name, e.target.value)}
                          value={params[param.name] || ''}
                        />
                      </div>
                      <div className="md:col-span-5">
                        <p className="text-xs text-gray-400">{param.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between">
              <button
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleTestAPI}
                disabled={loading}
              >
                {loading ? (
                  <FiRefreshCw className="animate-spin" />
                ) : (
                  <FiClock />
                )}
                {loading ? 'Fetching...' : 'Test Endpoint'}
              </button>
              <div className="text-sm text-gray-400">
                {result && !error && (
                  <span>
                    {Array.isArray(result)
                      ? `${result.length} record(s) returned`
                      : 'Response received'}
                  </span>
                )}
              </div>
            </div>

            {error && (
              <div className="mt-6 p-3 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg">
                <p className="text-red-400">{error}</p>
              </div>
            )}

            {result && !error && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-white mb-3">Response</h3>
                <div className="bg-gray-800 rounded-lg p-4 overflow-auto max-h-96">
                  <pre className="text-gray-300 text-sm font-mono whitespace-pre-wrap">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default APITestPage; 