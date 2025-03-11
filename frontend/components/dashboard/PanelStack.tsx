import { FC, useState } from 'react';
import { PanelData } from './panels';
import DashboardCard from './DashboardCard';

interface PanelStackProps {
  panels: PanelData[];
  expandedPanel: string | null;
  theme: 'dark' | 'light';
  onPanelClick: (panelId: string) => void;
  isMobile: boolean;
  selectedRegion: string;
}

const PanelStack: FC<PanelStackProps> = ({ 
  panels, 
  expandedPanel, 
  theme, 
  onPanelClick,
  isMobile,
  selectedRegion
}) => {
  // State for tracking which panel is being hovered (desktop only)
  const [hoveredPanel, setHoveredPanel] = useState<string | null>(null);

  // Mouse handlers for desktop hover effect
  const handleMouseEnter = (panelId: string) => {
    if (!isMobile) {
      setHoveredPanel(panelId);
    }
  };

  const handleMouseLeave = () => {
    if (!isMobile) {
      setHoveredPanel(null);
    }
  };

  // For desktop view (horizontal layout)
  if (!isMobile) {
    return (
      <div className="flex overflow-x-auto justify-center hide-scrollbar gap-3 h-[82dvh]">
        <div className="flex gap-3 flex-nowrap">
          {panels.map((panel) => (
            <DashboardCard
              key={panel.id}
              panel={panel}
              isExpanded={expandedPanel === panel.id}
              isHoverExpanded={hoveredPanel === panel.id && expandedPanel !== panel.id}
              onClick={() => onPanelClick(panel.id)}
              onMouseEnter={() => handleMouseEnter(panel.id)}
              onMouseLeave={handleMouseLeave}
              theme={theme}
              isMobile={false}
              selectedRegion={selectedRegion}
            />
          ))}
        </div>
      </div>
    );
  }
  
  // For mobile view (vertical layout)
  return (
    <div className="flex flex-col gap-3 pb-4 overflow-y-auto h-[85dvh] hide-scrollbar">
      {panels.map((panel) => (
        <DashboardCard
          key={panel.id}
          panel={panel}
          isExpanded={expandedPanel === panel.id}
          isHoverExpanded={false} // No hover expansion on mobile
          onClick={() => onPanelClick(panel.id)}
          theme={theme}
          isMobile={true}
          selectedRegion={selectedRegion}
        />
      ))}
    </div>
  );
};

export default PanelStack; 