from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class File(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class UserType(str, Enum):
    OPERATION = "operation"
    CLIENT = "client"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    user_type: UserType

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[str] = None

class FileDownloadResponse(BaseModel):
    download_url: str
    file_name: str

class FileUploadResponse(BaseModel):
    file_path: str
    file_id: int
