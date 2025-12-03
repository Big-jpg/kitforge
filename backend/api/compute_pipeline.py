# backend/api/compute_pipeline.py
"""
3D Model Analysis Pipeline
Extracts geometric properties, mesh quality, and complexity metrics
"""

import trimesh
import numpy as np
from typing import Dict, Tuple, Optional
import hashlib
from pathlib import Path


class ModelAnalyzer:
    """Analyzes 3D models (STL/3MF) and extracts engineering metrics"""
    
    def __init__(self):
        self.supported_formats = ['.stl', '.3mf', '.obj', '.ply']
    
    def load_model(self, file_path: str) -> trimesh.Trimesh:
        """Load a 3D model file using trimesh"""
        try:
            mesh = trimesh.load(file_path, force='mesh')
            
            # Handle multi-part files (3MF often contains multiple meshes)
            if isinstance(mesh, list):
                # Combine all meshes into a single mesh
                if len(mesh) == 0:
                    raise ValueError("File contains no meshes")
                elif len(mesh) == 1:
                    mesh = mesh[0]
                else:
                    # Concatenate multiple meshes
                    mesh = trimesh.util.concatenate(mesh)
            
            # Handle Scene objects (some formats return scenes)
            elif isinstance(mesh, trimesh.Scene):
                # Dump the scene to a single mesh
                mesh = mesh.dump(concatenate=True)
            
            return mesh
        except Exception as e:
            raise ValueError(f"Failed to load 3D model: {str(e)}")
    
    def compute_file_hash(self, file_path: str) -> str:
        """Generate SHA256 hash of file for deduplication"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def extract_geometry(self, mesh: trimesh.Trimesh) -> Dict:
        """Extract basic geometric properties"""
        # Volume in cm³ (trimesh returns mm³)
        volume_cm3 = mesh.volume / 1000.0
        
        # Bounding box in mm
        bbox = mesh.bounding_box.extents
        
        # Surface area in cm²
        surface_area_cm2 = mesh.area / 100.0
        
        return {
            'volume_cm3': round(volume_cm3, 2),
            'bounding_box': tuple(round(x, 2) for x in bbox),
            'surface_area_cm2': round(surface_area_cm2, 2)
        }
    
    def analyze_mesh_quality(self, mesh: trimesh.Trimesh) -> Dict:
        """Analyze mesh quality and topology"""
        return {
            'triangle_count': len(mesh.faces),
            'is_watertight': mesh.is_watertight,
            'shell_count': len(mesh.split()),
            'vertex_count': len(mesh.vertices)
        }
    
    def compute_complexity_score(self, mesh: trimesh.Trimesh, geometry: Dict) -> int:
        """
        Calculate complexity score (0-10) based on multiple factors:
        - Triangle density
        - Shell count
        - Thin walls detection
        - Aspect ratio
        - Watertightness
        """
        score = 0
        
        # Triangle density (normalized)
        tri_density = len(mesh.faces) / max(geometry['volume_cm3'], 1)
        if tri_density > 1000:
            score += 2
        elif tri_density > 500:
            score += 1
        
        # Multiple shells add complexity
        shell_count = len(mesh.split())
        if shell_count > 3:
            score += 2
        elif shell_count > 1:
            score += 1
        
        # Aspect ratio (tall/thin parts are harder)
        bbox = geometry['bounding_box']
        max_dim = max(bbox)
        min_dim = min(bbox)
        aspect_ratio = max_dim / max(min_dim, 0.1)
        if aspect_ratio > 10:
            score += 2
        elif aspect_ratio > 5:
            score += 1
        
        # Non-watertight meshes need repair
        if not mesh.is_watertight:
            score += 2
        
        # Surface area to volume ratio (thin walls)
        sa_vol_ratio = geometry['surface_area_cm2'] / max(geometry['volume_cm3'], 0.1)
        if sa_vol_ratio > 50:
            score += 2
        elif sa_vol_ratio > 25:
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def generate_preview_image(self, mesh: trimesh.Trimesh, output_path: str) -> str:
        """Generate a preview image of the 3D model"""
        try:
            # Create a scene with the mesh
            scene = mesh.scene()
            
            # Render to PNG
            png_data = scene.save_image(resolution=[800, 600])
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(png_data)
            
            return output_path
        except Exception as e:
            print(f"Warning: Could not generate preview image: {str(e)}")
            return None
    
    def analyze_model(
        self, 
        file_path: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Complete analysis pipeline for a 3D model
        Returns all extracted metrics
        """
        # Load the model
        mesh = self.load_model(file_path)
        
        # Extract all properties
        geometry = self.extract_geometry(mesh)
        quality = self.analyze_mesh_quality(mesh)
        complexity = self.compute_complexity_score(mesh, geometry)
        
        # Generate preview if output directory provided
        preview_path = None
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            file_hash = self.compute_file_hash(file_path)
            preview_path = f"{output_dir}/{file_hash[:16]}_preview.png"
            preview_path = self.generate_preview_image(mesh, preview_path)
        
        # Compute file hash
        file_hash = self.compute_file_hash(file_path)
        
        return {
            'file_hash': file_hash,
            'geometry': geometry,
            'quality': quality,
            'complexity_score': complexity,
            'preview_image_path': preview_path
        }


# Singleton instance
analyzer = ModelAnalyzer()
