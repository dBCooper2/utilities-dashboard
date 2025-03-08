'use client';

import React from 'react';
import DashboardPanels from '../components/DashboardPanels';

export default function Home() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center p-6 bg-black text-white">
      <div className="w-full max-w-[1800px] mx-auto my-2">
        <header className="mb-6 text-center">
          <h1 className="text-4xl font-medium text-white">Energy Analytics Dashboard</h1>
          <p className="text-gray-400">Interactive power grid monitoring and analysis tools</p>
        </header>
        
        <div className="w-full h-[500px] mt-6 mb-6 flex justify-center">
          <DashboardPanels />
        </div>
      </div>
    </main>
  );
}
