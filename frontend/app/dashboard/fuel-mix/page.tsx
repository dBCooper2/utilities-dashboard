'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import FuelMixChart from '../../../components/charts/FuelMixChart';

export default function FuelMixPage() {
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
          <h1 className="text-3xl font-medium text-white">Fuel Mix Chart</h1>
          <p className="text-gray-400">Analyze the composition of energy generation sources across different regions.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Energy Generation by Fuel Type</h2>
          <div className="h-[500px]">
            <FuelMixChart />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            The fuel mix chart visualizes the proportion of different energy sources used for electricity generation, 
            including both renewable and non-renewable sources.
          </p>
          <p className="text-gray-400">
            A diverse fuel mix helps ensure energy security, price stability, and can contribute to reduced 
            environmental impacts depending on the proportion of low-carbon energy sources.
          </p>
        </div>
      </div>
    </main>
  );
} 