from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, unique=True, index=True, nullable=False)
    ip = Column(String)
    hostname = Column(String)
    vendor = Column(String)
    device_type = Column(String, default="Unknown")
    os_hint = Column(String)
    is_trusted = Column(Boolean, default=False)
    is_ignored = Column(Boolean, default=False)
    is_authorized = Column(Boolean, default=True)  # Para lista blanca/negra
    status = Column(String, default="Online", index=True) # Online, Offline, Warning, Critical
    alias = Column(String)
    notes = Column(Text)
    tags = Column(String)  # Comma-separated tags
    group_id = Column(Integer, ForeignKey("device_groups.id"))
    first_seen = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Network position for map
    map_x = Column(Float)
    map_y = Column(Float)

    alerts = relationship("Alert", back_populates="device")
    metrics = relationship("MetricHistory", back_populates="device")
    sensors = relationship("Sensor", back_populates="device")
    port_scans = relationship("PortScan", back_populates="device")

class DeviceGroup(Base):
    __tablename__ = "device_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    color = Column(String)  # For UI
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    level = Column(String, default="INFO", index=True)  # CRITICAL, WARNING, INFO, DEBUG
    condition = Column(String, index=True)  # DEVICE_OFFLINE, HIGH_LATENCY, etc.
    type = Column(String, index=True)  # Alias de condition (compatibilidad)
    message = Column(Text)
    device_name = Column(String)  # Cache del nombre
    device_ip = Column(String)  # Cache de la IP
    alert_metadata = Column(JSON)  # Datos adicionales
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)

    device = relationship("Device", back_populates="alerts")

class MetricHistory(Base):
    __tablename__ = "metrics_history"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), index=True)
    metric_name = Column(String, index=True)  # ping_latency, bandwidth_in, cpu_usage, etc.
    value = Column(Float)
    unit = Column(String)  # ms, Mbps, %, etc.
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    device = relationship("Device", back_populates="metrics")
    sensor = relationship("Sensor", back_populates="metrics")

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)  # PING, PORT, SNMP, HTTP, BANDWIDTH
    config = Column(JSON)  # Configuración específica del sensor
    interval = Column(Integer, default=60)  # Segundos entre mediciones
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_run = Column(DateTime)
    status = Column(String, default="OK")  # OK, WARNING, ERROR
    
    device = relationship("Device", back_populates="sensors")
    metrics = relationship("MetricHistory", back_populates="sensor")

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))  # NULL = global rule
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    condition = Column(String, index=True)  # DEVICE_OFFLINE, HIGH_LATENCY, etc.
    level = Column(String, default="WARNING")  # CRITICAL, WARNING, INFO, DEBUG
    channels = Column(JSON)  # ["in_app", "email", "telegram", "webhook"]
    threshold = Column(Float)  # Valor umbral para condiciones numéricas
    throttle_minutes = Column(Integer, default=5)  # Anti-spam
    escalate_after_minutes = Column(Integer)  # Escalar si no se atiende
    last_triggered = Column(DateTime)  # Última vez que se disparó
    # Campos legacy (compatibilidad)
    metric_name = Column(String)
    threshold_value = Column(Float)
    threshold_operator = Column(String)  # >, <, ==, !=
    aggregation = Column(String)  # AVG, MAX, MIN, SUM
    time_window = Column(Integer)  # Minutos
    alert_level = Column(String, default="WARNING")
    notification_channels = Column(JSON)  # [" email", "telegram", "webhook"]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PortScan(Base):
    __tablename__ = "port_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    port = Column(Integer)
    protocol = Column(String)  # TCP/UDP
    state = Column(String)  # open, closed, filtered
    service = Column(String)  # http, ssh, ftp, etc.
    version = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    device = relationship("Device", back_populates="port_scans")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    report_type = Column(String)  # UPTIME, BANDWIDTH, SECURITY, CUSTOM
    format = Column(String)  # PDF, HTML, CSV
    schedule = Column(String)  # DAILY, WEEKLY, MONTHLY
    config = Column(JSON)  # Configuración del reporte
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="VIEWER")  # ADMIN, OPERATOR, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)

class Config(Base):
    __tablename__ = "config"
    
    key = Column(String, primary_key=True)
    value = Column(Text)
    category = Column(String)  # GENERAL, NOTIFICATIONS, SECURITY, etc.
    description = Column(Text)

from sqlalchemy import event

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./network_monitor.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Enable WAL mode for better concurrency
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
