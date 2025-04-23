pip install folium
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests

# Title and description
st.title("Disaster Resilience Alert System")
st.write("""
Access real-time weather and earthquake data, visualize disaster-prone areas, and receive alerts directly from this dashboard.
""")

# User Inputs for Location
st.sidebar.header("User Settings")
location = st.sidebar.text_input("Enter your location (City, State):", "Chalakkudy, KL")

# Weather API Section
st.header("Weather Data")
def fetch_weather_data(location, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "Temperature (K)": data["main"]["temp"],
            "Humidity (%)": data["main"]["humidity"],
            "Rainfall (mm)": data.get("rain", {}).get("1h", 0)
        }
    else:
        st.error("Failed to fetch weather data.")
        return {}

weather_api_key = "b28b939a45cb011d435a29d520e05aba"  # Replace with your OpenWeatherMap API Key
weather_data = fetch_weather_data(location, weather_api_key)
st.write(pd.DataFrame([weather_data]))

# Earthquake API Section
st.header("Earthquake Data")
def fetch_earthquake_data():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": "2025-04-20",
        "endtime": "2025-04-23",
        "minmagnitude": 4.0
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["features"]
    else:
        st.error("Failed to fetch earthquake data.")
        return []

earthquake_data = fetch_earthquake_data()
earthquake_df = pd.DataFrame([{
    "Magnitude": event['properties']['mag'],
    "Location": event['properties']['place']
} for event in earthquake_data])
st.write(earthquake_df)

# Earthquake Map Section
st.header("Earthquake Map")
disaster_map = folium.Map(location=[10.3, 76.2], zoom_start=5)  # Adjust map center coordinates
for event in earthquake_data:
    latitude = event['geometry']['coordinates'][1]
    longitude = event['geometry']['coordinates'][0]
    magnitude = event['properties']['mag']
    folium.Marker(
        location=[latitude, longitude],
        popup=f"Magnitude: {magnitude}",
        icon=folium.Icon(color="red")
    ).add_to(disaster_map)
folium_static(disaster_map)

# Display Alerts
st.header("Alerts Section")
if weather_data.get("Rainfall (mm)", 0) > 50:
    st.warning(f"🚨 Alert: Heavy rainfall detected in {location}. Take precautions!")
if earthquake_df["Magnitude"].max() >= 5.0:
    st.warning(f"🚨 Alert: High-magnitude earthquake detected in {location}. Stay safe!")
