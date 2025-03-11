"use client";

import React, { useState, useEffect } from "react";
import { SunIcon, MoonIcon } from "@heroicons/react/24/outline";
import { panels } from "@/components/dashboard/panels";
import PanelStack from "@/components/dashboard/PanelStack";
import Link from "next/link";

export default function Dashboard() {
  // State for expanded panel and theme
  const [expandedPanel, setExpandedPanel] = useState<string | null>(null); // Start with no panel expanded
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isMobile, setIsMobile] = useState<boolean>(false);

  // Function to handle panel click - toggles the panel closed if clicked again
  const handlePanelClick = (panelId: string) => {
    setExpandedPanel(prevExpandedPanel => 
      prevExpandedPanel === panelId ? null : panelId
    );
  };

  // Toggle theme between light and dark
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  // Check if we're on mobile view
  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768); // 768px is the standard md breakpoint
    };
    
    // Initial check
    checkIfMobile();
    
    // Add resize listener
    window.addEventListener('resize', checkIfMobile);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkIfMobile);
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.classList.toggle('light', theme === 'light');
  }, [theme]);

  return (
    <div className={`min-h-dvh ${theme === 'dark' ? 'bg-black' : 'bg-white'} transition-colors duration-300`}>
      {/* Subtle background effects for dark mode only */}
      {theme === 'dark' && (
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -left-40 w-80 h-80 bg-stone-900/10 rounded-full blur-3xl"></div>
          <div className="absolute top-40 -right-40 w-80 h-80 bg-stone-800/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-40 left-1/3 w-80 h-80 bg-stone-900/10 rounded-full blur-3xl"></div>
        </div>
      )}

      {/* For mobile: everything in one scrollable container */}
      {isMobile ? (
        <div className="relative w-full px-4 py-4 overflow-y-auto">
          {/* Header */}
          <header className="mb-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-stone-100' : 'text-stone-900'}`}>
                  Next-Day-Market Dashboard
                </h1>
                <p className={`mt-1 ${theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}`}>
                  Real-time energy market visualization and analysis
                </p>
              </div>
              
              {/* Theme toggle button */}
              <button 
                onClick={toggleTheme}
                className={`p-2 rounded-full transition-colors ${
                  theme === 'dark' 
                    ? 'bg-stone-800 text-stone-400 hover:bg-stone-700 hover:text-stone-200' 
                    : 'bg-stone-200 text-stone-700 hover:bg-stone-300 hover:text-stone-900'
                }`}
                aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </header>

          {/* Main Dashboard for mobile - in the same scroll container */}
          <PanelStack 
            panels={panels}
            expandedPanel={expandedPanel}
            theme={theme}
            onPanelClick={handlePanelClick}
            isMobile={true}
          />
        </div>
      ) : (
        // For desktop: sticky header and separate scrollable content
        <>
          {/* Header for desktop */}
          <header className="relative px-4 pt-4 pb-2 flex justify-between items-center">
            <div>
              <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-stone-100' : 'text-stone-900'}`}>
                Next-Day-Market Dashboard
              </h1>
              <p className={`mt-1 ${theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}`}>
                Real-time energy market visualization and analysis
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <Link 
                href="/api-testing" 
                className={`text-sm ${theme === 'dark' ? 'text-stone-400' : 'text-stone-600'} hover:${theme === 'dark' ? 'text-stone-200' : 'text-stone-900'} transition-colors`}
              >
                API Testing
              </Link>
              
              {/* Theme toggle button */}
              <button 
                onClick={toggleTheme}
                className={`p-2 rounded-full transition-colors ${
                  theme === 'dark' 
                    ? 'bg-stone-800 text-stone-400 hover:bg-stone-700 hover:text-stone-200' 
                    : 'bg-stone-200 text-stone-700 hover:bg-stone-300 hover:text-stone-900'
                }`}
                aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </header>

          {/* Main Dashboard for desktop */}
          <main className="relative w-full px-2 sm:px-3 pb-2">
            <PanelStack 
              panels={panels}
              expandedPanel={expandedPanel}
              theme={theme}
              onPanelClick={handlePanelClick}
              isMobile={false}
            />
          </main>
        </>
      )}
    </div>
  );
}
