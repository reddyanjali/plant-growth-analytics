import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy import create_engine, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid
from passlib.context import CryptContext

# JWT Settings
class Settings(BaseModel):
    authjwt_secret_key: str = "PROJ_SECRET_KEY"

@AuthJWT.load_config
def get_config():
    return Settings()

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@plants_db:5432/plants"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Exception handler for JWT errors
app = FastAPI()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# SensorData Model
class SensorData(Base):
    __tablename__ = "plant_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(String, index=True)
    plant_id = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    soil_moisture = Column(Float)
    light_level = Column(Float)
    plant_height = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

# OptimalConditions Model
class OptimalConditionsOut(BaseModel):
    temperature_range: str
    humidity_range: str
    soil_moisture_range: str

    class Config:
        orm_mode = True

# Pydantic models
class SensorDataCreate(BaseModel):
    zone_id: str
    plant_id: str
    temperature: float
    humidity: float
    soil_moisture: float
    light_level: float

    class Config:
        orm_mode = True

class SensorDataOut(SensorDataCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# Initialize database
Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Plant API!"}

# ---------------- User Endpoints ----------------
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Get the user from the database
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create a JWT token
    access_token = Authorize.create_access_token(subject=db_user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------- Sensor Data Endpoints ----------------
@app.post("/api/v1/sensor-data/batch", response_model=List[SensorDataOut])
def create_sensor_data_batch(sensor_data: List[SensorDataCreate], db: Session = Depends(get_db)):
    db_data = [SensorData(**data.dict()) for data in sensor_data]
    db.add_all(db_data)
    db.commit()
    for data in db_data:
        db.refresh(data)
    return db_data

@app.post("/api/v1/sensor-data/single", response_model=SensorDataOut)
def create_sensor_data_single(sensor_data: SensorDataCreate, db: Session = Depends(get_db)):
    db_sensor_data = SensorData(**sensor_data.dict())
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data

@app.get("/api/v1/sensor-data/{zone_id}", response_model=List[SensorDataOut])
def get_sensor_data_by_zone(zone_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(SensorData).filter(SensorData.zone_id == zone_id)).scalars().all()
    return result

@app.get("/api/v1/sensor-data/{zone_id}/{plant_id}", response_model=List[SensorDataOut])
def get_sensor_data_by_zone_and_plant(zone_id: str, plant_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(SensorData).filter(SensorData.zone_id == zone_id, SensorData.plant_id.contains(plant_id))).scalars().all()
    return result

# ---------------- Analytics Endpoints ----------------
@app.get("/api/v1/analytics/growth-rate/{plant_id}")
def get_growth_rate(plant_id: str, db: Session = Depends(get_db)):
    sensor_data = db.execute(select(SensorData).filter(SensorData.plant_id == plant_id)).scalars().all()
    
    growth_rates = []
    for i in range(1, len(sensor_data)):
        prev_data = sensor_data[i - 1]
        curr_data = sensor_data[i]
        
        # Assuming plant_height is being recorded
        if prev_data.plant_height is not None and curr_data.plant_height is not None:
            growth_rate = curr_data.plant_height - prev_data.plant_height
            growth_rates.append({"timestamp": curr_data.timestamp, "growth_rate": growth_rate})
    
    return {"growth_rates": growth_rates}

@app.get("/api/v1/analytics/optimal-conditions/{species_id}", response_model=OptimalConditionsOut)
def get_optimal_conditions(species_id: str, db: Session = Depends(get_db)):
    # Get all sensor data for this species
    sensor_data = db.query(SensorData).filter(SensorData.plant_id == species_id).all()

    if not sensor_data:
        raise HTTPException(status_code=404, detail="No sensor data found for this species")

    # Calculate optimal conditions based on the sensor data
    temperatures = [data.temperature for data in sensor_data]
    humidities = [data.humidity for data in sensor_data]
    soil_moistures = [data.soil_moisture for data in sensor_data]

    optimal_conditions = OptimalConditionsOut(
        temperature_range=f"{min(temperatures):.2f}-{max(temperatures):.2f}°C",
        humidity_range=f"{min(humidities):.2f}-{max(humidities):.2f}%",
        soil_moisture_range=f"{min(soil_moistures):.2f}-{max(soil_moistures):.2f}"
    )

    return optimal_conditions

@app.get("/api/v1/analytics/yield-prediction/{zone_id}")
def get_yield_prediction(zone_id: str, db: Session = Depends(get_db)):
    # Fetch sensor data for the specified zone
    zone_data = db.execute(select(SensorData).filter(SensorData.zone_id == zone_id)).scalars().all()

    if not zone_data:
        raise HTTPException(status_code=404, detail="No data found for the zone")

    # Calculate average temperature and humidity as placeholders for yield prediction
    avg_temperature = sum([data.temperature for data in zone_data if data.temperature is not None]) / len([data for data in zone_data if data.temperature is not None])
    avg_humidity = sum([data.humidity for data in zone_data if data.humidity is not None]) / len([data for data in zone_data if data.humidity is not None])

    # Prediction based on both temperature and humidity
    if avg_temperature < 15 and avg_humidity < 50:
        yield_prediction = 10  # Low temperature and low humidity
    elif 15 <= avg_temperature <= 25 and 50 <= avg_humidity <= 70:
        yield_prediction = 20  # Optimal range
    else:
        yield_prediction = 30  # High temperature or humidity, could indicate high yield potential

    return {
        "predicted_yield": yield_prediction,
        "zone": zone_id,
        "avg_temperature": avg_temperature,
        "avg_humidity": avg_humidity
    }
