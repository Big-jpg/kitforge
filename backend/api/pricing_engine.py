# backend/api/pricing_engine.py
"""
Pricing Engine - Material cost and print time estimation
"""

from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class PricingEngine:
    """Calculate material costs and print time estimates"""
    
    def __init__(self):
        # Material defaults (can be overridden)
        self.default_density = float(os.getenv('DEFAULT_MATERIAL_DENSITY', 1.24))  # g/cm³
        self.default_cost_per_gram = float(os.getenv('DEFAULT_COST_PER_GRAM', 0.02))  # USD
        self.fdm_print_speed = float(os.getenv('FDM_PRINT_SPEED', 20.0))  # cm³/hour
        
        # Material database (expandable)
        self.materials = {
            'PLA': {'density': 1.24, 'cost_per_gram': 0.02},
            'ABS': {'density': 1.04, 'cost_per_gram': 0.025},
            'PETG': {'density': 1.27, 'cost_per_gram': 0.03},
            'TPU': {'density': 1.21, 'cost_per_gram': 0.05},
            'Nylon': {'density': 1.14, 'cost_per_gram': 0.06},
            'ASA': {'density': 1.07, 'cost_per_gram': 0.035},
        }
    
    def calculate_mass(
        self, 
        volume_cm3: float, 
        material: str = 'PLA',
        infill_percentage: int = 20
    ) -> float:
        """
        Calculate part mass based on volume and material
        
        Args:
            volume_cm3: Part volume in cubic centimeters
            material: Material type (PLA, ABS, etc.)
            infill_percentage: Infill density (0-100)
        
        Returns:
            Mass in grams
        """
        # Get material density
        if material in self.materials:
            density = self.materials[material]['density']
        else:
            density = self.default_density
        
        # Account for infill (simplified model)
        # Assumes 2 perimeters + top/bottom layers = ~30% solid minimum
        effective_density = density * (0.3 + 0.7 * (infill_percentage / 100))
        
        mass_g = volume_cm3 * effective_density
        return round(mass_g, 2)
    
    def calculate_material_cost(
        self,
        mass_g: float,
        material: str = 'PLA'
    ) -> float:
        """
        Calculate material cost based on mass
        
        Args:
            mass_g: Part mass in grams
            material: Material type
        
        Returns:
            Cost in USD
        """
        if material in self.materials:
            cost_per_gram = self.materials[material]['cost_per_gram']
        else:
            cost_per_gram = self.default_cost_per_gram
        
        cost = mass_g * cost_per_gram
        return round(cost, 2)
    
    def estimate_print_time(
        self,
        volume_cm3: float,
        complexity_score: int,
        infill_percentage: int = 20
    ) -> float:
        """
        Estimate print time based on volume and complexity
        
        Args:
            volume_cm3: Part volume
            complexity_score: Complexity rating (0-10)
            infill_percentage: Infill density
        
        Returns:
            Estimated print time in hours
        """
        # Base time from volume
        base_time = volume_cm3 / self.fdm_print_speed
        
        # Complexity multiplier (1.0 to 2.0)
        complexity_multiplier = 1.0 + (complexity_score / 10.0)
        
        # Infill adjustment (higher infill = more time)
        infill_multiplier = 0.8 + (infill_percentage / 100.0) * 0.4
        
        total_time = base_time * complexity_multiplier * infill_multiplier
        
        return round(total_time, 2)
    
    def get_recommended_settings(
        self,
        complexity_score: int,
        bounding_box: tuple
    ) -> Dict:
        """
        Recommend print settings based on part characteristics
        
        Args:
            complexity_score: Part complexity (0-10)
            bounding_box: (x, y, z) dimensions in mm
        
        Returns:
            Dictionary of recommended settings
        """
        # Layer height based on complexity
        if complexity_score >= 7:
            layer_height = 0.12  # Fine detail
        elif complexity_score >= 4:
            layer_height = 0.16  # Standard
        else:
            layer_height = 0.20  # Fast
        
        # Infill based on size and complexity
        max_dim = max(bounding_box)
        if max_dim > 200 or complexity_score >= 7:
            infill = 25  # Stronger for large/complex parts
        else:
            infill = 20  # Standard
        
        # Support detection (simplified heuristic)
        z_height = bounding_box[2]
        xy_max = max(bounding_box[0], bounding_box[1])
        aspect_ratio = z_height / max(xy_max, 1)
        
        supports_needed = aspect_ratio > 2 or complexity_score >= 6
        
        return {
            'layer_height_mm': layer_height,
            'infill_percentage': infill,
            'supports_needed': supports_needed,
            'brim_recommended': max_dim > 150,
            'print_speed_mm_s': 50 if complexity_score >= 6 else 60
        }
    
    def calculate_full_pricing(
        self,
        volume_cm3: float,
        complexity_score: int,
        bounding_box: tuple,
        material: str = 'PLA',
        infill_percentage: Optional[int] = None
    ) -> Dict:
        """
        Complete pricing calculation with all details
        
        Returns:
            Dictionary with mass, cost, time, and settings
        """
        # Get recommended settings if infill not specified
        settings = self.get_recommended_settings(complexity_score, bounding_box)
        if infill_percentage is None:
            infill_percentage = settings['infill_percentage']
        
        # Calculate mass and cost
        mass_g = self.calculate_mass(volume_cm3, material, infill_percentage)
        material_cost = self.calculate_material_cost(mass_g, material)
        
        # Estimate print time
        print_time = self.estimate_print_time(volume_cm3, complexity_score, infill_percentage)
        
        return {
            'mass_g': mass_g,
            'material_cost_usd': material_cost,
            'est_print_time_hours': print_time,
            'recommended_settings': settings,
            'material_used': material
        }


# Singleton instance
pricing_engine = PricingEngine()
