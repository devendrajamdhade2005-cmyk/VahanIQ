"""
Database initialization script
Run this to create all tables (for development only - use Alembic in production)
"""

import asyncio
from app.core.database import engine, Base
from app.models import *  # Import all models


async def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    asyncio.run(init_db())
