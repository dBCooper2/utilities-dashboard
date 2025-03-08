'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import LoadVsPriceChart from '../../../components/charts/LoadVsPriceChart';

export default function LoadVsPricePage() {
  return (
    <main className="flex min-h-screen flex-col items-center p-6 bg-black text-white">
      <div className="w-full max-w-[1200px] mx-auto">
        <div className="mb-6 flex items-center">
          <Link href="/" className="flex items-center text-white hover:text-gray-300 mr-4">
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Dashboard
          </Link>
        </div>
        
        <header className="mb-8">
          <h1 className="text-3xl font-medium text-white">Load vs. LMBP</h1>
          <p className="text-gray-400">Compare electricity demand against price variations to identify patterns.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Correlation between Load and Price</h2>
          <div className="h-[500px] flex items-center justify-center bg-zinc-800/50 rounded-lg">
            <LoadVsPriceChart height="100%" />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            The relationship between load (demand) and price is a fundamental dynamic in electricity markets. 
            As demand increases, more expensive generation resources must be brought online, typically resulting in higher prices.
          </p>
          <p className="text-gray-400">
            This correlation can be affected by factors such as:
          </p>
          <ul className="list-disc pl-5 mt-2 text-gray-400 space-y-1">
            <li>Transmission constraints</li>
            <li>Generation outages</li>
            <li>Fuel price volatility</li>
            <li>Extreme weather events</li>
            <li>Renewable energy availability</li>
          </ul>
        </div>
      </div>
    </main>
  );
} 