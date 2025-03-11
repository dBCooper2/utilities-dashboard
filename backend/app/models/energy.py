from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, PrimaryKeyConstraint, text
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Zone(Base):
    """Electric Zone model with geographical information"""
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    state = Column(String)
    iso_rto = Column(String)  # SERC, FRCC, PJM, MISO, SPP
    geojson = Column(JSON)  # GeoJSON data for the zone
    
    # Relationships
    lbmp_data = relationship("LBMP", back_populates="zone")
    load_data = relationship("Load", back_populates="zone")
    # Add relationships to ZoneInterface
    outgoing_interfaces = relationship("ZoneInterface", foreign_keys="ZoneInterface.from_zone_id", back_populates="from_zone")
    incoming_interfaces = relationship("ZoneInterface", foreign_keys="ZoneInterface.to_zone_id", back_populates="to_zone")
    
    def __repr__(self):
        return f"<Zone {self.code}: {self.name}>"

class LBMP(Base):
    """Locational Based Marginal Price data"""
    __tablename__ = "lbmp"
    
    id = Column(Integer, autoincrement=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    timestamp = Column(DateTime, index=True)
    type = Column(String)  # DA (Day Ahead) or RT (Real Time)
    price = Column(Float)  # $/MWh
    congestion = Column(Float)  # $/MWh
    losses = Column(Float)  # $/MWh
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    # Relationships
    zone = relationship("Zone", back_populates="lbmp_data")
    
    def __repr__(self):
        return f"<LBMP {self.zone.code} {self.type} @ {self.timestamp}: ${self.price}>"

class Load(Base):
    """Load data"""
    __tablename__ = "load"
    
    id = Column(Integer, autoincrement=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    timestamp = Column(DateTime, index=True)
    type = Column(String)  # D (Demand), F (Forecast), etc.
    value = Column(Float)  # MW
    with_losses = Column(Float)  # MW
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    # Relationships
    zone = relationship("Zone", back_populates="load_data")
    
    def __repr__(self):
        return f"<Load {self.zone.code} {self.type} @ {self.timestamp}: {self.value} MW>"

class FuelMix(Base):
    """Fuel mix data"""
    __tablename__ = "fuel_mix"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, server_default=text("nextval('fuel_mix_id_seq')"))
    iso_rto = Column(String, index=True)  # SERC, FRCC, PJM, MISO, SPP
    state = Column(String, index=True, nullable=True)  # Optional state filter
    timestamp = Column(DateTime, index=True)
    fuel_type = Column(String)  # COL (Coal), NG (Natural Gas), NUC (Nuclear), etc.
    generation = Column(Float)  # MW
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<FuelMix {self.iso_rto} {self.fuel_type} @ {self.timestamp}: {self.generation} MW>"

class InterfaceFlow(Base):
    """Interface flow data between regions"""
    __tablename__ = "interface_flow"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, server_default=text("nextval('interface_flow_id_seq')"))
    timestamp = Column(DateTime, index=True)
    from_iso_rto = Column(String, index=True)
    to_iso_rto = Column(String, index=True)
    value = Column(Float)  # MW
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<InterfaceFlow {self.from_iso_rto} -> {self.to_iso_rto} @ {self.timestamp}: {self.value} MW>"

class ZoneInterface(Base):
    """Mapping between zones and interfaces"""
    __tablename__ = "zone_interfaces"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)  # Name of the interface (e.g., "PJM-NYISO")
    from_zone_id = Column(Integer, ForeignKey("zones.id"), index=True)
    to_zone_id = Column(Integer, ForeignKey("zones.id"), index=True)
    capacity = Column(Float, nullable=True)  # Maximum capacity in MW
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    
    # Relationships
    from_zone = relationship("Zone", foreign_keys=[from_zone_id], back_populates="outgoing_interfaces")
    to_zone = relationship("Zone", foreign_keys=[to_zone_id], back_populates="incoming_interfaces")
    flow_data = relationship("ZoneInterfaceFlow", back_populates="interface")
    
    def __repr__(self):
        return f"<ZoneInterface {self.name}: {self.from_zone.code} -> {self.to_zone.code}>"

class ZoneInterfaceFlow(Base):
    """Flow data for zone-to-zone interfaces"""
    __tablename__ = "zone_interface_flow"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interface_id = Column(Integer, ForeignKey("zone_interfaces.id"), index=True)
    timestamp = Column(DateTime, index=True)
    value = Column(Float)  # MW
    congestion = Column(Float, nullable=True)  # $/MWh
    
    # Define a composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'timestamp'),
    )
    
    # Relationships
    interface = relationship("ZoneInterface", back_populates="flow_data")
    
    def __repr__(self):
        return f"<ZoneInterfaceFlow {self.interface.name} @ {self.timestamp}: {self.value} MW>" 