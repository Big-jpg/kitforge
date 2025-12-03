# frontend/app.py
"""
KitForge Streamlit Frontend
Main application interface for kit card generation
"""

import streamlit as st
import requests
from pathlib import Path
import json
from datetime import datetime
import os

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Page configuration
st.set_page_config(
    page_title="KitForge - Kit Card Builder",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ecf0f1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None


def login(username: str, password: str):
    """Login to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data['access_token']
            st.session_state.username = username
            
            # Get user info
            get_user_info()
            return True, "Login successful!"
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, f"Login failed: {str(e)}"


def register(username: str, email: str, password: str):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data['access_token']
            st.session_state.username = username
            
            # Get user info
            get_user_info()
            return True, "Registration successful!"
        else:
            return False, response.json().get('detail', 'Registration failed')
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def get_user_info():
    """Get current user information"""
    if not st.session_state.token:
        return
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            st.session_state.user_info = response.json()
    except Exception as e:
        st.error(f"Failed to get user info: {str(e)}")


def upload_file(file):
    """Upload a 3D model file"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.uploaded_file_path = data['path']
            return True, data
        else:
            return False, response.json().get('detail', 'Upload failed')
    except Exception as e:
        return False, f"Upload failed: {str(e)}"


def analyze_model(file_path: str, part_name: str):
    """Analyze the uploaded 3D model"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            params={"file_path": file_path, "part_name": part_name},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            st.session_state.analysis_result = response.json()
            return True, st.session_state.analysis_result
        else:
            return False, response.json().get('detail', 'Analysis failed')
    except Exception as e:
        return False, f"Analysis failed: {str(e)}"


def generate_card(card_data: dict, format: str):
    """Generate a kit card"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-card",
            params={"format": format},
            json=card_data,
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Generation failed')
    except Exception as e:
        return False, f"Generation failed: {str(e)}"


def logout():
    """Logout and clear session"""
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.user_info = None
    st.session_state.uploaded_file_path = None
    st.session_state.analysis_result = None


# Main application
def main():
    # Header
    st.markdown('<div class="main-header">🔧 KitForge</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Engineering rituals, automated</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/2c3e50/ffffff?text=KitForge", use_container_width=True)
        
        if st.session_state.token:
            st.success(f"👤 Logged in as: **{st.session_state.username}**")
            
            if st.session_state.user_info:
                st.info(f"**Tier:** {st.session_state.user_info['subscription_tier'].upper()}")
                st.info(f"**Cards this month:** {st.session_state.user_info['cards_generated_this_month']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.warning("Please login or register to continue")
    
    # Authentication
    if not st.session_state.token:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Login", use_container_width=True):
                    if login_username and login_password:
                        success, message = login(login_username, login_password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter username and password")
            
            with col2:
                st.info("**Demo Account:** username: `demo`, password: `demo123`")
        
        with tab2:
            st.subheader("Register")
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            
            if st.button("Register", use_container_width=True):
                if reg_username and reg_email and reg_password:
                    success, message = register(reg_username, reg_email, reg_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields")
    
    # Main application (authenticated users only)
    else:
        st.markdown("---")
        
        # File upload section
        st.header("1️⃣ Upload 3D Model")
        
        uploaded_file = st.file_uploader(
            "Choose an STL or 3MF file",
            type=['stl', '3mf', 'obj', 'ply'],
            help="Upload your 3D model file for analysis"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info(f"**File:** {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
            
            with col2:
                if st.button("📤 Upload & Analyze", use_container_width=True):
                    with st.spinner("Uploading file..."):
                        success, result = upload_file(uploaded_file)
                        
                        if success:
                            st.success("File uploaded successfully!")
                            
                            # Analyze the model
                            part_name = st.text_input(
                                "Part Name (optional)",
                                value=Path(uploaded_file.name).stem
                            )
                            
                            with st.spinner("Analyzing 3D model..."):
                                success, analysis = analyze_model(result['path'], part_name)
                                
                                if success:
                                    st.success("Analysis complete!")
                                else:
                                    st.error(analysis)
                        else:
                            st.error(result)
        
        # Analysis results section
        if st.session_state.analysis_result:
            st.markdown("---")
            st.header("2️⃣ Analysis Results")
            
            result = st.session_state.analysis_result
            
            # Display preview image if available
            if result.get('preview_image_path') and Path(result['preview_image_path']).exists():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(result['preview_image_path'], caption="3D Model Preview", use_container_width=True)
                with col2:
                    st.subheader(result['part_name'])
                    st.write(f"**File Hash:** `{result['file_hash'][:16]}...`")
            else:
                st.subheader(result['part_name'])
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Volume", f"{result['volume_cm3']:.2f} cm³")
            with col2:
                st.metric("Mass", f"{result['mass_g']:.2f} g")
            with col3:
                st.metric("Material Cost", f"${result['est_material_cost']:.2f}")
            with col4:
                st.metric("Print Time", f"{result['est_print_time_hours']:.2f} hrs")
            
            # Detailed information
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Geometric Properties")
                st.write(f"**Bounding Box:** {result['bounding_box'][0]:.1f} × {result['bounding_box'][1]:.1f} × {result['bounding_box'][2]:.1f} mm")
                st.write(f"**Surface Area:** {result['surface_area_cm2']:.2f} cm²")
                
                st.subheader("Recommended Settings")
                st.write(f"**Layer Height:** {result['recommended_layer_height']:.2f} mm")
                st.write(f"**Infill:** {result['recommended_infill']}%")
            
            with col2:
                st.subheader("Mesh Quality")
                st.write(f"**Triangle Count:** {result['triangle_count']:,}")
                st.write(f"**Watertight:** {'✅ Yes' if result['is_watertight'] else '⚠️ No'}")
                st.write(f"**Shell Count:** {result['shell_count']}")
                st.write(f"**Complexity Score:** {result['complexity_score']}/10")
            
            # Kit card generation
            st.markdown("---")
            st.header("3️⃣ Generate Kit Card")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Generate Markdown", use_container_width=True):
                    with st.spinner("Generating Markdown kit card..."):
                        success, gen_result = generate_card(result, "markdown")
                        if success:
                            st.success("Markdown kit card generated!")
                            st.info(f"**File:** {gen_result['output_path']}")
                            st.balloons()
                            
                            # Refresh user info
                            get_user_info()
                        else:
                            st.error(gen_result)
            
            with col2:
                if st.button("📊 Generate JSON", use_container_width=True):
                    with st.spinner("Generating JSON kit card..."):
                        success, gen_result = generate_card(result, "json")
                        if success:
                            st.success("JSON kit card generated!")
                            st.info(f"**File:** {gen_result['output_path']}")
                            st.balloons()
                            
                            # Refresh user info
                            get_user_info()
                        else:
                            st.error(gen_result)
            
            with col3:
                if st.session_state.user_info['subscription_tier'] == 'paid':
                    if st.button("📕 Generate PDF", use_container_width=True):
                        with st.spinner("Generating PDF kit card..."):
                            success, gen_result = generate_card(result, "pdf")
                            if success:
                                st.success("PDF kit card generated!")
                                st.info(f"**File:** {gen_result['output_path']}")
                                st.balloons()
                                
                                # Refresh user info
                                get_user_info()
                            else:
                                st.error(gen_result)
                else:
                    st.button("📕 Generate PDF (Paid Only)", use_container_width=True, disabled=True)
                    st.caption("⭐ Upgrade to paid tier for PDF export")


if __name__ == "__main__":
    main()
