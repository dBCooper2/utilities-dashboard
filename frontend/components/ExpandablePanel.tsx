'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IconType } from 'react-icons';

interface ExpandablePanelProps {
  title: string;
  description: string;
  icon: IconType;
  actionLabel: string;
  isExpandedByDefault?: boolean;
  isExpanded?: boolean;
  onExpand?: () => void;
  children?: React.ReactNode;
}

const ExpandablePanel: React.FC<ExpandablePanelProps> = ({
  title,
  description,
  icon: Icon,
  actionLabel,
  isExpandedByDefault = false,
  isExpanded: externalIsExpanded,
  onExpand,
  children,
}) => {
  const [internalIsExpanded, setInternalIsExpanded] = useState(isExpandedByDefault);
  
  // If isExpanded is provided externally, use that; otherwise use internal state
  const isExpanded = externalIsExpanded !== undefined ? externalIsExpanded : internalIsExpanded;

  // Handle panel expansion
  const handlePanelClick = () => {
    if (externalIsExpanded === undefined) {
      setInternalIsExpanded(!internalIsExpanded);
    }
    
    if (onExpand) {
      onExpand();
    }
  };

  // Random shape background using SVG
  const randomShape = (
    <div className="absolute inset-0 opacity-10 z-0 overflow-hidden">
      <svg width="100%" height="100%" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <path
          fill="currentColor"
          d="M42.8,-65.1C54.7,-54.7,63.1,-40.9,67.1,-26.2C71.1,-11.5,70.6,4,65.6,16.9C60.7,29.7,51.3,39.8,40.4,47.6C29.5,55.4,17.1,60.9,3.1,57.8C-10.8,54.7,-26.3,43.1,-38,30.2C-49.7,17.3,-57.6,3.2,-58.4,-12.1C-59.1,-27.4,-52.6,-43.9,-41.1,-54.5C-29.6,-65.1,-14.8,-69.8,0.4,-70.3C15.6,-70.9,31.0,-65.4,42.8,-65.1Z"
          transform="translate(100 100)"
        />
      </svg>
    </div>
  );

  return (
    <motion.div
      className={`energy-panel ${isExpanded ? 'energy-panel-expanded flex-1 max-w-[500px]' : 'w-20'} 
        h-[450px] transition-all duration-500 ease-in-out overflow-hidden flex relative`}
      onClick={handlePanelClick}
      whileHover={{ scale: 1.01 }}
      initial={false}
      layout
    >
      {/* Subtle glow effect on top and left borders */}
      <div
        className={`absolute inset-0 ${
          isExpanded ? 'opacity-30' : 'opacity-10'
        } pointer-events-none`}
        style={{
          background:
            'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0) 20%, rgba(255, 255, 255, 0) 80%, rgba(255, 255, 255, 0.05) 100%)',
        }}
      />

      {/* Random shape background */}
      <div className="absolute inset-0 z-0 opacity-10 overflow-hidden pointer-events-none">
        {randomShape}
      </div>

      {/* Vertical title when collapsed */}
      <AnimatePresence initial={false}>
        {!isExpanded && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center h-full">
              <p className="transform rotate-90 text-white whitespace-nowrap text-base font-medium tracking-wide">
                {title}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content when expanded */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            className="flex flex-col w-full h-full p-6 z-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <div className="mb-4 flex items-center gap-2">
              <Icon className="text-primary" size={20} />
              <h3 className="text-lg font-semibold text-white">{title}</h3>
            </div>
            
            <p className="text-muted-foreground text-sm mb-4">{description}</p>

            <div className="flex-1 overflow-hidden">{children}</div>

            <div className="mt-4">
              <button className="flex items-center gap-2 bg-secondary hover:bg-secondary/90 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                <Icon size={16} />
                {actionLabel}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ExpandablePanel; 