from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LoadDataPoint(BaseModel):
    timestamp: str
    value: float

class PriceDataPoint(BaseModel):
    timestamp: str
    value: float

class WeatherData(BaseModel):
    temperature: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    timestamp: str

class EnergyMixItem(BaseModel):
    source: str
    percentage: float

class ResortEnergyData(BaseModel):
    resort_id: str
    resort_name: str
    region: str
    load_data: List[LoadDataPoint]
    losses: List[LoadDataPoint]
    lbmp_data: List[PriceDataPoint]
    energy_mix: List[EnergyMixItem]
    weather: WeatherData

class InterfaceFlow(BaseModel):
    from_region: str
    to_region: str
    power_flow: float  # MW
    scheduled_flow: float  # MW
    transfer_limit: Optional[float] = None  # MW
    timestamp: str

class DashboardResponse(BaseModel):
    resort_data: List[ResortEnergyData]
    interface_flows: List[InterfaceFlow]
    timestamp: str 