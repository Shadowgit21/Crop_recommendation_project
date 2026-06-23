<<<<<<< HEAD

import streamlit as st
import pickle
import numpy as np
import tensorflow as tf
from PIL import Image
import pandas as pd

# 🎨 Page config
st.set_page_config(page_title="Crop Predictor", layout="centered")

page = st.sidebar.selectbox("Select Page", ["Crop Recommendation", "Disease Detection"])

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    </style>
""", unsafe_allow_html=True)


# 🌾 Crop Page
if page == "Crop Recommendation":

    model = pickle.load(open("model/crop_model.pkl", "rb"))

    st.markdown("""
    <h1 style='text-align: center; color: #2E8B57; font-size:42px;'>
    🌾 Smart Crop Recommendation System
    </h1>

    <p style='text-align: center; font-size:18px;'>
    AI-powered system to recommend the best crop based on soil & climate 🌱
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### 🌱 AI-based Crop Prediction Tool")
    st.markdown("---")

    st.info("👉 Enter soil nutrients and weather conditions to get the best crop recommendation")

    st.markdown("### 🌱 Enter soil & climate conditions")
    st.markdown("---")

    st.warning("⚠️ Enter all values and click 'Predict Crop' to see result")
    st.subheader("📊 Input Parameters")

    # Inputs
    st.markdown("## 🌱 Soil Parameters")
    N = st.number_input("Nitrogen", min_value=0.0)
    P = st.number_input("Phosphorus", min_value=0.0)
    K = st.number_input("Potassium", min_value=0.0)

    st.markdown("## 🌦️ Climate Parameters")
    temperature = st.number_input("Temperature (°C)")
    humidity = st.number_input("Humidity (%)")
    ph = st.number_input("pH")
    rainfall = st.number_input("Rainfall (mm)")

    # Prediction
    if st.button("🌾 Predict Crop"):
        data = [[N, P, K, temperature, humidity, ph, rainfall]]
        data_df = pd.DataFrame(data, columns=['N','P','K','temperature','humidity','ph','rainfall'])
        prediction = model.predict(data_df)

        st.markdown(f"""
        <div style='background-color:#e6ffe6;padding:20px;border-radius:10px;text-align:center'>
            <h2 style='color:#2E8B57;'>🌱 Recommended Crop</h2>
            <h1 style='color:#000;'>{prediction[0].upper()}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Developed by Subrato Dutta 🚀")
    st.markdown("---")
    st.markdown("👨‍💻 Built with Machine Learning + Streamlit")


# 🌿 Disease Page
elif page == "Disease Detection":

    disease_model = tf.keras.models.load_model("disease_model/disease_model.h5")

    st.header("🌿 Plant Disease Detection")

    uploaded_file = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        img = image.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = disease_model.predict(img_array)
        predicted_class = np.argmax(prediction)

        class_names = ['Pepper__bell__Bacterial_spot', 'Pepper__bell__healthy']

        st.success(f"🌿 Predicted Disease: {class_names[predicted_class]}")
        
        
import requests
import streamlit as st

api_key = "51b0d245435e2d19c8e875523c3d83f5"

st.title("🌦 Weather + Crop System")

city = st.text_input("Enter City Name")

if city:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    if data["cod"] == 200:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        st.success("Weather Data Fetched ✅")
        st.write(f"🌡 Temperature: {temp} °C")
        st.write(f"💧 Humidity: {humidity} %")

    else:
=======

import streamlit as st
import pickle
import numpy as np
import tensorflow as tf
from PIL import Image
import pandas as pd

# 🎨 Page config
st.set_page_config(page_title="Crop Predictor", layout="centered")

page = st.sidebar.selectbox("Select Page", ["Crop Recommendation", "Disease Detection"])

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    </style>
""", unsafe_allow_html=True)


# 🌾 Crop Page
if page == "Crop Recommendation":

    model = pickle.load(open("model/crop_model.pkl", "rb"))

    st.markdown("""
    <h1 style='text-align: center; color: #2E8B57; font-size:42px;'>
    🌾 Smart Crop Recommendation System
    </h1>

    <p style='text-align: center; font-size:18px;'>
    AI-powered system to recommend the best crop based on soil & climate 🌱
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### 🌱 AI-based Crop Prediction Tool")
    st.markdown("---")

    st.info("👉 Enter soil nutrients and weather conditions to get the best crop recommendation")

    st.markdown("### 🌱 Enter soil & climate conditions")
    st.markdown("---")

    st.warning("⚠️ Enter all values and click 'Predict Crop' to see result")
    st.subheader("📊 Input Parameters")

    # Inputs
    st.markdown("## 🌱 Soil Parameters")
    N = st.number_input("Nitrogen", min_value=0.0)
    P = st.number_input("Phosphorus", min_value=0.0)
    K = st.number_input("Potassium", min_value=0.0)

    st.markdown("## 🌦️ Climate Parameters")
    temperature = st.number_input("Temperature (°C)")
    humidity = st.number_input("Humidity (%)")
    ph = st.number_input("pH")
    rainfall = st.number_input("Rainfall (mm)")

    # Prediction
    if st.button("🌾 Predict Crop"):
        data = [[N, P, K, temperature, humidity, ph, rainfall]]
        data_df = pd.DataFrame(data, columns=['N','P','K','temperature','humidity','ph','rainfall'])
        prediction = model.predict(data_df)

        st.markdown(f"""
        <div style='background-color:#e6ffe6;padding:20px;border-radius:10px;text-align:center'>
            <h2 style='color:#2E8B57;'>🌱 Recommended Crop</h2>
            <h1 style='color:#000;'>{prediction[0].upper()}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Developed by Subrato Dutta 🚀")
    st.markdown("---")
    st.markdown("👨‍💻 Built with Machine Learning + Streamlit")


# 🌿 Disease Page
elif page == "Disease Detection":

    disease_model = tf.keras.models.load_model("disease_model/disease_model.h5")

    st.header("🌿 Plant Disease Detection")

    uploaded_file = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        img = image.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = disease_model.predict(img_array)
        predicted_class = np.argmax(prediction)

        class_names = ['Pepper__bell__Bacterial_spot', 'Pepper__bell__healthy']

        st.success(f"🌿 Predicted Disease: {class_names[predicted_class]}")
        
        
import requests
import streamlit as st

api_key = "51b0d245435e2d19c8e875523c3d83f5"

st.title("🌦 Weather + Crop System")

city = st.text_input("Enter City Name")

if city:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    if data["cod"] == 200:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        st.success("Weather Data Fetched ✅")
        st.write(f"🌡 Temperature: {temp} °C")
        st.write(f"💧 Humidity: {humidity} %")

    else:
>>>>>>> f1268ec (Crop recommendation project)
        st.error("City not found ❌")