'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Code } from 'lucide-react';

const Navbar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: Home },
    { href: '/api-test', label: 'API Test', icon: Code },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-white font-medium text-xl">Energy Dashboard</span>
            </Link>
          </div>
          <div className="flex items-center">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`ml-4 px-3 py-2 rounded-md text-sm font-medium flex items-center transition-colors ${
                    isActive
                      ? 'bg-zinc-800 text-white'
                      : 'text-gray-300 hover:bg-zinc-900/80 hover:text-white'
                  }`}
                >
                  <Icon className="mr-2" size={18} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 