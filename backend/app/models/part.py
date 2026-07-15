"""
Parts inventory and usage tracking models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Part(Base):
    """Parts inventory model"""
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False, index=True)
    
    # Part details
    sku = Column(String(100), nullable=False, index=True)  # Stock Keeping Unit
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "Brakes", "Engine", "Electrical"
    
    # Pricing
    unit_price = Column(Float, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    
    # Inventory
    stock_quantity = Column(Integer, default=0, nullable=False)
    min_stock_threshold = Column(Integer, default=5, nullable=False)
    max_stock_capacity = Column(Integer, nullable=True)
    
    # Supplier info
    supplier_name = Column(String(255), nullable=True)
    supplier_part_number = Column(String(100), nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_restocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    showroom = relationship("Showroom", back_populates="parts")
    usage_records = relationship("PartUsage", back_populates="part")
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum threshold"""
        return self.stock_quantity <= self.min_stock_threshold
    
    def __repr__(self):
        return f"<Part(id={self.id}, sku={self.sku}, name={self.name}, stock={self.stock_quantity})>"


class PartUsage(Base):
    """Parts used in repair cases - tracks consumption"""
    __tablename__ = "parts_used"

    id = Column(Integer, primary_key=True, index=True)
    repair_case_id = Column(Integer, ForeignKey("repair_cases.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    
    # Usage details
    quantity = Column(Integer, nullable=False)
    unit_price_at_use = Column(Float, nullable=False)  # Price at time of use (for historical accuracy)
    total_cost = Column(Float, nullable=False)
    
    # Timestamps
    used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    repair_case = relationship("RepairCase", back_populates="parts_used")
    part = relationship("Part", back_populates="usage_records")
    
    def __repr__(self):
        return f"<PartUsage(repair_case_id={self.repair_case_id}, part_id={self.part_id}, qty={self.quantity})>"
