from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserType(str, enum.Enum):
    OPERATION = "operation"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    login_history = relationship("UserLoginHistory", back_populates="user")
    files = relationship("File", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserLoginHistory(Base):
    __tablename__ = "user_login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(String)
    ip_address = Column(String)
    
    user = relationship("User", back_populates="login_history")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="files")
