import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import requests
import json
import pickle
import joblib
import sqlite3
import datetime
import os
import sys
import random
from dotenv import load_dotenv

# =============================================
# 1. DATABASE FUNCTIONS
# =============================================
def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, crop TEXT, 
                  N INT, P INT, K INT, temp REAL, humidity REAL, ph REAL, rainfall REAL)''')
    conn.commit()
    conn.close()

def save_recommendation(crop, features):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("""INSERT INTO recommendations 
                 (date, crop, N, P, K, temp, humidity, ph, rainfall) 
                 VALUES (?,?,?,?,?,?,?,?,?)""",
              (datetime.datetime.now().isoformat(), crop, *features))
    conn.commit()
    conn.close()

# =============================================
# 2. WEATHER FUNCTION
# =============================================
load_dotenv()
def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'].capitalize(),
            }
    except:
        return None
    return None

# =============================================
# 3. PAGE CONFIGURATION
# =============================================
st.set_page_config(
    page_title="🌾 Smart Crop Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()

# =============================================
# 4. PROFESSIONAL CSS
# =============================================
st.markdown("""
<style>
    /* ---- Main Background ---- */
    .stApp {
        background: linear-gradient(135deg, #f5f7f0 0%, #e8ede4 100%);
    }
    
    /* ---- Sidebar Styling ---- */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a3a2a 0%, #2d5a47 100%);
    }
    .css-1d391kg .stSelectbox label, 
    .css-1d391kg .stTextInput label,
    .css-1d391kg .stRadio label {
        color: #e8f5e9 !important;
        font-weight: 500 !important;
    }
    .css-1d391kg .stSelectbox div[data-baseweb="select"] {
        background-color: #2d5a47;
        border-radius: 10px;
        border: 1px solid #4caf84;
    }
    .css-1d391kg .stTextInput input {
        background-color: #2d5a47;
        border-radius: 10px;
        border: 1px solid #4caf84;
        color: white !important;
    }
    .css-1d391kg .stRadio > div {
        background-color: #2d5a47;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* ---- Sidebar Text ---- */
    .sidebar-title {
        color: #a5d6a7 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-align: center;
    }
    .sidebar-subtitle {
        color: #c8e6c9 !important;
        font-size: 0.85rem !important;
        text-align: center;
        opacity: 0.8;
    }
    
    /* ---- Header ---- */
    .main-header {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d5a47 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(26, 58, 42, 0.3);
        text-align: center;
        border: 1px solid rgba(76, 175, 132, 0.3);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .main-header p {
        color: #a5d6a7;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* ---- Glass Cards ---- */
    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 1.8rem 2rem;
        box-shadow: 0 8px 32px rgba(26, 58, 42, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(26, 58, 42, 0.15);
    }
    .glass-card h3 {
        color: #1a3a2a;
        font-weight: 700;
        border-bottom: 3px solid #4caf84;
        padding-bottom: 0.7rem;
        margin-top: 0;
        display: inline-block;
    }
    .glass-card .subtitle {
        color: #5a7a6a;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* ---- Result Box ---- */
    .result-box {
        background: linear-gradient(145deg, #1a3a2a, #2d5a47);
        border-radius: 30px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(26, 58, 42, 0.35);
        border: 1px solid #4caf84;
        animation: fadeInUp 0.6s ease;
    }
    .result-box h2 {
        color: #a5d6a7;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .result-box .crop-name {
        color: #f5ffb2;
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1.1;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin: 0.5rem 0;
    }
    .result-box .confidence {
        color: #b8e6d0;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    .result-box .confidence span {
        background: rgba(255,255,255,0.1);
        padding: 0.3rem 1rem;
        border-radius: 20px;
    }
    
    /* ---- Buttons ---- */
    .stButton button {
        background: linear-gradient(145deg, #1a3a2a, #2d5a47) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.7rem 3rem !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(26, 58, 42, 0.3) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px;
        width: 100% !important;
    }
    .stButton button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 8px 30px rgba(26, 58, 42, 0.4) !important;
        background: linear-gradient(145deg, #2d5a47, #1a3a2a) !important;
    }
    
    /* ---- Weather Widget ---- */
    .weather-widget {
        background: rgba(26, 58, 42, 0.06);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        border-left: 5px solid #4caf84;
        margin: 0.5rem 0;
    }
    .weather-widget .temp {
        font-size: 2rem;
        font-weight: 700;
        color: #1a3a2a;
    }
    
    /* ---- Metrics ---- */
    .metric-box {
        background: rgba(255,255,255,0.6);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(76, 175, 132, 0.2);
    }
    .metric-box .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a3a2a;
    }
    .metric-box .label {
        font-size: 0.8rem;
        color: #5a7a6a;
        font-weight: 500;
    }
    
    /* ---- Disease Boxes ---- */
    .disease-box {
        background: linear-gradient(145deg, #b71c1c, #d32f2f);
        border-radius: 30px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(183, 28, 28, 0.35);
        border: 1px solid #ef5350;
        animation: fadeInUp 0.6s ease;
    }
    .disease-box h2 {
        color: #ffcdd2;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .disease-box h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .healthy-box {
        background: linear-gradient(145deg, #1a3a2a, #2d5a47);
        border-radius: 30px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(26, 58, 42, 0.35);
        border: 1px solid #4caf84;
        animation: fadeInUp 0.6s ease;
    }
    .healthy-box h2 {
        color: #a5d6a7;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .healthy-box h1 {
        color: #a5d6a7;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* ---- Animations ---- */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* ---- Footer ---- */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        color: #5a7a6a;
        font-size: 0.85rem;
        border-top: 1px solid rgba(26, 58, 42, 0.1);
        letter-spacing: 0.5px;
    }
    .footer span {
        color: #4caf84;
        font-weight: 600;
    }
    
    /* ---- Slider Styling ---- */
    .stSlider > div > div > div > div {
        background-color: #4caf84 !important;
    }
    
    /* ---- Image Styling ---- */
    .stImage img {
        border-radius: 20px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# 5. LOAD MODELS
# =============================================
@st.cache_resource
def load_models():
    try:
        model = joblib.load("models/best_crop_model.pkl")
        encoder = joblib.load("models/label_encoder.pkl")
        return model, encoder
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None

model, encoder = load_models()

# =============================================
# 6. SIDEBAR
# =============================================
with st.sidebar:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=90)
    st.markdown('<p class="sidebar-title">🌿 Smart Crop</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">AI-powered farming assistant</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    app_mode = st.radio(
        "Choose Feature",
        ["🌾 Crop Recommendation", "🧪 Disease Detection"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### ⚙️ Weather")
    api_key = st.text_input("API Key", type="password", placeholder="Enter your key", label_visibility="collapsed")
    city = st.text_input("📍 City", value="Delhi", label_visibility="collapsed")
    
    st.divider()
    st.caption("Made with ❤️ for farmers")

# =============================================
# 7. CROP RECOMMENDATION
# =============================================
if app_mode == "🌾 Crop Recommendation":
    st.markdown("""
    <div class="main-header">
        <h1>🌾 Smart Crop Recommendation</h1>
        <p>AI-powered insights to maximize your agricultural yield</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Weather
    if api_key and city:
        weather = get_weather(city)
        if weather:
            col_w1, col_w2, col_w3, col_w4 = st.columns(4)
            with col_w1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{weather['temp']}°C</div>
                    <div class="label">🌡️ Temperature</div>
                </div>
                """, unsafe_allow_html=True)
            with col_w2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{weather['humidity']}%</div>
                    <div class="label">💧 Humidity</div>
                </div>
                """, unsafe_allow_html=True)
            with col_w3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">☁️</div>
                    <div class="label">{weather['description']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_w4:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{"🌱 Growing" if weather['temp'] > 15 else "❄️ Cool"}</div>
                    <div class="label">📅 Status</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main Input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌱 Soil Parameters")
        st.markdown('<p class="subtitle">Adjust sliders to match your field conditions</p>', unsafe_allow_html=True)
        
        N = st.slider("🧪 Nitrogen (N)", 0, 140, 50)
        P = st.slider("🧪 Phosphorus (P)", 0, 145, 50)
        K = st.slider("🧪 Potassium (K)", 0, 205, 50)
        temperature = st.slider("🌡️ Temperature (°C)", 0.0, 50.0, 25.0, step=0.5)
        humidity = st.slider("💧 Humidity (%)", 0.0, 100.0, 60.0, step=1.0)
        ph = st.slider("⚗️ Soil pH", 3.5, 10.0, 6.5, step=0.1)
        rainfall = st.slider("🌧️ Rainfall (mm)", 0.0, 300.0, 100.0, step=5.0)
        
        if ph < 5.5 or ph > 8.0:
            st.warning("⚠️ pH outside ideal range (5.5–8.0). Consider soil amendments.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Results", unsafe_allow_html=True)
        
        if st.button("🌿 Recommend Crop"):
            if model is None or encoder is None:
                st.error("❌ Model not loaded. Check logs.")
            else:
                with st.spinner("Analyzing soil data..."):
                    features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
                    pred_num = model.predict(features)[0]
                    crop = encoder.inverse_transform([pred_num])[0]
                    
                    confidence = 0.0
                    if hasattr(model, "predict_proba"):
                        probs = model.predict_proba(features)
                        confidence = float(np.max(probs) * 100)
                    
                    save_recommendation(crop, [N, P, K, temperature, humidity, ph, rainfall])
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <h2>🌾 Recommended Crop</h2>
                        <div class="crop-name">{crop.upper()}</div>
                        <div class="confidence"><span>Confidence: {confidence:.1f}%</span></div>
                        <div style="margin-top:1rem; color:#b8e6d0; font-size:0.9rem;">
                            N:{N} | P:{P} | K:{K} | pH:{ph}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tips = {
                        "Rice": "🌾 Requires standing water. Ensure good irrigation.",
                        "Wheat": "🌾 Cool season crop. Needs well-drained soil.",
                        "Maize": "🌽 Warm season crop. High sunlight requirement.",
                        "Cotton": "🌿 Needs long frost-free periods.",
                        "Sugarcane": "🌱 Heavy feeder. Requires deep, rich soil.",
                        "Mango": "🥭 Needs dry season before flowering.",
                        "Banana": "🍌 Requires high humidity and consistent rainfall."
                    }
                    st.info(f"💡 {tips.get(crop, 'Ensure proper crop rotation and organic fertilizers.')}")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# 8. DISEASE DETECTION
# =============================================
else:
    st.markdown("""
    <div class="main-header">
        <h1>🧪 Plant Disease Detection</h1>
        <p>Upload a leaf photo to diagnose diseases and get treatment</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 Upload leaf image (JPG, PNG, JPEG)",
        type=["jpg", "jpeg", "png"],
        help="Ensure the leaf is clearly visible in good lighting"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="📸 Uploaded Leaf", use_container_width=True)
        
        with col2:
            if st.button("🔬 Analyze Disease", use_container_width=True):
                with st.spinner("🧪 Analyzing..."):
                    diseases = ["Bacterial Spot", "Healthy", "Leaf Blight", "Powdery Mildew", "Rust"]
                    result = random.choice(diseases)
                    confidence = round(random.uniform(85.0, 99.0), 1)
                    
                    if result != "Healthy":
                        st.markdown(f"""
                        <div class="disease-box">
                            <h2>⚠️ Disease Detected</h2>
                            <h1>{result}</h1>
                            <p style="color:#ffcdd2; font-size:1.2rem;">Confidence: {confidence}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        treatments = {
                            "Bacterial Spot": """
                                🧪 **Treatment:**
                                1. 🗑️ Remove infected leaves.
                                2. 💧 Avoid overhead watering.
                                3. 🧴 Apply copper-based bactericides.
                                4. 🌱 Rotate crops.
                            """,
                            "Leaf Blight": """
                                🧪 **Treatment:**
                                1. ✂️ Prune infected parts.
                                2. 🧴 Apply fungicides.
                                3. 🌬️ Improve air circulation.
                            """,
                            "Powdery Mildew": """
                                🧪 **Treatment:**
                                1. 🗑️ Remove infected leaves.
                                2. 🧴 Apply sulfur or neem oil.
                                3. ☀️ Increase sunlight.
                            """,
                            "Rust": """
                                🧪 **Treatment:**
                                1. ✂️ Remove infected leaves.
                                2. 🧴 Apply fungicides.
                                3. 🌱 Use disease-free seeds.
                            """
                        }
                        st.info(treatments.get(result, "Consult a local expert."))
                    else:
                        st.markdown(f"""
                        <div class="healthy-box">
                            <h2>✅ Plant is Healthy</h2>
                            <h1>Good News!</h1>
                            <p style="color:#b8e6d0; font-size:1.2rem;">Confidence: {confidence}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("🌿 Your plant looks healthy! Continue proper care.")
    
    st.divider()
    st.caption("📌 Demo Mode: Real disease model coming soon!")

# =============================================
# 9. FOOTER
# =============================================
st.markdown("""
<div class="footer">
    🌱 <span>Smart Crop Assistant v2.0</span> &nbsp;·&nbsp; 
    Data-driven decisions for sustainable farming
</div>
""", unsafe_allow_html=True)