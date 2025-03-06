import httpx
import random
from app.core.config import settings
from datetime import datetime

class SkiResortService:
    def __init__(self):
        self.api_key = settings.RAPID_API_KEY
        self.base_url = "https://ski-resort-forecast.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "ski-resort-forecast.p.rapidapi.com"
        }
    
    async def get_resort_locations(self):
        """Get list of ski resorts and their locations"""
        # For testing without the actual API, return mock data
        # In a real implementation, you would make the API call
        
        mock_resorts = [
            {
                "id": "vail",
                "name": "Vail: 39.6403: -106.3742",
                "latitude": 39.6403,
                "longitude": -106.3742,
                "country": "US"
            },
            {
                "id": "aspen",
                "name": "Aspen: 39.1911: -106.8175",
                "latitude": 39.1911,
                "longitude": -106.8175,
                "country": "US"
            },
            {
                "id": "park-city",
                "name": "Park City: 40.6461: -111.4980",
                "latitude": 40.6461,
                "longitude": -111.4980,
                "country": "US"
            },
            {
                "id": "whistler",
                "name": "Whistler: 50.1163: -122.9574",
                "latitude": 50.1163,
                "longitude": -122.9574,
                "country": "CA"
            },
            {
                "id": "chamonix",
                "name": "Chamonix: 45.9237: 6.8694",
                "latitude": 45.9237,
                "longitude": 6.8694,
                "country": "FR"
            },
            {
                "id": "zermatt",
                "name": "Zermatt: 46.0207: 7.7491",
                "latitude": 46.0207,
                "longitude": 7.7491,
                "country": "CH"
            },
            {
                "id": "st-anton",
                "name": "St. Anton: 47.1297: 10.2648",
                "latitude": 47.1297,
                "longitude": 10.2648,
                "country": "AT"
            },
            {
                "id": "cortina",
                "name": "Cortina d'Ampezzo: 46.5404: 12.1366",
                "latitude": 46.5404,
                "longitude": 12.1366,
                "country": "IT"
            },
            {
                "id": "are",
                "name": "Åre: 63.3979: 13.0801",
                "latitude": 63.3979,
                "longitude": 13.0801,
                "country": "SE"
            },
            {
                "id": "trysil",
                "name": "Trysil: 61.3145: 12.2738",
                "latitude": 61.3145,
                "longitude": 12.2738,
                "country": "NO"
            }
        ]
        
        # For testing - if API key is provided, actually call the API
        if self.api_key and self.api_key not in ["your-rapid-api-key", ""]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/resorts",
                        headers=self.headers
                    )
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"Error calling Ski Resort API: {e}")
                # Fall back to mock data
        
        return mock_resorts
    
    async def get_resort_forecast(self, resort_id):
        """Get weather forecast for a specific resort"""
        # Mock forecast data for testing
        return {
            "resort_id": resort_id,
            "forecast": {
                "periods": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "temperature": random.uniform(-5, 10),
                        "snow": random.uniform(0, 20),
                        "wind": random.uniform(5, 30)
                    }
                ]
            }
        } 