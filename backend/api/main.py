# backend/api/main.py
"""
KitForge FastAPI Backend
Main API service for 3D model processing and kit card generation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import shutil
from pathlib import Path
import os
from datetime import timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.user import UserCreate, UserLogin, Token
from backend.models.kitcard import KitCard, KitCardCreate
from backend.api.compute_pipeline import analyzer
from backend.api.pricing_engine import pricing_engine
from backend.api.card_generator import card_generator
from backend.api.auth import (
    user_store,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialize FastAPI app
app = FastAPI(
    title="KitForge API",
    description="3D Model Analysis and Kit Card Generation API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Directories
UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', './uploads'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './output'))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Dependency: Get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return current user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_store.get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "KitForge API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = user_store.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user['username']},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and receive JWT token"""
    user = user_store.authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user['username']},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user['username'],
        "email": current_user['email'],
        "subscription_tier": current_user['subscription_tier'],
        "cards_generated_this_month": current_user['cards_generated_this_month']
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a 3D model file (STL/3MF)"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.stl', '.3mf', '.obj', '.ply']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: .stl, .3mf, .obj, .ply"
        )
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{current_user['username']}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return {
        "filename": file.filename,
        "path": str(file_path),
        "size_bytes": file_path.stat().st_size
    }


@app.post("/analyze")
async def analyze_model(
    file_path: str,
    part_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Analyze a 3D model and return metrics"""
    
    # Validate file exists
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Run analysis
        analysis = analyzer.analyze_model(file_path, output_dir=str(OUTPUT_DIR))
        
        # Calculate pricing
        pricing = pricing_engine.calculate_full_pricing(
            volume_cm3=analysis['geometry']['volume_cm3'],
            complexity_score=analysis['complexity_score'],
            bounding_box=analysis['geometry']['bounding_box']
        )
        
        # Combine results
        result = {
            'part_name': part_name or Path(file_path).stem,
            'file_hash': analysis['file_hash'],
            'volume_cm3': analysis['geometry']['volume_cm3'],
            'surface_area_cm2': analysis['geometry']['surface_area_cm2'],
            'bounding_box': analysis['geometry']['bounding_box'],
            'mass_g': pricing['mass_g'],
            'triangle_count': analysis['quality']['triangle_count'],
            'is_watertight': analysis['quality']['is_watertight'],
            'shell_count': analysis['quality']['shell_count'],
            'complexity_score': analysis['complexity_score'],
            'est_material_cost': pricing['material_cost_usd'],
            'est_print_time_hours': pricing['est_print_time_hours'],
            'recommended_layer_height': pricing['recommended_settings']['layer_height_mm'],
            'recommended_infill': pricing['recommended_settings']['infill_percentage'],
            'preview_image_path': analysis['preview_image_path']
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/generate-card")
async def generate_card(
    card_data: dict,
    format: str = "markdown",
    current_user: dict = Depends(get_current_user)
):
    """Generate a kit card in the specified format"""
    
    # Check if user can generate cards
    can_generate, reason = user_store.can_generate_card(current_user['username'])
    
    if not can_generate:
        raise HTTPException(status_code=403, detail=reason)
    
    # Check PDF access (paid tier only)
    if format.lower() == 'pdf' and current_user['subscription_tier'] != 'paid':
        raise HTTPException(
            status_code=403,
            detail="PDF export is only available for paid tier users"
        )
    
    try:
        # Generate the card
        output_path = card_generator.generate_card(
            card_data=card_data,
            format=format,
            include_preview=True
        )
        
        # Increment user's card count
        user_store.increment_card_count(current_user['username'])
        
        return {
            "success": True,
            "format": format,
            "output_path": output_path,
            "cards_remaining": user_store.can_generate_card(current_user['username'])[1]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Card generation failed: {str(e)}")


@app.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Download a generated kit card file"""
    
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KitForge API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 8000)),
        reload=True
    )
