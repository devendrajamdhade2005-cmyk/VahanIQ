"""
Invoice model for repair billing
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Invoice(Base):
    """Invoice model for repair cases"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    repair_case_id = Column(Integer, ForeignKey("repair_cases.id"), nullable=False, unique=True, index=True)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., INV-2024-001234
    invoice_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    labor_cost = Column(Float, nullable=False)
    parts_cost = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    tax_percentage = Column(Float, default=18.0, nullable=False)  # GST percentage
    discount_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Payment status
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(50), nullable=True)  # cash, card, upi, etc.
    transaction_id = Column(String(100), nullable=True)
    
    # Document
    pdf_url = Column(String(500), nullable=True)  # S3/storage URL for PDF invoice
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    repair_case = relationship("RepairCase", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, total={self.total_amount}, paid={self.is_paid})>"
