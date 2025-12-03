# backend/models/kitcard.py
"""
KitCard model - the core data structure for 3D part analysis
"""

from pydantic import BaseModel
from typing import Optional, Tuple
from datetime import datetime


class KitCard(BaseModel):
    """
    The atomic unit of the KitForge ecosystem.
    Contains all metadata extracted from a 3D model file.
    """
    id: Optional[int] = None
    user_id: int
    
    # Part Identification
    part_name: str
    file_hash: str
    original_filename: str
    
    # Geometric Properties
    volume_cm3: float
    mass_g: float
    bounding_box: Tuple[float, float, float]  # (x, y, z) in mm
    surface_area_cm2: float
    
    # Mesh Quality
    triangle_count: int
    is_watertight: bool
    shell_count: int
    
    # Cost Analysis
    est_material_cost: float
    complexity_score: int  # 0-10
    
    # Print Estimation
    est_print_time_hours: float
    recommended_layer_height: float = 0.2  # mm
    recommended_infill: int = 20  # percentage
    
    # Preview
    preview_image_path: Optional[str] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "part_name": "Tactical Grip",
                "volume_cm3": 45.2,
                "mass_g": 56.0,
                "bounding_box": (120.5, 45.3, 30.2),
                "complexity_score": 6,
                "est_material_cost": 1.12,
                "est_print_time_hours": 2.26
            }
        }


class KitCardCreate(BaseModel):
    """Request model for creating a new kit card"""
    part_name: Optional[str] = None
    material_density: Optional[float] = 1.24  # PLA default
    cost_per_gram: Optional[float] = 0.02


class KitCardExport(BaseModel):
    """Export format options"""
    format: str  # "markdown", "json", "pdf"
    include_preview: bool = True
