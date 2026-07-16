"""
Initialize database tables
"""

import asyncio
from app.core.database import engine, Base
from app.models import *  # Import all models


async def init_db():
    """Create all database tables"""
    print("📊 Creating database tables...")
    
    async with engine.begin() as conn:
        # Drop all tables first (for clean start)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("💡 Next: Run 'python3 seed_data.py' to add test data")


if __name__ == "__main__":
    asyncio.run(init_db())
