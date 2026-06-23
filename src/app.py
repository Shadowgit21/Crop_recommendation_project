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
from dotenv import load_dotenv

# =============================================
# 1. DATABASE FUNCTIONS (built-in)
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
st.set_page_config(page_title="🌾 Smart Crop Assistant", page_icon="🌱", layout="wide")
init_db()

# =============================================
# 4. CUSTOM CSS
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
# 5. LOAD MODEL AND ENCODER
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
# 6. SIDEBAR - NAVIGATION
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
# 7. FEATURE 1: CROP RECOMMENDATION
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

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌱 Soil & Environmental Parameters")
        N = st.slider("🧪 Nitrogen (N)", 0, 140, 50)
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
                confidence = 0.0
                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(features)
                    confidence = float(np.max(probs) * 100)
                save_recommendation(crop, [N, P, K, temperature, humidity, ph, rainfall])
                st.markdown(f"""
                <div class="result-box">
                    <h2>🌾 RECOMMENDED</h2>
                    <h1 style="color:#f5ffb2; font-size:3rem;">{crop.upper()}</h1>
                    <p style="font-size:1.2rem;">Confidence: {confidence:.1f}%</p>
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
                st.info(f"💡 **Pro Tip**: {tips.get(crop, 'Ensure proper crop rotation and organic fertilizers.')}")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# 8. FEATURE 2: DISEASE DETECTION (DEMO)
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
                            <h2>✅ PLANT IS HEALTHY</h2>
                            <h1 style="color:#a5d6a7;">Good News!</h1>
                            <p>Confidence: {confidence}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("🌿 Your plant looks healthy!")
    st.divider()
    st.caption("📌 Demo Mode: Real model coming soon!")

# =============================================
# 9. FOOTER
# =============================================
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #5a7a6a; font-size: 0.9rem; border-top: 1px solid #ddd;">
    🌱 <b>Smart Crop Assistant v2.0</b> &nbsp;|&nbsp; Data-driven decisions for sustainable farming
</div>
""", unsafe_allow_html=True)