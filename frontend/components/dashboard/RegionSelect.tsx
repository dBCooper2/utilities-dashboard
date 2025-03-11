"use client";

import { useEffect, useState } from "react";
import { 
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue, 
} from "@/components/ui/select";

interface State {
  code: string;
  name: string;
}

interface RegionSelectProps {
  onRegionChange: (region: string) => void;
  theme: 'dark' | 'light';
}

// Default states data as fallback
const DEFAULT_STATES: State[] = [
  { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' },
  { code: 'NC', name: 'North Carolina' },
  { code: 'SC', name: 'South Carolina' },
  { code: 'TN', name: 'Tennessee' },
  { code: 'AL', name: 'Alabama' },
  { code: 'MS', name: 'Mississippi' },
];

const RegionSelect = ({ onRegionChange, theme }: RegionSelectProps) => {
  const [states, setStates] = useState<State[]>(DEFAULT_STATES);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch the list of states from the backend
  useEffect(() => {
    const fetchStates = async () => {
      try {
        setIsLoading(true);
        
        // Try to fetch states from the API
        const response = await fetch('/api/energy/states');
        
        if (!response.ok) {
          throw new Error(`API returned status: ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('API response:', responseData);
        
        // The API returns { states: string[] } where each string is a state code
        // We need to convert this to an array of { code, name } objects
        if (responseData && responseData.states && Array.isArray(responseData.states)) {
          const stateCodesArray = responseData.states;
          
          // Map state codes to state objects with names
          const statesWithNames = stateCodesArray.map((stateCode: string) => {
            // Find the state in our default list to get the name
            const knownState = DEFAULT_STATES.find(s => s.code === stateCode);
            return {
              code: stateCode,
              // Use the known name or generate a formatted name
              name: knownState?.name || formatStateName(stateCode)
            };
          });
          
          if (statesWithNames.length > 0) {
            setStates(statesWithNames);
          }
        } else {
          console.warn('API did not return expected states format, using defaults');
        }
      } catch (error) {
        console.error('Failed to fetch states:', error);
        // We already have default states set in the initial state
      } finally {
        setIsLoading(false);
      }
    };

    fetchStates();
  }, []);

  // Helper function to format state codes into readable names
  const formatStateName = (stateCode: string): string => {
    // Example conversion: "NC" -> "North Carolina"
    // This is just a basic implementation - for unknown codes, just return the code
    const stateNameMap: {[key: string]: string} = {
      'AL': 'Alabama',
      'FL': 'Florida',
      'GA': 'Georgia',
      'MS': 'Mississippi',
      'NC': 'North Carolina',
      'SC': 'South Carolina',
      'TN': 'Tennessee',
      // Add more mappings as needed
    };
    
    return stateNameMap[stateCode] || stateCode;
  };

  return (
    <div className="w-full max-w-xs">
      <Select 
        defaultValue="southeast" 
        onValueChange={onRegionChange}
        disabled={isLoading}
      >
        <SelectTrigger 
          className={`${
            theme === 'dark' 
              ? 'text-stone-300 border-stone-700 bg-stone-900/50' 
              : 'text-stone-700 border-stone-300 bg-stone-100/50'
          } w-full h-8 text-xs`}
        >
          <SelectValue placeholder="Select region" />
        </SelectTrigger>
        <SelectContent
          className={`${
            theme === 'dark' 
              ? 'bg-stone-900 border-stone-700 text-stone-300' 
              : 'bg-white border-stone-300 text-stone-700'
          }`}
        >
          <SelectGroup>
            <SelectLabel 
              className={theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}
            >
              Regions
            </SelectLabel>
            <SelectItem value="southeast">Entire Southeast</SelectItem>
            <SelectSeparator className={`bg-stone-700/50`} />
            <SelectLabel 
              className={theme === 'dark' ? 'text-stone-400' : 'text-stone-500'}
            >
              States
            </SelectLabel>
            {Array.isArray(states) && states.map((state) => (
              <SelectItem key={state.code} value={state.code}>
                {state.name}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
};

export default RegionSelect; 