'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import ZonalDataChart from '../../../components/charts/ZonalDataChart';

export default function ZonalDataPage() {
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
          <h1 className="text-3xl font-medium text-white">Zonal Data</h1>
          <p className="text-gray-400">Explore detailed data for specific energy zones in the southeastern US.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Zonal Metrics and Comparison</h2>
          <div className="h-[500px] flex items-center justify-center bg-zinc-800/50 rounded-lg">
            <ZonalDataChart height="100%" />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            Zonal data analysis provides insights into regional differences within the electricity grid, 
            highlighting variations in generation mix, load patterns, and price characteristics.
          </p>
          <p className="text-gray-400">
            Key zonal characteristics typically include:
          </p>
          <ul className="list-disc pl-5 mt-2 text-gray-400 space-y-1">
            <li>Dominant generation types in each zone</li>
            <li>Peak demand periods and magnitudes</li>
            <li>Transmission constraints affecting zonal prices</li>
            <li>Import/export relationships with neighboring zones</li>
            <li>Seasonal variations in zonal characteristics</li>
          </ul>
        </div>
      </div>
    </main>
  );
} 