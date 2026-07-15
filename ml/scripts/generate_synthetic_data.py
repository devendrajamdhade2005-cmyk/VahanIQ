"""
Generate synthetic data for AutoSense AI Platform

Creates realistic:
- Vehicles (Tata models)
- Sensor readings with physical decay patterns
- Failure scenarios
- Owners
"""

import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.core.database import async_session_maker
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.showroom import Showroom
from backend.app.models.vehicle import Vehicle, VehicleStatus
from backend.app.models.sensor import SensorReading

fake = Faker('en_IN')  # Indian locale

# Tata Motors vehicle models
TATA_MODELS = [
    {"make": "Tata", "model": "Nexon", "variants": ["XE", "XM", "XZ", "XZ+", "XZ+ (O)"]},
    {"make": "Tata", "model": "Harrier", "variants": ["XE", "XM", "XMA", "XT", "XZ", "XZ+"]},
    {"make": "Tata", "model": "Safari", "variants": ["XE", "XM", "XT", "XT+", "XZ", "XZ+"]},
    {"make": "Tata", "model": "Punch", "variants": ["Pure", "Adventure", "Accomplished", "Creative"]},
    {"make": "Tata", "model": "Altroz", "variants": ["XE", "XM", "XM+", "XT", "XZ", "XZ (O)"]},
    {"make": "Tata", "model": "Tiago", "variants": ["XE", "XM", "XT", "XZ", "XZ+"]},
    {"make": "Tata", "model": "Tigor", "variants": ["XE", "XM", "XT", "XZ", "XZ+"]},
]

COLORS = ["Pearl White", "Flame Red", "Royale Blue", "Daytona Grey", "Foliage Green", "Midnight Plum", "Arizona Blue"]

# DTC codes for various issues
DTC_CODES = {
    "engine": ["P0300", "P0301", "P0302", "P0171", "P0172", "P0401", "P0420"],
    "transmission": ["P0700", "P0715", "P0720", "P0730"],
    "brake": ["C0035", "C0040", "C0045", "C0050"],
    "electrical": ["B0001", "B0002", "U0001", "U0100"],
    "fuel": ["P0171", "P0172", "P0420", "P0442"],
}


