from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    coins = Column(Integer, default=1000)
    
    inventory = relationship("Inventory", back_populates="user")
    sent_transactions = relationship("CoinTransaction", foreign_keys="[CoinTransaction.from_user_id]", back_populates="from_user")
    received_transactions = relationship("CoinTransaction", foreign_keys="[CoinTransaction.to_user_id]", back_populates="to_user")

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_transactions")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_transactions")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item = Column(String)
    quantity = Column(Integer, default=0)
    
    user = relationship("User", back_populates="inventory")