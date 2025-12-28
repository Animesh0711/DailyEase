from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

# Association table for many-to-many relationship between Subscription and Newspaper
subscription_newspapers = Table(
    'subscription_newspapers',
    Base.metadata,
    Column('subscription_id', Integer, ForeignKey('subscriptions.id'), primary_key=True),
    Column('newspaper_id', Integer, ForeignKey('newspapers.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    phone = Column(String)
    address = Column(Text)
    city = Column(String)
    pincode = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    deliveries = relationship("Delivery", back_populates="user")

class Newspaper(Base):
    __tablename__ = "newspapers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    language = Column(String)
    genre = Column(String)
    price_daily = Column(Float)
    price_weekly = Column(Float)
    price_monthly = Column(Float)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    subscriptions = relationship("Subscription", secondary=subscription_newspapers, back_populates="newspapers")
    magazines = relationship("Magazine", back_populates="newspaper")

class Magazine(Base):
    __tablename__ = "magazines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    language = Column(String)
    genre = Column(String)
    newspaper_id = Column(Integer, ForeignKey("newspapers.id"), nullable=True)
    is_complementary = Column(Boolean, default=False)
    price = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    
    newspaper = relationship("Newspaper", back_populates="magazines")

class MilkPackage(Base):
    __tablename__ = "milk_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quantity_ml = Column(Integer)
    price_daily = Column(Float)
    price_weekly = Column(Float)
    price_monthly = Column(Float)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    subscriptions = relationship("Subscription", back_populates="milk_package")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    milk_package_id = Column(Integer, ForeignKey("milk_packages.id"), nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    frequency = Column(String)
    is_paused = Column(Boolean, default=False)
    paused_from = Column(DateTime, nullable=True)
    paused_until = Column(DateTime, nullable=True)
    total_cost = Column(Float)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="subscriptions")
    newspapers = relationship("Newspaper", secondary=subscription_newspapers, back_populates="subscriptions")
    milk_package = relationship("MilkPackage", back_populates="subscriptions")
    deliveries = relationship("Delivery", back_populates="subscription")

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    scheduled_date = Column(DateTime)
    status = Column(String, default="pending")
    delivered_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="deliveries")
    subscription = relationship("Subscription", back_populates="deliveries")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    stripe_payment_id = Column(String, unique=True, nullable=True)
    payment_method = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="payments")
