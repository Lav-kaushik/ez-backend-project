# File Management API

A secure FastAPI-based file management system that allows users to upload and download files with role-based access control.

## Features

- 🔐 JWT-based authentication system
- 👥 Two user roles: Client and Operation
- 📁 File upload with support for PPTX, DOCX, and XLSX formats
- 📥 Secure file download with pre-signed S3 URLs
- 📊 File metadata tracking (size, type, upload time)
- 🔄 Refresh token support for better security
- 🛡️ CORS enabled for frontend integration

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (can be easily configured to use PostgreSQL/MySQL)
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: AWS S3
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.8+
- AWS Account with S3 access
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ez_dir
2.Create and activate a virtual environment
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  
3. Install dependencies
  pip install -r requirements.txt

4. Set up environment variables: Create a .env file in the project root with the following variables:
    At mention
    DATABASE_URL=sqlite:///./test.db
   
    SECRET_KEY=your-secret-key-here
   
    ALGORITHM=HS256
   
    ACCESS_TOKEN_EXPIRE_MINUTES=30
   
    AWS_ACCESS_KEY_ID=your-aws-access-key
   
    AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   
    AWS_REGION=your-aws-region
   
    S3_BUCKET_NAME=your-s3-bucket-name

   
**RUNNING THE APPLICATION**
1. Initialize the database:
  python init_db.py
2. Start the FastAPI server:
    python main.py
3. Access the API documentation at:
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc






  
