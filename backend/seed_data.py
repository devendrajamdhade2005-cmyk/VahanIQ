"""
Seed initial data for development/testing
Creates admin user, sample showrooms, test users, and sample vehicles
"""

import asyncio
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.showroom import Showroom
from app.models.vehicle import Vehicle, VehicleStatus


async def seed_data():
    """Seed initial data"""
    async with async_session_maker() as db:
        print("🌱 Seeding initial data...")
        
        # Check if admin already exists
        result = await db.execute(
            select(User).where(User.role == UserRole.ADMIN).limit(1)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("⚠️  Admin user already exists. Skipping seed.")
            return
        
        # Create admin user
        admin = User(
            email="admin@autosense.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            phone="+91-9876543210",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        print("✅ Created admin user: admin@autosense.ai / admin123")
        
        # Create sample showrooms
        showroom1 = Showroom(
            name="Tata Motors Service Center - Mumbai Central",
            code="TMSC-MUM-001",
            address="123 Main Road, Fort",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            phone="+91-22-12345678",
            email="mumbai.central@tatamotors.com",
            region="West",
            manager_name="Rajesh Kumar",
            capacity=15,
            is_active=True
        )
        db.add(showroom1)
        
        showroom2 = Showroom(
            name="Tata Motors Service Center - Pune Baner",
            code="TMSC-PUN-001",
            address="456 Baner Road, Baner",
            city="Pune",
            state="Maharashtra",
            pincode="411045",
            phone="+91-20-23456789",
            email="pune.baner@tatamotors.com",
            region="West",
            manager_name="Priya Sharma",
            capacity=10,
            is_active=True
        )
        db.add(showroom2)
        
        await db.commit()
        await db.refresh(showroom1)
        await db.refresh(showroom2)
        print(f"✅ Created showroom: {showroom1.name}")
        print(f"✅ Created showroom: {showroom2.name}")
        
        # Create showroom manager for Mumbai
        manager1 = User(
            email="manager.mumbai@autosense.ai",
            hashed_password=get_password_hash("manager123"),
            full_name="Rajesh Kumar",
            phone="+91-9876543211",
            role=UserRole.SHOWROOM,
            showroom_id=showroom1.id,
            is_active=True,
            is_verified=True
        )
        db.add(manager1)
        print("✅ Created showroom manager: manager.mumbai@autosense.ai / manager123")
        
        # Create mechanic for Mumbai
        mechanic1 = User(
            email="mechanic.mumbai@autosense.ai",
            hashed_password=get_password_hash("mechanic123"),
            full_name="Amit Patel",
            phone="+91-9876543212",
            role=UserRole.MECHANIC,
            showroom_id=showroom1.id,
            is_active=True,
            is_verified=True
        )
        db.add(mechanic1)
        print("✅ Created mechanic: mechanic.mumbai@autosense.ai / mechanic123")
        
        # Create vehicle owner
        owner1 = User(
            email="owner@example.com",
            hashed_password=get_password_hash("owner123"),
            full_name="Suresh Gupta",
            phone="+91-9876543213",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True
        )
        db.add(owner1)
        print("✅ Created vehicle owner: owner@example.com / owner123")
        
        await db.commit()
        await db.refresh(owner1)
        
        # Create sample vehicles
        vehicle1 = Vehicle(
            registration_number="MH01AB1234",
            vin="MAT123456789ABCDE",
            make="Tata",
            model="Nexon",
            year=2022,
            variant="XZ+ Diesel",
            color="Flame Red",
            owner_id=owner1.id,
            home_showroom_id=showroom1.id,
            current_mileage=15000,
            health_status=VehicleStatus.HEALTHY,
            health_score=92.5,
            last_service_date=datetime.utcnow() - timedelta(days=30),
            next_service_due=datetime.utcnow() + timedelta(days=60)
        )
        db.add(vehicle1)
        
        vehicle2 = Vehicle(
            registration_number="MH02CD5678",
            vin="MAT987654321FGHIJ",
            make="Tata",
            model="Harrier",
            year=2021,
            variant="XZ Diesel",
            color="Royale Blue",
            owner_id=owner1.id,
            home_showroom_id=showroom1.id,
            current_mileage=42000,
            health_status=VehicleStatus.WATCH,
            health_score=78.3,
            last_service_date=datetime.utcnow() - timedelta(days=90),
            next_service_due=datetime.utcnow() + timedelta(days=30)
        )
        db.add(vehicle2)
        
        await db.commit()
        print("✅ Created 2 sample vehicles")
        
        print("\n✨ Seed data created successfully!")
        print("\n📋 Login credentials:")
        print("   Admin:            admin@autosense.ai / admin123")
        print("   Showroom Manager: manager.mumbai@autosense.ai / manager123")
        print("   Mechanic:         mechanic.mumbai@autosense.ai / mechanic123")
        print("   Vehicle Owner:    owner@example.com / owner123")
        print("\n🚗 Sample vehicles:")
        print(f"   Vehicle 1: {vehicle1.registration_number} - {vehicle1.make} {vehicle1.model}")
        print(f"   Vehicle 2: {vehicle2.registration_number} - {vehicle2.make} {vehicle2.model}")
        print("\n💡 Next step: Generate more test data with:")
        print("   python ../ml/scripts/generate_synthetic_data.py")


async def reset_data():
    """Reset all data (DANGEROUS - use with caution!)"""
    from app.core.database import engine, Base
    
    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != "RESET":
        print("❌ Reset cancelled.")
        return
    
    print("🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("📊 Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database reset complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        asyncio.run(reset_data())
        asyncio.run(seed_data())
    else:
        asyncio.run(seed_data())
