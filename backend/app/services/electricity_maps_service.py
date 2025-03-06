import httpx
from app.core.config import settings

class ElectricityMapsService:
    def __init__(self):
        self.api_key = settings.ELECTRICITY_MAPS_API_KEY
        self.base_url = "https://api.electricitymap.org/v3"
        self.headers = {
            "auth-token": self.api_key
        }
    
    async def get_carbon_intensity(self, latitude, longitude):
        """Get carbon intensity for a specific location"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/carbon-intensity/latest",
                params={"lat": latitude, "lon": longitude},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json() 
        