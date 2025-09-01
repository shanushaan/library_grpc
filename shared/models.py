from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="USER")
    
    # Library member fields
    full_name = Column(String(100), nullable=False)
    phone = Column(String(15))
    address = Column(String(255))
    membership_date = Column(Date, default=date.today)
    
    # System fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100))
    genre = Column(String(50))
    published_year = Column(Integer)
    available_copies = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)

# Member table removed - using single User table

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Changed from member_id to user_id
    book_id = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    return_date = Column(DateTime)
    status = Column(String(20), default="BORROWED")
    fine_amount = Column(Integer, default=0)

class BookRequest(Base):
    __tablename__ = "book_requests"
    
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, nullable=False)
    request_type = Column(String(20), nullable=False)
    status = Column(String(20), default="PENDING")
    request_date = Column(DateTime, default=datetime.utcnow)
    admin_response_date = Column(DateTime)
    admin_id = Column(Integer)
    notes = Column(Text)
    transaction_id = Column(Integer)