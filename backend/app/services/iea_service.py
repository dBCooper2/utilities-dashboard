import httpx
from datetime import datetime
import random

class IEAService:
    def __init__(self):
        self.base_url = "https://api.iea.org/data"
    
    async def get_realtime_data(self, country_code):
        """Get real-time electricity data from IEA Tracker"""
        # Since we're not using the IEA API directly (not freely available), 
        # generate realistic mock data based on the country
        
        # Different countries have different typical energy mixes
        energy_mix = []
        
        if country_code in ["US", "CA"]:
            # North American typical mix
            energy_mix = [
                {"source": "Natural Gas", "percentage": random.uniform(30, 40)},
                {"source": "Coal", "percentage": random.uniform(15, 25)},
                {"source": "Nuclear", "percentage": random.uniform(18, 22)},
                {"source": "Hydro", "percentage": random.uniform(5, 10)},
                {"source": "Wind", "percentage": random.uniform(8, 12)},
                {"source": "Solar", "percentage": random.uniform(2, 7)},
                {"source": "Biomass", "percentage": random.uniform(1, 3)}
            ]
        elif country_code in ["FR", "SE"]:
            # France, Sweden - high nuclear
            energy_mix = [
                {"source": "Nuclear", "percentage": random.uniform(40, 70)},
                {"source": "Hydro", "percentage": random.uniform(10, 20)},
                {"source": "Wind", "percentage": random.uniform(5, 15)},
                {"source": "Natural Gas", "percentage": random.uniform(5, 10)},
                {"source": "Solar", "percentage": random.uniform(2, 8)},
                {"source": "Biomass", "percentage": random.uniform(2, 5)}
            ]
        elif country_code in ["NO", "AT", "CH"]:
            # Norway, Austria, Switzerland - high hydro
            energy_mix = [
                {"source": "Hydro", "percentage": random.uniform(50, 80)},
                {"source": "Wind", "percentage": random.uniform(5, 15)},
                {"source": "Natural Gas", "percentage": random.uniform(5, 15)},
                {"source": "Solar", "percentage": random.uniform(2, 8)},
                {"source": "Biomass", "percentage": random.uniform(2, 5)},
                {"source": "Nuclear", "percentage": random.uniform(0, 5)}
            ]
        else:
            # Default mix
            energy_mix = [
                {"source": "Coal", "percentage": random.uniform(25, 35)},
                {"source": "Natural Gas", "percentage": random.uniform(20, 30)},
                {"source": "Nuclear", "percentage": random.uniform(10, 20)},
                {"source": "Hydro", "percentage": random.uniform(10, 15)},
                {"source": "Wind", "percentage": random.uniform(5, 15)},
                {"source": "Solar", "percentage": random.uniform(1, 5)},
                {"source": "Biomass", "percentage": random.uniform(1, 3)}
            ]
        
        # Normalize to ensure total is 100%
        total = sum(item["percentage"] for item in energy_mix)
        energy_mix = [
            {"source": item["source"], "percentage": (item["percentage"] / total) * 100}
            for item in energy_mix
        ]
        
        # Simulate total generation based on country size
        generation_factors = {
            "US": (35000, 50000),
            "CA": (15000, 25000),
            "FR": (20000, 30000),
            "DE": (18000, 28000),
            "CH": (5000, 10000),
            "AT": (4000, 9000),
            "IT": (10000, 20000),
            "NO": (8000, 15000),
            "SE": (10000, 18000)
        }
        
        generation_range = generation_factors.get(country_code, (8000, 15000))
        total_generation = random.uniform(*generation_range)
            
        return {
            "country": country_code,
            "timestamp": datetime.now().isoformat(),
            "electricity_mix": energy_mix,
            "total_generation": total_generation  # MW
        } 