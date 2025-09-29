import streamlit as st
import requests

st.set_page_config(
    page_title="API Diagnostic",
    page_icon="🔧",
    layout="wide"
)

def test_api_directly():
    """Test the API endpoint directly and show raw response"""
    
    api_key = st.secrets["EODHD_API_KEY"]
    
    # Test the exact endpoint you provided
    url = "https://eodhd.com/api/exchange-symbol-list/KAR"
    params = {
        'api_token': api_key,
        'fmt': 'json'
    }
    
    st.write("🔧 **Testing API Endpoint:**")
    st.code(f"URL: {url}")
    st.code(f"Params: {params}")
    
    try:
        with st.spinner("Calling API..."):
            response = requests.get(url, params=params, timeout=15)
        
        st.write("📡 **Response Details:**")
        st.write(f"Status Code: {response.status_code}")
        st.write(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            st.success("✅ API Call Successful!")
            st.write(f"Data Type: {type(data)}")
            st.write(f"Data Length: {len(data) if data else 0}")
            
            if data and len(data) > 0:
                st.write("📊 **Sample Data (first 5 items):**")
                for i, item in enumerate(data[:5]):
                    st.write(f"{i+1}. {item}")
            else:
                st.warning("⚠️ API returned empty data")
                
        else:
            st.error(f"❌ API Error: {response.status_code}")
            st.write(f"Response Text: {response.text}")
            
    except Exception as e:
        st.error(f"💥 Exception: {str(e)}")

def test_alternative_endpoints():
    """Test alternative API endpoints"""
    
    api_key = st.secrets["EODHD_API_KEY"]
    endpoints = [
        "https://eodhd.com/api/exchange-symbol-list/PSX",
        "https://eodhd.com/api/exchange-symbol-list/PAK", 
        "https://eodhd.com/api/exchanges/KAR",
        "https://eodhd.com/api/symbol-search/HBL.KAR"
    ]
    
    st.write("🔄 **Testing Alternative Endpoints:**")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, params={'api_token': api_key, 'fmt': 'json'}, timeout=10)
            st.write(f"{endpoint} -> Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ Works! Found {len(data) if data else 0} items")
        except Exception as e:
            st.write(f"{endpoint} -> Error: {str(e)}")

# Main app
st.title("🔧 EODHD API Diagnostic")
st.markdown("### Testing API endpoints to find working PSX data")

st.warning("Let's figure out why the API call is failing")

if st.button("🧪 RUN API DIAGNOSTIC", type="primary"):
    test_api_directly()
    
if st.button("🔄 TEST ALTERNATIVE ENDPOINTS"):
    test_alternative_endpoints()
