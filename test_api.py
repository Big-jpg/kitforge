#!/usr/bin/env python3
"""
Test the complete KitForge API workflow
"""

import requests
import json

API_BASE = "http://localhost:8000"

print("🔧 Testing KitForge API\n")

# 1. Login
print("1. Logging in...")
response = requests.post(f"{API_BASE}/auth/login", json={
    "username": "demo",
    "password": "demo123"
})
token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Logged in successfully\n")

# 2. Upload file
print("2. Uploading test STL file...")
with open('test_part.stl', 'rb') as f:
    files = {'file': ('test_part.stl', f, 'application/octet-stream')}
    response = requests.post(f"{API_BASE}/upload", files=files, headers=headers)
    upload_data = response.json()
    file_path = upload_data['path']
    print(f"✅ File uploaded: {file_path}\n")

# 3. Analyze model
print("3. Analyzing 3D model...")
response = requests.post(
    f"{API_BASE}/analyze",
    params={"file_path": file_path, "part_name": "Test Box"},
    headers=headers
)
analysis = response.json()
print(f"✅ Analysis complete!")
print(f"   Volume: {analysis['volume_cm3']} cm³")
print(f"   Mass: {analysis['mass_g']} g")
print(f"   Cost: ${analysis['est_material_cost']}")
print(f"   Print Time: {analysis['est_print_time_hours']} hours")
print(f"   Complexity: {analysis['complexity_score']}/10\n")

# 4. Generate Markdown card
print("4. Generating Markdown kit card...")
response = requests.post(
    f"{API_BASE}/generate-card",
    params={"format": "markdown"},
    json=analysis,
    headers=headers
)
result = response.json()
print(f"✅ Kit card generated: {result['output_path']}\n")

# 5. Generate JSON card
print("5. Generating JSON kit card...")
response = requests.post(
    f"{API_BASE}/generate-card",
    params={"format": "json"},
    json=analysis,
    headers=headers
)
result = response.json()
print(f"✅ Kit card generated: {result['output_path']}\n")

print("🎉 All tests passed!")
