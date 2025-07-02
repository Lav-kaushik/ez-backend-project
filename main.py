from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Request
from fastapi import File as FastAPIFile  
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
from auth import create_access_token, create_refresh_token, get_current_active_user
from datetime import timedelta
import os
from dotenv import load_dotenv
from s3_utils import s3_service
from typing import List
import uuid
from schemas import Token, User, UserCreate, File as FileSchema, FileUploadResponse

# Create database tables
models.Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(title="File Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Dependency
def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# Auth routes
@app.post("/signup", response_model=schemas.Token)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_password = user.password  # In production, use: get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or user.hashed_password != form_data.password:  # In production, use: verify_password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Store login history
    login_history = models.UserLoginHistory(
        user_id=user.id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    db.add(login_history)
    db.commit()
    
    # Generate tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "user_type": user.user_type}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username, "user_type": user.user_type})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# File routes
ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx"}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Add strict role check
    if current_user.user_type != "operation":  # Make sure this is a string comparison
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operation users can upload files"
        )
    
    # Check file type
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_path = s3_service.upload_file(file.file, unique_filename)
        
        # Save file metadata to database
        file_record = models.File(
            file_name=file.filename,
            file_path=s3_path,
            file_type=file_extension,
            file_size=0,  # In production, get actual file size
            owner_id=current_user.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return {"file_path": s3_path, "file_id": file_record.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@app.get("/download/{file_id}", response_model=schemas.FileDownloadResponse)
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a pre-signed URL to download a file.
    Returns a JSON object with the download URL.
    """
    # Check if user is client
    if current_user.user_type != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client users can download files"
        )
    
    # Get file from database
    file_record = db.query(models.File).filter(models.File.id == file_id).first()
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Generate a pre-signed URL that expires in 1 hour
        presigned_url = s3_service.generate_presigned_url(file_record.file_path)
        return {"download_url": presigned_url, "file_name": file_record.file_name}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating download URL: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
