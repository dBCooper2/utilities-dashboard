'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import LoadChart from '../../../components/charts/LoadChart';

export default function LoadDataPage() {
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
          <h1 className="text-3xl font-medium text-white">Load with Losses</h1>
          <p className="text-gray-400">Track electricity load and transmission losses across the system.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Load and Transmission Losses Over Time</h2>
          <div className="h-[500px]">
            <LoadChart />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            Load represents the total electricity demand in the system at any given time, measured in megawatts (MW).
          </p>
          <p className="text-gray-400">
            Transmission losses occur as electricity travels through the grid's transmission and distribution systems, 
            typically accounting for about 5-10% of the total electricity generated.
          </p>
        </div>
      </div>
    </main>
  );
} 