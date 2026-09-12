from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone, timedelta
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=nigeria_time)
    
def nigeria_time():
    return datetime.now(timezone(timedelta(hours=1)))

class TransactionType(enum.Enum):
    sale = "sale"
    expense = "expense"

class CreditStatus(enum.Enum):
    pending = "pending"
    settled = "settled"

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=nigeria_time)
    credits = relationship("CreditRecord", back_populates="customer")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=nigeria_time)

class CreditRecord(Base):
    __tablename__ = "credit_records"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount_owed = Column(Float, nullable=False)
    status = Column(Enum(CreditStatus), default=CreditStatus.pending)
    created_at = Column(DateTime, default=nigeria_time)
    customer = relationship("Customer", back_populates="credits")
    payments = relationship("CreditPayment", back_populates="credit_record")
    items = relationship("CreditItem", back_populates="credit_record")

class CreditPayment(Base):
    __tablename__ = "credit_payments"
    id = Column(Integer, primary_key=True, index=True)
    credit_record_id = Column(Integer, ForeignKey("credit_records.id"))
    amount_paid = Column(Float, nullable=False)
    date_paid = Column(DateTime, default=nigeria_time)
    credit_record = relationship("CreditRecord", back_populates="payments")

class CreditItem(Base):
    __tablename__ = "credit_items"
    id = Column(Integer, primary_key=True, index=True)
    credit_record_id = Column(Integer, ForeignKey("credit_records.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    date_added = Column(DateTime, default=nigeria_time)
    credit_record = relationship("CreditRecord", back_populates="items")