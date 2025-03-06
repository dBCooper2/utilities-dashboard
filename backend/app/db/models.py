from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class SkiResort(Base):
    __tablename__ = "ski_resorts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    region = Column(String)
    country = Column(String)
    
    # Relationships
    weather_data = relationship("WeatherData", back_populates="resort")
    energy_data = relationship("EnergyData", back_populates="resort")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    resort_id = Column(Integer, ForeignKey("ski_resorts.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    
    # Relationships
    resort = relationship("SkiResort", back_populates="weather_data")

class EnergyData(Base):
    __tablename__ = "energy_data"
    
    id = Column(Integer, primary_key=True, index=True)
    resort_id = Column(Integer, ForeignKey("ski_resorts.id"))
    timestamp = Column(DateTime, index=True)
    total_load = Column(Float)
    transmission_losses = Column(Float)
    net_generation = Column(Float)
    lbmp_price = Column(Float)  # Locational Based Pricing Mechanism
    energy_mix = Column(JSON)  # Store energy mix as JSON
    
    # Relationships
    resort = relationship("SkiResort", back_populates="energy_data")

class InterfaceFlow(Base):
    __tablename__ = "interface_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    from_region = Column(String, index=True)
    to_region = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    power_flow = Column(Float)  # MW
    scheduled_flow = Column(Float)  # MW
    transfer_limit = Column(Float)  # MW 