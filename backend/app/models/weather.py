from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Region(Base):
    """Region model with geographical information"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    state = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    weather_points = relationship("WeatherPoint", back_populates="region")
    climate_normals = relationship("ClimateNormal", back_populates="region")
    
    def __repr__(self):
        return f"<Region {self.code}: {self.name}>"

class WeatherPoint(Base):
    """15-minute interval weather data"""
    __tablename__ = "weather_points"
    
    id = Column(Integer, autoincrement=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    snow = Column(Float)
    snow_depth = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    pressure = Column(Float)
    condition = Column(Integer)
    cloud_cover = Column(Integer)
    solar_radiation = Column(Float)
    is_forecast = Column(Boolean, default=False)
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    # Relationships
    region = relationship("Region", back_populates="weather_points")
    
    def __repr__(self):
        return f"<WeatherPoint {self.region.code} @ {self.timestamp}>"

class HourlyWeather(Base):
    """Hourly weather data"""
    __tablename__ = "hourly_weather"
    
    id = Column(Integer, autoincrement=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    snow = Column(Float)
    snow_depth = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    pressure = Column(Float)
    condition = Column(Integer)
    cloud_cover = Column(Integer)
    solar_radiation = Column(Float)
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<HourlyWeather {self.region_id} @ {self.timestamp}>"

class DailyWeather(Base):
    """Daily weather data"""
    __tablename__ = "daily_weather"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    date = Column(DateTime, index=True)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_avg = Column(Float)
    precipitation = Column(Float)
    snow = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    pressure = Column(Float)
    condition = Column(Integer)
    cloud_cover = Column(Integer)
    solar_radiation = Column(Float)
    
    def __repr__(self):
        return f"<DailyWeather {self.region_id} @ {self.date}>"

class MonthlyWeather(Base):
    """Monthly weather data"""
    __tablename__ = "monthly_weather"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    year = Column(Integer)
    month = Column(Integer)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_avg = Column(Float)
    precipitation = Column(Float)
    snow = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)
    pressure = Column(Float)
    condition = Column(Integer)
    cloud_cover = Column(Integer)
    solar_radiation = Column(Float)
    
    def __repr__(self):
        return f"<MonthlyWeather {self.region_id} @ {self.year}-{self.month}>"

class ClimateNormal(Base):
    """Climate normals data"""
    __tablename__ = "climate_normals"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    month = Column(Integer)
    day = Column(Integer)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_avg = Column(Float)
    precipitation = Column(Float)
    
    # Relationships
    region = relationship("Region", back_populates="climate_normals")
    
    def __repr__(self):
        return f"<ClimateNormal {self.region.code} @ {self.month}-{self.day}>"

class WeatherForecast(Base):
    """Weather forecast data"""
    __tablename__ = "weather_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    forecast_date = Column(DateTime)  # Date the forecast was made
    target_date = Column(DateTime, index=True)  # Date the forecast is for
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_avg = Column(Float)
    precipitation = Column(Float)
    condition = Column(Integer)
    
    def __repr__(self):
        return f"<WeatherForecast {self.region_id} @ {self.target_date} (made on {self.forecast_date})>" 