class DataGenerator:
    """Generate realistic synthetic data"""
    
    def __init__(self):
        self.owners = []
        self.vehicles = []
        self.showrooms = []
    
    async def generate_all(self, num_vehicles=50):
        """Generate complete dataset"""
        async with async_session_maker() as db:
            print("🌱 Generating synthetic data...")
            
            # Get existing showrooms
            from sqlalchemy import select
            result = await db.execute(select(Showroom))
            self.showrooms = list(result.scalars().all())
            
            if not self.showrooms:
                print("❌ No showrooms found. Run seed_data.py first!")
                return
            
            print(f"✅ Found {len(self.showrooms)} showrooms")
            
            # Generate owners
            print(f"👥 Generating {num_vehicles} vehicle owners...")
            await self._generate_owners(db, num_vehicles)
            
            # Generate vehicles
            print(f"🚗 Generating {num_vehicles} vehicles...")
            await self._generate_vehicles(db, num_vehicles)
            
            # Generate sensor readings
            print(f"📊 Generating sensor readings...")
            await self._generate_sensor_readings(db)
            
            print("\n✨ Synthetic data generation complete!")
            print(f"   Created: {len(self.owners)} owners")
            print(f"   Created: {len(self.vehicles)} vehicles")
            print(f"   Created: ~{len(self.vehicles) * 100} sensor readings")
    
    async def _generate_owners(self, db, count):
        """Generate vehicle owners"""
        for i in range(count):
            owner = User(
                email=fake.email(),
                hashed_password=get_password_hash("owner123"),
                full_name=fake.name(),
                phone=fake.phone_number(),
                role=UserRole.OWNER,
                is_active=True,
                is_verified=True
            )
            db.add(owner)
            self.owners.append(owner)
        
        await db.commit()
        
        # Refresh to get IDs
        for owner in self.owners:
            await db.refresh(owner)
    
    async def _generate_vehicles(self, db, count):
        """Generate vehicles with realistic data"""
        for i in range(count):
            model_info = random.choice(TATA_MODELS)
            year = random.randint(2018, 2024)
            
            # Generate registration number (Indian format)
            state_codes = ["MH", "DL", "KA", "TN", "UP"]
            reg_num = f"{random.choice(state_codes)}{random.randint(1, 99):02d}{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{random.randint(1000, 9999)}"
            
            # Assign to showroom
            showroom = random.choice(self.showrooms)
            
            # Owner
            owner = self.owners[i]
            
            # Mileage based on year
            current_year = 2024
            age = current_year - year
            base_mileage = age * random.randint(8000, 15000)  # 8k-15k km per year
            mileage = base_mileage + random.randint(0, 5000)
            
            # Health status based on mileage and age
            health_status = self._calculate_health_status(mileage, age)
            health_score = self._calculate_health_score(mileage, age)
            
            vehicle = Vehicle(
                registration_number=reg_num,
                vin=self._generate_vin(),
                make=model_info["make"],
                model=model_info["model"],
                year=year,
                variant=random.choice(model_info["variants"]),
                color=random.choice(COLORS),
                owner_id=owner.id,
                home_showroom_id=showroom.id,
                current_mileage=mileage,
                health_status=health_status,
                health_score=health_score,
                last_service_date=fake.date_time_between(start_date="-6m", end_date="now"),
                next_service_due=fake.date_time_between(start_date="now", end_date="+3m")
            )
            
            db.add(vehicle)
            self.vehicles.append(vehicle)
        
        await db.commit()
        
        # Refresh to get IDs
        for vehicle in self.vehicles:
            await db.refresh(vehicle)
    
    async def _generate_sensor_readings(self, db):
        """Generate sensor readings with realistic patterns"""
        
        for vehicle in self.vehicles:
            # Generate readings for last 30 days
            num_readings = random.randint(50, 150)
            
            # Calculate wear patterns based on mileage
            age_years = 2024 - vehicle.year
            brake_wear_factor = vehicle.current_mileage / 50000  # Brakes wear over 50k km
            
            for i in range(num_readings):
                # Timestamp - distributed over last 30 days
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
                
                # Base readings (normal operation)
                reading = self._generate_normal_reading(vehicle, timestamp)
                
                # Add wear patterns
                reading = self._apply_wear_patterns(reading, vehicle, brake_wear_factor)
                
                # Occasionally add faults
                if random.random() < 0.1:  # 10% chance of fault indicators
                    reading = self._add_fault_indicators(reading, vehicle)
                
                sensor_reading = SensorReading(
                    vehicle_id=vehicle.id,
                    timestamp=timestamp,
                    **reading
                )
                
                db.add(sensor_reading)
            
            # Commit in batches
            if self.vehicles.index(vehicle) % 10 == 0:
                await db.commit()
                print(f"   Processed {self.vehicles.index(vehicle) + 1}/{len(self.vehicles)} vehicles...")
        
        await db.commit()
    
    def _generate_normal_reading(self, vehicle, timestamp):
        """Generate normal sensor reading"""
        # Simulate driving patterns
        is_driving = random.random() < 0.7  # 70% chance vehicle is being driven
        
        if is_driving:
            return {
                "rpm": random.uniform(1000, 4000),
                "speed": random.uniform(20, 100),
                "engine_load": random.uniform(20, 70),
                "coolant_temp": random.uniform(85, 95),
                "intake_temp": random.uniform(25, 45),
                "throttle_position": random.uniform(10, 60),
                "maf": random.uniform(5, 25),
                "fuel_pressure": random.uniform(250, 350),
                "fuel_level": random.uniform(20, 90),
                "fuel_trim_short": random.uniform(-5, 5),
                "fuel_trim_long": random.uniform(-5, 5),
                "o2_voltage": random.uniform(0.1, 0.9),
                "brake_fluid_pressure": random.uniform(0, 50),
                "brake_pad_thickness_fl": max(2, 12 - (vehicle.current_mileage / 10000)),
                "brake_pad_thickness_fr": max(2, 12 - (vehicle.current_mileage / 10000)),
                "brake_pad_thickness_rl": max(2, 12 - (vehicle.current_mileage / 10000) * 0.8),
                "brake_pad_thickness_rr": max(2, 12 - (vehicle.current_mileage / 10000) * 0.8),
                "transmission_temp": random.uniform(70, 90),
                "gear_position": random.randint(1, 5),
                "battery_voltage": random.uniform(13.5, 14.5),
                "mileage": vehicle.current_mileage + random.uniform(0, 50)
            }
        else:
            # Idling
            return {
                "rpm": random.uniform(700, 900),
                "speed": 0,
                "engine_load": random.uniform(5, 15),
                "coolant_temp": random.uniform(85, 92),
                "intake_temp": random.uniform(25, 35),
                "throttle_position": 0,
                "maf": random.uniform(2, 5),
                "fuel_pressure": random.uniform(250, 300),
                "fuel_level": random.uniform(20, 90),
                "battery_voltage": random.uniform(13.0, 14.0),
                "mileage": vehicle.current_mileage
            }
    
    def _apply_wear_patterns(self, reading, vehicle, brake_wear_factor):
        """Apply realistic wear patterns"""
        # Brake pad wear (more worn = thinner)
        if "brake_pad_thickness_fl" in reading:
            reading["brake_pad_thickness_fl"] = max(1.5, reading["brake_pad_thickness_fl"] - brake_wear_factor * 2)
            reading["brake_pad_thickness_fr"] = max(1.5, reading["brake_pad_thickness_fr"] - brake_wear_factor * 2)
            reading["brake_pad_thickness_rl"] = max(1.5, reading["brake_pad_thickness_rl"] - brake_wear_factor * 1.5)
            reading["brake_pad_thickness_rr"] = max(1.5, reading["brake_pad_thickness_rr"] - brake_wear_factor * 1.5)
        
        # Battery degradation
        if vehicle.current_mileage > 80000:
            reading["battery_voltage"] = max(12.0, reading.get("battery_voltage", 14.0) - random.uniform(0, 1))
        
        return reading
    
    def _add_fault_indicators(self, reading, vehicle):
        """Add fault indicators for testing"""
        fault_type = random.choice(["brake", "engine", "fuel", "electrical"])
        
        if fault_type == "brake":
            # Worn brake pads
            reading["brake_pad_thickness_fl"] = random.uniform(1.0, 2.5)
            reading["brake_pad_thickness_fr"] = random.uniform(1.0, 2.5)
            reading["dtc_codes"] = random.choice(DTC_CODES["brake"])
        
        elif fault_type == "engine":
            # Engine issues
            reading["coolant_temp"] = random.uniform(100, 110)  # Overheating
            reading["engine_load"] = random.uniform(75, 95)  # High load
            reading["dtc_codes"] = random.choice(DTC_CODES["engine"])
        
        elif fault_type == "fuel":
            # Fuel system issues
            reading["fuel_trim_short"] = random.uniform(10, 20)  # Out of range
            reading["fuel_trim_long"] = random.uniform(-15, -10)
            reading["dtc_codes"] = random.choice(DTC_CODES["fuel"])
        
        elif fault_type == "electrical":
            # Electrical issues
            reading["battery_voltage"] = random.uniform(11.5, 12.5)  # Low voltage
            reading["dtc_codes"] = random.choice(DTC_CODES["electrical"])
        
        return reading
    
    def _calculate_health_status(self, mileage, age):
        """Calculate vehicle health status"""
        if mileage < 30000 and age < 3:
            return VehicleStatus.HEALTHY
        elif mileage < 60000 and age < 5:
            return random.choice([VehicleStatus.HEALTHY, VehicleStatus.WATCH])
        elif mileage < 100000 and age < 7:
            return random.choice([VehicleStatus.WATCH, VehicleStatus.WARNING])
        else:
            return random.choice([VehicleStatus.WARNING, VehicleStatus.CRITICAL])
    
    def _calculate_health_score(self, mileage, age):
        """Calculate health score (0-100)"""
        base_score = 100
        
        # Deduct for mileage
        mileage_penalty = (mileage / 1000) * 0.05
        
        # Deduct for age
        age_penalty = age * 2
        
        score = base_score - mileage_penalty - age_penalty
        return max(50, min(100, score + random.uniform(-5, 5)))
    
    def _generate_vin(self):
        """Generate realistic VIN"""
        chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(17))


async def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic data for AutoSense AI")
    parser.add_argument("--vehicles", type=int, default=50, help="Number of vehicles to generate")
    args = parser.parse_args()
    
    generator = DataGenerator()
    await generator.generate_all(num_vehicles=args.vehicles)


if __name__ == "__main__":
    asyncio.run(main())
