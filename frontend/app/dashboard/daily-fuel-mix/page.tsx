'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import DailyFuelMixChart from '../../../components/charts/DailyFuelMixChart';

export default function DailyFuelMixPage() {
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
          <h1 className="text-3xl font-medium text-white">Daily Fuel Mix</h1>
          <p className="text-gray-400">View daily changes in energy generation sources and their proportions.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Fuel Mix Changes Over Time</h2>
          <div className="h-[500px] flex items-center justify-center bg-zinc-800/50 rounded-lg">
            <DailyFuelMixChart height="100%" />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            Daily fuel mix data shows how the contribution of different energy sources varies throughout the day, 
            reflecting changing demand patterns and the operational characteristics of different generation types.
          </p>
          <p className="text-gray-400">
            Common patterns include:
          </p>
          <ul className="list-disc pl-5 mt-2 text-gray-400 space-y-1">
            <li>Solar generation peaking during midday hours</li>
            <li>Natural gas units ramping up to meet evening peak demand</li>
            <li>Coal and nuclear providing baseload generation</li>
            <li>Wind generation often increasing during nighttime hours</li>
            <li>Hydro being dispatched strategically to address peak demand periods</li>
          </ul>
        </div>
      </div>
    </main>
  );
} 