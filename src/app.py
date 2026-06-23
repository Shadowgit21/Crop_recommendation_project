import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import requests
import json
import pickle
import joblib
from datetime import datetime

# Import our modular helpers
from src.utils.weather import get_weather
from src.utils.database import init_db, save_recommendation

# Initialize database
init_db()

# =============================================
# 1. PAGE CONFIGURATION
# =============================================
st.set_page_config(
    page_title="🌾 Smart Crop Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# 2. CUSTOM CSS
# =============================================
st.markdown("""
<style>
    .main { background-color: #f4f7f2; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #1b5e20; color: white; }
    .result-box { background: #1e3a2f; border-radius: 15px; padding: 1.5rem; text-align: center; color: white; }
    .result-box h2 { color: #f5ffb2; }
    .disease-box { background: #b71c1c; border-radius: 15px; padding: 1.5rem; text-align: center; color: white; }
    .healthy-box { background: #1e3a2f; border-radius: 15px; padding: 1.5rem; text-align: center; color: white; }
    .glass-card { background: rgba(255,255,255,0.85); border-radius: 20px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# =============================================
# 3. LOAD MODEL AND ENCODER
# =============================================
@st.cache_resource
def load_models():
    try:
        model = joblib.load("models/best_crop_model.pkl")
        encoder = joblib.load("models/label_encoder.pkl")
        return model, encoder
    except:
        return None, None

model, encoder = load_models()

# =============================================
# 4. SIDEBAR - NAVIGATION
# =============================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    st.markdown("## 🌿 Navigation")
    
    app_mode = st.radio(
        "Select Feature",
        ["🌾 Crop Recommendation", "🧪 Disease Detection"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### ⚙️ Weather Settings")
    api_key = st.text_input("OpenWeather API Key", type="password", placeholder="Enter your key")
    city = st.text_input("📍 City", value="Delhi")
    
    st.divider()
    st.caption("🌱 Smart Crop Assistant v2.0")

# =============================================
# 5. FEATURE 1: CROP RECOMMENDATION
# =============================================
if app_mode == "🌾 Crop Recommendation":
    st.markdown("# 🌾 Smart Crop Recommendation")
    st.markdown("AI-powered insights to maximize your agricultural yield")

    # Weather Display
    if api_key and city:
        weather = get_weather(city)
        if weather:
            col_w1, col_w2, col_w3, col_w4 = st.columns(4)
            col_w1.metric("🌡️ Temperature", f"{weather['temp']}°C")
            col_w2.metric("💧 Humidity", f"{weather['humidity']}%")
            col_w3.metric("☁️ Condition", weather['description'])
            col_w4.metric("📅 Status", "🌱 Growing" if weather['temp'] > 15 else "❄️ Cool")
    
    st.divider()

    # Input Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌱 Soil & Environmental Parameters")
        
        N = st.slider("🧪 Nitrogen (N)", 0, 140, 50, help="Nitrogen content in soil (ppm)")
        P = st.slider("🧪 Phosphorus (P)", 0, 145, 50)
        K = st.slider("🧪 Potassium (K)", 0, 205, 50)
        temperature = st.slider("🌡️ Temperature (°C)", 0.0, 50.0, 25.0, step=0.5)
        humidity = st.slider("💧 Humidity (%)", 0.0, 100.0, 60.0)
        ph = st.slider("⚗️ Soil pH", 3.5, 10.0, 6.5, step=0.1)
        rainfall = st.slider("🌧️ Rainfall (mm)", 0.0, 300.0, 100.0)
        
        if ph < 5.5 or ph > 8.0:
            st.warning("⚠️ pH outside ideal range (5.5 - 8.0). Consider soil amendments.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Results")
        
        if st.button("🌿 Recommend Crop", use_container_width=True):
            if model is None or encoder is None:
                st.error("❌ Model not loaded. Please train the model first.")
            else:
                features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
                pred_num = model.predict(features)[0]
                crop = encoder.inverse_transform([pred_num])[0]
                
                # Confidence
                confidence = 0.0
                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(features)
                    confidence = float(np.max(probs) * 100)
                
                # Save to database
                save_recommendation(crop, [N, P, K, temperature, humidity, ph, rainfall])
                
                st.markdown(f"""
                <div class="result-box">
                    <h2>🌾 RECOMMENDED</h2>
                    <h1 style="color:#f5ffb2; font-size:3rem;">{crop.upper()}</h1>
                    <p style="font-size:1.2rem;">Confidence: {confidence:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Crop Tips
                tips = {
                    "Rice": "🌾 Requires standing water. Ensure good irrigation.",
                    "Wheat": "🌾 Cool season crop. Needs well-drained soil.",
                    "Maize": "🌽 Warm season crop. High sunlight requirement.",
                    "Cotton": "🌿 Needs long frost-free periods.",
                    "Sugarcane": "🌱 Heavy feeder. Requires deep, rich soil.",
                    "Mango": "🥭 Needs dry season before flowering.",
                    "Banana": "🍌 Requires high humidity and consistent rainfall."
                }
                st.info(f"💡 **Pro Tip**: {tips.get(crop, 'Ensure proper crop rotation and organic fertilizers.')}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# 6. FEATURE 2: DISEASE DETECTION (DEMO MODE)
# =============================================
else:
    st.markdown("# 🧪 Plant Disease Detection")
    st.markdown("Upload a photo of your crop leaf to diagnose diseases and get treatment methods")
    
    st.divider()
    
    uploaded_file = st.file_uploader(
        "📤 Upload a leaf image (JPG, PNG, JPEG)",
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
                    # === DEMO MODE ===
                    import random
                    diseases = ["Bacterial Spot", "Healthy", "Leaf Blight", "Powdery Mildew", "Rust"]
                    result = random.choice(diseases)
                    confidence = round(random.uniform(85.0, 99.0), 1)
                    
                    if result != "Healthy":
                        st.markdown(f"""
                        <div class="disease-box">
                            <h2>⚠️ DISEASE DETECTED</h2>
                            <h1 style="color:#ffcdd2;">{result}</h1>
                            <p>Confidence: {confidence}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        treatments = {
                            "Bacterial Spot": """
                                🧪 **Treatment & Removal Methods:**
                                1. 🗑️ Remove and destroy infected leaves immediately.
                                2. 💧 Avoid overhead watering.
                                3. 🧴 Apply copper-based bactericides weekly.
                                4. 🌱 Rotate crops with non-host plants.
                                5. 🧤 Disinfect gardening tools.
                            """,
                            "Leaf Blight": """
                                🧪 **Treatment:**
                                1. ✂️ Prune infected leaves and branches.
                                2. 🧴 Apply fungicides (chlorothalonil, mancozeb).
                                3. 🌬️ Improve air circulation.
                                4. 🚫 Avoid working with wet plants.
                            """,
                            "Powdery Mildew": """
                                🧪 **Treatment:**
                                1. 🗑️ Remove heavily infected leaves.
                                2. 🧴 Apply sulfur-based fungicides or neem oil.
                                3. ☀️ Ensure 6+ hours of sunlight.
                                4. 💧 Water at base, not on leaves.
                            """,
                            "Rust": """
                                🧪 **Treatment:**
                                1. ✂️ Remove infected leaves.
                                2. 🧴 Apply fungicides (triadimefon, myclobutanil).
                                3. 🌬️ Increase spacing to reduce humidity.
                                4. 🌱 Use disease-free seeds.
                            """
                        }
                        st.info(treatments.get(result, "Consult a local agricultural expert."))
                    else:
                        st.markdown(f"""
                        <div class="healthy-box">
                            <h2>✅ PLANT IS HEALTHY</h2>
                            <h1 style="color:#a5d6a7;">Good News!</h1>
                            <p>Confidence: {confidence}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("🌿 Your plant looks healthy! Continue proper care.")
    
    st.divider()
    st.caption("📌 Demo Mode: Real disease model coming soon!")

# =============================================
# 7. FOOTER
# =============================================
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #5a7a6a; font-size: 0.9rem; border-top: 1px solid #ddd;">
    🌱 <b>Smart Crop Assistant v2.0</b> &nbsp;|&nbsp; Data-driven decisions for sustainable farming
</div>
""", unsafe_allow_html=True)