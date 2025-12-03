# 🔧 KitForge - 3D Printing Kit Card Builder MVP

**KitForge** is a powerful tool for 3D printing enthusiasts and professionals to analyze STL/3MF files, calculate material costs, estimate print times, and generate professional kit cards. Built with FastAPI, Streamlit, and trimesh for robust 3D model analysis.

---

## 🚀 Features

### Core Functionality
* **3D Model Analysis** - Upload STL/3MF/OBJ files for automated analysis
* **Geometric Extraction** - Volume, bounding box, surface area, mesh quality
* **Material Cost Calculation** - Accurate cost estimation based on material type and infill
* **Print Time Estimation** - Intelligent heuristics based on volume and complexity
* **Complexity Scoring** - 0-10 rating based on geometry, aspect ratio, and mesh quality
* **Kit Card Generation** - Export as Markdown, JSON, or PDF

### Authentication & Tiers
* **JWT Token Authentication** - Secure user sessions
* **Freemium Model** - 5 free kit cards per month
* **Paid Tier** - Unlimited cards + PDF export

### Engineering Pipeline
* **Trimesh Integration** - Professional-grade 3D mesh analysis
* **Watertightness Detection** - Identify mesh repair needs
* **Multi-shell Detection** - Analyze complex geometries
* **Preview Generation** - Automatic 3D model thumbnails

---

## 📁 Project Structure

```
kitforge/
├── backend/
│   ├── api/
│   │   ├── main.py                # FastAPI backend service
│   │   ├── compute_pipeline.py    # 3D model scanning & analysis
│   │   ├── pricing_engine.py      # Cost & time estimation
│   │   ├── card_generator.py      # Kit card output engine
│   │   └── auth.py                # JWT authentication
│   ├── models/
│   │   ├── user.py                # User data models
│   │   └── kitcard.py             # KitCard data models
│   └── storage/
│
├── frontend/
│   ├── app.py                     # Streamlit main application
│   ├── components/                # Modular UI blocks
│   └── session/
│
├── uploads/                       # Uploaded 3D files
├── output/                        # Generated kit cards
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment configuration template
└── README.md
```

---

## ⚙️ Tech Stack

**Backend:**
- FastAPI - High-performance async API framework
- Trimesh - 3D mesh processing and analysis
- ReportLab - PDF generation
- Python-JOSE - JWT token handling
- Passlib - Password hashing with bcrypt

**Frontend:**
- Streamlit - Rapid web application framework
- Requests - HTTP client for API communication

**3D Processing:**
- Trimesh - Mesh loading, analysis, and manipulation
- NumPy - Numerical computations
- NetworkX - Graph-based mesh operations

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- pip or conda

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/kitforge.git
cd kitforge
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Key Environment Variables:**
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/kitforge
DEFAULT_MATERIAL_DENSITY=1.24  # PLA in g/cm³
DEFAULT_COST_PER_GRAM=0.02     # USD per gram
FREE_TIER_CARDS_PER_MONTH=5
```

### 4. Create Required Directories

```bash
mkdir -p uploads output
```

---

## 🚀 Running the Application

### Start the Backend API

```bash
cd backend/api
python main.py
```

The API will be available at `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Start the Streamlit Frontend

In a new terminal:

```bash
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### 1. Authentication

**Demo Account:**
- Username: `demo`
- Password: `demo123`

Or register a new account through the Streamlit interface.

### 2. Upload 3D Model

- Click "Choose an STL or 3MF file"
- Select your 3D model file
- Click "Upload & Analyze"

### 3. Review Analysis

The system will extract:
- **Volume** and **Mass**
- **Material Cost** and **Print Time**
- **Mesh Quality** metrics
- **Complexity Score**
- **Recommended Settings**

### 4. Generate Kit Card

Choose your export format:
- **Markdown** - Free tier, human-readable
- **JSON** - Free tier, machine-readable
- **PDF** - Paid tier only, professional output

---

## 🧪 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT token
- `GET /auth/me` - Get current user info

### File Operations
- `POST /upload` - Upload 3D model file
- `POST /analyze` - Analyze uploaded model
- `POST /generate-card` - Generate kit card
- `GET /download/{filename}` - Download generated card

### Health
- `GET /health` - API health check

---

## 🔬 3D Analysis Pipeline

### Geometric Properties
```python
volume_cm3 = mesh.volume / 1000.0
bounding_box = mesh.bounding_box.extents
surface_area_cm2 = mesh.area / 100.0
```

### Mesh Quality
```python
triangle_count = len(mesh.faces)
is_watertight = mesh.is_watertight
shell_count = len(mesh.split())
```

### Complexity Score (0-10)
Factors:
- Triangle density
- Shell count
- Aspect ratio (tall/thin parts)
- Watertightness
- Surface area to volume ratio

### Material Cost
```python
mass_g = volume_cm3 * density * infill_factor
cost = mass_g * cost_per_gram
```

### Print Time Estimation
```python
base_time = volume_cm3 / print_speed
adjusted_time = base_time * complexity_multiplier * infill_multiplier
```

---

## 📊 Material Database

| Material | Density (g/cm³) | Cost per Gram |
|----------|-----------------|---------------|
| PLA      | 1.24            | $0.02         |
| ABS      | 1.04            | $0.025        |
| PETG     | 1.27            | $0.03         |
| TPU      | 1.21            | $0.05         |
| Nylon    | 1.14            | $0.06         |
| ASA      | 1.07            | $0.035        |

---

## 🎯 Freemium Model

### Free Tier
- ✅ 5 kit cards per month
- ✅ Markdown export
- ✅ JSON export
- ❌ PDF export
- ❌ Custom branding

### Paid Tier
- ✅ Unlimited kit cards
- ✅ All export formats (MD, JSON, PDF)
- ✅ Saved templates (future)
- ✅ Custom livery selection (future)

---

## 🛣️ Roadmap

### Phase 1 (Current - MVP)
- [x] STL/3MF file upload
- [x] 3D model analysis
- [x] Material cost calculation
- [x] Kit card generation (MD/JSON/PDF)
- [x] Basic authentication
- [x] Freemium enforcement

### Phase 2 (Next Sprint)
- [ ] PostgreSQL database integration
- [ ] User dashboard with history
- [ ] Saved templates
- [ ] Multiple material profiles
- [ ] Batch processing

### Phase 3 (Future)
- [ ] Livery generator (camo patterns)
- [ ] Hydrodip visualization
- [ ] Print farm integration
- [ ] Forger's Supply drops system
- [ ] Community marketplace

---

## 🧰 Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black backend/ frontend/
flake8 backend/ frontend/
```

### API Documentation

FastAPI automatically generates interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🐳 Docker Deployment (Future)

```bash
docker-compose up -d
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 💬 Support

For issues, questions, or feature requests:
- Open a GitHub issue
- Email: support@kitforge.com

---

## 🎖️ Credits

**Built with:**
- FastAPI - Modern Python web framework
- Streamlit - Rapid UI development
- Trimesh - 3D mesh processing
- ReportLab - PDF generation

**Philosophy:**
> "Engineering rituals, automated. KitForge transforms 3D printing from a hobby into a craft."

---

**KitForge MVP** | *Strength. Craftsmanship. Repeatable Excellence.*
