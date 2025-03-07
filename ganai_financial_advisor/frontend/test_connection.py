import streamlit as st
import requests
import os
import json

st.title("Backend Connection Test")

# Get backend URL from different sources
default_backend_url = "http://127.0.0.1:5001/api/predict"

# Try different sources for the backend URL
sources = {
    "Environment Variable": os.environ.get("BACKEND_URL", None),
    "Streamlit Secrets": None
}

# Try to get from Streamlit secrets
try:
    sources["Streamlit Secrets"] = st.secrets.get("BACKEND_URL", None)
except Exception:
    pass

# Display all sources
st.write("### Backend URL Sources")
for source_name, source_value in sources.items():
    if source_value:
        st.success(f"{source_name}: {source_value}")
    else:
        st.error(f"{source_name}: Not found")

# Determine the actual URL to use (prioritize secrets, then env var, then default)
raw_backend_url = None
if sources["Streamlit Secrets"]:
    raw_backend_url = sources["Streamlit Secrets"]
    st.info("Using URL from Streamlit Secrets")
elif sources["Environment Variable"]:
    raw_backend_url = sources["Environment Variable"]
    st.info("Using URL from Environment Variable")
else:
    raw_backend_url = default_backend_url
    st.warning(f"Using default URL: {default_backend_url}")

# Extract the base URL (remove the endpoint path if present)
if '/api/' in raw_backend_url:
    BACKEND_BASE_URL = raw_backend_url.split('/api/')[0]
else:
    BACKEND_BASE_URL = raw_backend_url

if BACKEND_BASE_URL.endswith('/'):
    BACKEND_BASE_URL = BACKEND_BASE_URL[:-1]

st.write(f"Extracted base URL: {BACKEND_BASE_URL}")

# Manual override option
st.write("### Manual Override")
manual_url = st.text_input("Enter backend URL manually (leave empty to use detected URL):", 
                          placeholder="https://your-backend-url.com")

if manual_url:
    BACKEND_BASE_URL = manual_url
    if BACKEND_BASE_URL.endswith('/'):
        BACKEND_BASE_URL = BACKEND_BASE_URL[:-1]
    st.write(f"Using manually entered URL: {BACKEND_BASE_URL}")

# Test health endpoint
st.write("### Connection Tests")
if st.button("Test Health Endpoint"):
    try:
        health_url = f"{BACKEND_BASE_URL}/health"
        st.write(f"Connecting to: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            st.success(f"Successfully connected to health endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to health endpoint: {str(e)}")

# Test test endpoint
if st.button("Test Simple Endpoint"):
    try:
        test_url = f"{BACKEND_BASE_URL}/test"
        st.write(f"Connecting to: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            st.success(f"Successfully connected to test endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to test endpoint: {str(e)}")

# Test API endpoint
if st.button("Test API Endpoint"):
    try:
        api_url = f"{BACKEND_BASE_URL}/api/predict"
        st.write(f"Connecting to: {api_url}")
        
        response = requests.post(
            api_url, 
            json={"input_data": "Test query"}, 
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(f"Successfully connected to API endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API endpoint: {str(e)}")

# Environment information
with st.expander("Environment Information"):
    st.write("Environment Variables:")
    env_vars = {}
    for key in sorted(os.environ.keys()):
        if not key.startswith(('_', 'PYTHON')):  # Filter out some system variables
            value = '*' * 8 if 'KEY' in key or 'SECRET' in key else os.environ[key]
            env_vars[key] = value
    
    st.json(env_vars)
    
    st.write("Note: If you don't see BACKEND_URL in the environment variables, it means it's not set in your Streamlit Cloud deployment.") 