import streamlit as st
import requests

st.set_page_config(
    page_title="EODHD Free Tier Test",
    page_icon="🧪",
    layout="wide"
)

def test_basic_eod(symbol):
    """Test if basic EOD endpoint works"""
    url = f"https://eodhd.com/api/eod/{symbol}"
    params = {
        'api_token': st.secrets["EODHD_API_KEY"],
        'fmt': 'json',
        'from': '2024-01-01',
        'to': '2024-01-05'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.status_code, response.json() if response.status_code == 200 else None
    except Exception as e:
        return f"Error: {str(e)}", None

# Main test
st.title("🧪 EODHD Free Tier Reality Check")
st.markdown("### **Testing what ACTUALLY works with your free plan**")

st.warning("🚨 **Truth Bomb:** Let's see what you're actually paying for")

test_symbols = [
    'HBL.KAR', 'AAPL.US', 'RELIANCE.BSE', 'TATA.BSE',
    'MSFT.US', 'INFY.BSE', 'TCS.BSE'
]

if st.button("🔍 TEST WHAT ACTUALLY WORKS", type="primary"):
    
    results = []
    
    for symbol in test_symbols:
        with st.expander(f"Testing {symbol}", expanded=True):
            status, data = test_basic_eod(symbol)
            
            st.write(f"**Status:** {status}")
            
            if status == 200 and data:
                st.success(f"✅ **WORKS!** Got {len(data)} days of data")
                if data:
                    st.json(data[0])  # Show first data point
            elif status == 402:
                st.error("❌ **402 PAYMENT REQUIRED** - They lied about 'free'")
            elif status == 403:
                st.error("❌ **403 FORBIDDEN** - Not in your plan")
            else:
                st.error(f"❌ **FAILED:** {status}")
    
    st.markdown("---")
    st.subheader("🎯 **BOTTOM LINE:**")
    
    st.error("""
    **If most tests show 402 errors:**
    - They're lying about "free EOD data"
    - Your API key is practically useless
    - You need to find a different data provider
    """)
    
    st.info("""
    **Next Steps:**
    1. **Contact their support** and ask why basic EOD endpoints return 402
    2. **Check if any stocks actually work** (maybe only .US stocks?)
    3. **Consider alternative data providers** that are actually honest
    """)
