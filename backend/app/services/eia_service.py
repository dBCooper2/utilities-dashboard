import httpx
from datetime import datetime, timedelta
import random
from app.core.config import settings

class EIAService:
    def __init__(self):
        self.api_key = settings.EIA_API_KEY
        self.base_url = "https://api.eia.gov/v2"
    
    async def get_electricity_data(self, region_code):
        """Get electricity data from EIA API"""
        # For demo purposes, we'll generate mock data
        # In a real application, you'd make an actual API call
        
        # Generate 24 hours of historical data
        now = datetime.now()
        data_points = []
        losses = []
        
        for hour in range(24):
            timestamp = (now - timedelta(hours=24-hour)).isoformat()
            
            # Create a realistic load pattern that peaks in morning and evening
            hour_of_day = (now - timedelta(hours=24-hour)).hour
            
            # Base load varies by region size
            base_load = {
                "US_WEST": 30000,
                "US_EAST": 40000,
                "US_CENTRAL": 35000,
                "EU_ALPINE": 25000,
                "EU_NORDIC": 20000
            }.get(region_code, 25000)
            
            # Add time-of-day variation
            if 7 <= hour_of_day <= 10:  # Morning peak
                load_factor = random.uniform(1.1, 1.3)
            elif 17 <= hour_of_day <= 21:  # Evening peak
                load_factor = random.uniform(1.2, 1.4)
            elif 0 <= hour_of_day <= 5:  # Night low
                load_factor = random.uniform(0.7, 0.9)
            else:  # Mid-day
                load_factor = random.uniform(0.9, 1.1)
                
            # Add random variation
            load_factor *= random.uniform(0.95, 1.05)
            
            load = base_load * load_factor
            
            # Transmission losses are typically 2-6% of total load
            loss = load * random.uniform(0.02, 0.06)
            
            data_points.append({
                "timestamp": timestamp,
                "value": load
            })
            
            losses.append({
                "timestamp": timestamp,
                "value": loss
            })
            
        return {
            "total_load": data_points,
            "transmission_losses": losses
        }
    
    async def get_day_ahead_prices(self, region_code):
        """Get day-ahead prices from EIA API"""
        # For demo purposes, we'll generate mock data
        
        now = datetime.now()
        prices = []
        
        # Base prices vary by region
        base_price = {
            "US_WEST": 35,
            "US_EAST": 40,
            "US_CENTRAL": 32,
            "EU_ALPINE": 45,
            "EU_NORDIC": 38
        }.get(region_code, 35)
        
        for hour in range(24):
            timestamp = (now - timedelta(hours=24-hour)).isoformat()
            hour_of_day = (now - timedelta(hours=24-hour)).hour
            
            # Prices tend to follow load patterns but with more volatility
            if 7 <= hour_of_day <= 10:  # Morning peak
                price_factor = random.uniform(1.2, 1.5)
            elif 17 <= hour_of_day <= 21:  # Evening peak
                price_factor = random.uniform(1.3, 1.8)
            elif 0 <= hour_of_day <= 5:  # Night low
                price_factor = random.uniform(0.6, 0.8)
            else:  # Mid-day
                price_factor = random.uniform(0.9, 1.2)
                
            # Add random price spikes occasionally
            if random.random() < 0.1:
                price_factor *= random.uniform(1.2, 2.0)
                
            price = base_price * price_factor
            
            prices.append({
                "timestamp": timestamp,
                "value": price
            })
            
        return {
            "prices": prices
        }
    
    async def get_interface_flows(self):
        """Get power flows between regions"""
        # For demo purposes, we'll generate mock interface flows
        
        # Define region pairs
        region_pairs = [
            ("US_WEST", "US_CENTRAL"),
            ("US_CENTRAL", "US_EAST"),
            ("EU_ALPINE", "EU_CENTRAL"),
            ("EU_NORDIC", "EU_CENTRAL"),
            ("US_WEST", "CA_WEST")
        ]
        
        flows = []
        timestamp = datetime.now().isoformat()
        
        for from_region, to_region in region_pairs:
            # Randomize direction occasionally
            if random.random() < 0.3:
                from_region, to_region = to_region, from_region
                
            # Generate realistic flow values
            power_flow = random.uniform(500, 3000)
            scheduled_flow = power_flow * random.uniform(0.9, 1.1)
            transfer_limit = power_flow * random.uniform(1.2, 1.8)
            
            flows.append({
                "from_region": from_region,
                "to_region": to_region,
                "power_flow": power_flow,
                "scheduled_flow": scheduled_flow,
                "transfer_limit": transfer_limit,
                "timestamp": timestamp
            })
            
        return flows 