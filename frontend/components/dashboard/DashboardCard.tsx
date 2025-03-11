import { FC } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PanelData } from './panels';
import FuelMixChart from './FuelMixChart';

interface DashboardCardProps {
  panel: PanelData;
  isExpanded: boolean;
  isHoverExpanded?: boolean;
  onClick: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  theme: 'dark' | 'light';
  isMobile: boolean;
  selectedRegion: string;
}

const DashboardCard: FC<DashboardCardProps> = ({ 
  panel, 
  isExpanded,
  isHoverExpanded = false,
  onClick, 
  onMouseEnter,
  onMouseLeave,
  theme,
  isMobile,
  selectedRegion
}) => {
  // Determine if card should show expanded content
  const shouldShowExpanded = isExpanded || isHoverExpanded;

  // Styles for the card based on expanded state, theme, and mobile/desktop view
  const getCardStyles = () => {
    // Common styles for all cards
    const baseStyles = `
      cursor-pointer rounded-lg
      relative border flex-shrink-0
      ${theme === 'dark' 
        ? 'bg-stone-950/70 border-stone-800 hover:border-stone-700' 
        : 'bg-stone-50 border-stone-200 hover:border-stone-300'}
      ${shouldShowExpanded 
        ? theme === 'dark' 
          ? 'shadow-[0_0_15px_rgba(40,40,40,0.1)] border-stone-700' 
          : 'shadow-sm border-stone-300' 
        : ''}
      transition-all duration-300 ease-in-out
    `;

    // Mobile specific styles
    if (isMobile) {
      return `
        ${baseStyles}
        ${shouldShowExpanded ? 'h-auto pb-4 mb-8' : 'h-[60px] mb-2'}
        w-full
      `;
    }
    
    // Desktop specific styles
    return `
      ${baseStyles}
      h-full
      ${shouldShowExpanded ? 'w-[450px]' : 'w-[80px]'}
    `;
  };

  // Render dashboard component based on panel ID
  const renderDashboardComponent = () => {
    switch (panel.id) {
      case "fuel-mix-chart":
        return <FuelMixChart region={selectedRegion} theme={theme} isMobile={isMobile} />;
      default:
        // Default placeholder for panels without a specific component
        return (
          <div className={`rounded-lg border p-4 ${isMobile ? 'h-[300px]' : 'h-[420px]'} flex items-center justify-center ${
            theme === 'dark' 
              ? 'border-stone-800 bg-stone-900/50' 
              : 'border-stone-200 bg-stone-100/50'
          }`}>
            <p className={`text-sm ${theme === 'dark' ? 'text-stone-500' : 'text-stone-400'}`}>
              {`${panel.title} visualization for ${selectedRegion === 'southeast' ? 'entire Southeast' : `state: ${selectedRegion}`}`}
            </p>
          </div>
        );
    }
  };

  return (
    <Card
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={getCardStyles()}
    >
      {/* Using a CSS transition for the content with opacity */}
      <div className={`transition-opacity duration-300 ease-in-out ${shouldShowExpanded ? 'opacity-100' : 'opacity-0 absolute pointer-events-none'}`}>
        {/* Expanded view */}
        <CardHeader className="pt-5 pb-2">
          <div className="flex items-center mb-1">
            <span className={`mr-2 ${theme === 'dark' ? 'text-stone-300' : 'text-stone-600'}`}>
              {panel.icon}
            </span>
            <CardTitle className={`text-lg font-medium ${
              theme === 'dark' ? 'text-stone-100' : 'text-stone-900'
            }`}>
              {panel.title}
            </CardTitle>
          </div>
          <CardDescription className={theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}>
            {panel.description}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="flex-grow">
          {/* Render appropriate component based on panel ID */}
          {renderDashboardComponent()}
        </CardContent>
        
        <CardFooter className="pt-2 pb-4">
          <Button 
            variant={theme === 'dark' ? 'outline' : 'secondary'} 
            className={`
              ${theme === 'dark' 
                ? 'border-stone-700 text-stone-300 hover:bg-stone-800 hover:text-stone-100' 
                : 'text-stone-700 hover:text-stone-900'
              } transition-all
            `}
          >
            View Details
          </Button>
        </CardFooter>
      </div>
      
      {/* Collapsed view with separate transition */}
      <div className={`transition-opacity duration-300 ease-in-out ${!shouldShowExpanded ? 'opacity-100' : 'opacity-0 absolute pointer-events-none'}`}>
        <div className={`flex ${isMobile ? 'h-full w-full flex-row' : 'h-full flex-col'} items-center justify-center`}>
          <div className={`${isMobile ? 'mr-3 ml-4' : 'mb-4'} ${theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}`}>
            {panel.icon}
          </div>
          <div className={`${isMobile ? '' : 'vertical-text'} text-xs tracking-wider font-medium ${
            theme === 'dark' ? 'text-stone-300' : 'text-stone-600'
          }`}>
            {isMobile ? panel.title : panel.title.toUpperCase()}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default DashboardCard; 