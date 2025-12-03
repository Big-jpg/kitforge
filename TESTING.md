# KitForge Testing Guide

This document provides instructions for testing the KitForge MVP application.

---

## Quick Start Testing

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/kitforge.git
cd kitforge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 2. Start the Backend API

```bash
cd backend/api
python main.py
```

The API will be available at `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### 3. Start the Streamlit Frontend (Optional)

In a new terminal:

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

The app will open at `http://localhost:8501`

---

## Automated Testing

### Generate Test STL File

```bash
python create_test_stl.py
```

This creates a simple 50x30x20mm box for testing.

### Run API Test Suite

```bash
python test_api.py
```

This script tests the complete workflow:
1. ✅ User authentication
2. ✅ File upload
3. ✅ 3D model analysis
4. ✅ Kit card generation (Markdown & JSON)

---

## Manual API Testing

### 1. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

Save the token for subsequent requests.

### 2. Get User Info

```bash
TOKEN="your-token-here"

curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Upload 3D Model

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_part.stl"
```

Response:
```json
{
  "filename": "test_part.stl",
  "path": "uploads/demo_test_part.stl",
  "size_bytes": 684
}
```

### 4. Analyze Model

```bash
FILE_PATH="uploads/demo_test_part.stl"

curl -X POST "http://localhost:8000/analyze?file_path=$FILE_PATH&part_name=Test%20Box" \
  -H "Authorization: Bearer $TOKEN"
```

Response includes:
- Volume, mass, bounding box
- Triangle count, watertightness
- Complexity score
- Material cost estimate
- Print time estimate
- Recommended settings

### 5. Generate Kit Card

```bash
# Markdown format
curl -X POST "http://localhost:8000/generate-card?format=markdown" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @analysis_result.json

# JSON format
curl -X POST "http://localhost:8000/generate-card?format=json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @analysis_result.json
```

---

## Streamlit Frontend Testing

### 1. Login

Use the demo account:
- **Username:** `demo`
- **Password:** `demo123`

Or register a new account.

### 2. Upload File

1. Click "Choose an STL or 3MF file"
2. Select `test_part.stl`
3. Click "Upload & Analyze"

### 3. Review Analysis

The app will display:
- 3D preview image (if generated)
- Geometric properties
- Mesh quality metrics
- Cost and time estimates
- Recommended print settings

### 4. Generate Kit Cards

Click one of the buttons:
- **Generate Markdown** - Free tier
- **Generate JSON** - Free tier
- **Generate PDF** - Paid tier only (disabled for free users)

---

## Test Cases

### Test Case 1: Simple Geometry
**File:** `test_part.stl` (50x30x20mm box)
**Expected Results:**
- Volume: ~30 cm³
- Mass: ~16 g (PLA, 20% infill)
- Cost: ~$0.33
- Print Time: ~1.3 hours
- Complexity: 0-2/10
- Watertight: Yes

### Test Case 2: Complex Geometry
Upload a complex STL with:
- Multiple shells
- High triangle count
- Thin walls

**Expected Results:**
- Higher complexity score (6-10)
- Longer print time
- Finer layer height recommendation

### Test Case 3: Freemium Limits
1. Generate 5 kit cards with free account
2. Attempt to generate 6th card
3. Should receive error: "Free tier limit reached"

### Test Case 4: PDF Export (Paid Tier)
1. Free tier users should see disabled PDF button
2. Paid tier users can generate PDF cards

---

## Performance Testing

### Large File Upload
Test with STL files up to 100MB:
```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@large_model.stl"
```

### Concurrent Requests
Use Apache Bench or similar:
```bash
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/health
```

---

## Error Handling Tests

### Invalid File Format
```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"
```
**Expected:** 400 Bad Request - "Unsupported file format"

### Unauthorized Access
```bash
curl http://localhost:8000/auth/me
```
**Expected:** 401 Unauthorized

### Invalid Credentials
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"wrong"}'
```
**Expected:** 401 Unauthorized - "Incorrect username or password"

### Non-existent File
```bash
curl -X POST "http://localhost:8000/analyze?file_path=nonexistent.stl" \
  -H "Authorization: Bearer $TOKEN"
```
**Expected:** 404 Not Found - "File not found"

---

## Integration Testing

### Complete Workflow
1. Register new user
2. Login
3. Upload 3D model
4. Analyze model
5. Generate Markdown card
6. Generate JSON card
7. Verify output files exist
8. Check user card count incremented

---

## Cleanup

### Stop Backend Server
```bash
# Find the process
ps aux | grep "python main.py"

# Kill it
kill <PID>
```

### Clean Test Files
```bash
rm -rf uploads/*
rm -rf output/*
rm test_part.stl
```

---

## Known Issues

1. **Preview Image Generation:** May fail on some systems without proper graphics libraries
   - Workaround: Analysis continues without preview

2. **Large Files:** Files >100MB may timeout
   - Workaround: Increase timeout in `.env`

3. **Bcrypt Version:** Requires bcrypt 4.0.1 for compatibility
   - Already specified in requirements.txt

---

## Debugging

### Enable Debug Logging
Edit `backend/api/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Logs
```bash
tail -f /tmp/api.log
```

### Streamlit Debug Mode
```bash
streamlit run frontend/app.py --logger.level=debug
```

---

## CI/CD Testing (Future)

### GitHub Actions Workflow
```yaml
name: Test KitForge
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test_api.py
```

---

## Support

For issues or questions:
- Open a GitHub issue
- Check API docs at `http://localhost:8000/docs`
- Review logs in `/tmp/api.log`

---

**Happy Testing! 🔧**
