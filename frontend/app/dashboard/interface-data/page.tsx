'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import InterfaceFlowChart from '../../../components/charts/InterfaceFlowChart';

export default function InterfaceDataPage() {
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
          <h1 className="text-3xl font-medium text-white">Interface Data</h1>
          <p className="text-gray-400">Monitor energy flow between different zones and regions in the grid.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Interface Flow Between Zones</h2>
          <div className="h-[500px]">
            <InterfaceFlowChart />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            Interface flows represent the movement of electrical power between different regions or zones of the power grid, 
            measured in megawatts (MW).
          </p>
          <p className="text-gray-400">
            Monitoring these flows helps grid operators ensure system reliability, manage congestion, and identify 
            potential bottlenecks in the transmission system.
          </p>
        </div>
      </div>
    </main>
  );
} 