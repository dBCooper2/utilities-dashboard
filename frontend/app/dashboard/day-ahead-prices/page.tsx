'use client';

import React from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import PriceChart from '../../../components/charts/PriceChart';

export default function DayAheadPricesPage() {
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
          <h1 className="text-3xl font-medium text-white">Day-Ahead Market Zonal LMBP</h1>
          <p className="text-gray-400">View locational marginal prices across different zones for day-ahead market planning.</p>
        </header>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">Locational Marginal Pricing by Zone</h2>
          <div className="h-[500px]">
            <PriceChart />
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-medium mb-4">Additional Information</h2>
          <p className="text-gray-400 mb-4">
            Day-ahead markets enable participants to secure electricity prices up to a day before delivery, 
            reducing price volatility and uncertainty.
          </p>
          <p className="text-gray-400">
            LMPs (Locational Marginal Prices) reflect the value of electricity at different locations, 
            accounting for generation costs, transmission constraints, and losses.
          </p>
        </div>
      </div>
    </main>
  );
} 