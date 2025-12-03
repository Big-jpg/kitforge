#!/usr/bin/env python3
"""
Create a simple test STL file for testing the KitForge pipeline
"""

import trimesh
import numpy as np

# Create a simple box mesh
box = trimesh.creation.box(extents=[50, 30, 20])  # 50x30x20mm

# Save as STL
box.export('test_part.stl')

print(f"Created test_part.stl")
print(f"Volume: {box.volume / 1000:.2f} cm³")
print(f"Bounding box: {box.bounding_box.extents}")
print(f"Triangles: {len(box.faces)}")
print(f"Watertight: {box.is_watertight}")
