import httpx
from app.core.config import settings
from datetime import datetime

class MeteostatService:
    def __init__(self):
        self.api_key = settings.RAPID_API_KEY
        self.base_url = "https://meteostat.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
        }
    
    async def get_point_data(self, latitude, longitude):
        """Get current weather data for a specific location"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/point/hourly",
                headers=self.headers,
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "start": current_date,
                    "end": current_date,
                    "tz": "UTC"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Return the most recent data point or empty data if none available
            if data.get("data") and len(data["data"]) > 0:
                latest = data["data"][0]
                return {
                    "temperature": latest.get("temp"),
                    "precipitation": latest.get("prcp"),
                    "wind_speed": latest.get("wspd"),
                    "timestamp": latest.get("time")
                }
            return {
                "temperature": None,
                "precipitation": None,
                "wind_speed": None,
                "timestamp": datetime.now().isoformat()
            } 