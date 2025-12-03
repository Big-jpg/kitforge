# 🚀 KitForge Quick Start Guide

Get up and running with KitForge in 5 minutes!

---

## Prerequisites

- Python 3.11+
- Git

---

## Installation (3 Steps)

### 1. Clone & Setup

```bash
git clone https://github.com/Big-jpg/kitforge.git
cd kitforge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Start Backend

```bash
cd backend/api
python main.py
```

✅ API running at `http://localhost:8000`

### 3. Start Frontend (New Terminal)

```bash
cd kitforge
source venv/bin/activate
streamlit run frontend/app.py
```

✅ App opens in browser at `http://localhost:8501`

---

## First Use

### Login with Demo Account

- **Username:** `demo`
- **Password:** `demo123`

### Generate Test STL

```bash
python create_test_stl.py
```

### Upload & Analyze

1. Click "Choose an STL or 3MF file"
2. Select `test_part.stl`
3. Click "Upload & Analyze"
4. Review analysis results
5. Click "Generate Markdown" or "Generate JSON"

---

## API Testing

### Quick Test

```bash
python test_api.py
```

### Manual API Test

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Save the token and use it:
TOKEN="your-token-here"

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

---

## What You Get

✅ **3D Model Analysis**
- Volume, mass, bounding box
- Mesh quality metrics
- Complexity scoring

✅ **Cost Estimation**
- Material cost calculation
- Print time estimation
- Recommended settings

✅ **Kit Card Generation**
- Markdown export (free)
- JSON export (free)
- PDF export (paid tier)

---

## Freemium Limits

**Free Tier:**
- 5 kit cards per month
- Markdown & JSON export
- All analysis features

**Paid Tier:**
- Unlimited kit cards
- PDF export
- Custom branding (future)

---

## Troubleshooting

### Port Already in Use

```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### API Not Responding

```bash
# Check if running
curl http://localhost:8000/health
```

---

## Next Steps

1. **Read Full Documentation:** [README.md](README.md)
2. **Run Tests:** [TESTING.md](TESTING.md)
3. **View Project Summary:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
4. **Explore API Docs:** http://localhost:8000/docs

---

## Support

- **GitHub Issues:** https://github.com/Big-jpg/kitforge/issues
- **API Docs:** http://localhost:8000/docs

---

**Happy Forging! 🔧**
