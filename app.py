import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime
import time

st.set_page_config(
    page_title="PSX Scanner - DEBUG",
    page_icon="🐛",
    layout="wide"
)

class PSXDebugScanner:
    def __init__(self):
        try:
            self.api_key = st.secrets["EODHD_API_KEY"]
            st.success(f"✅ API Key loaded: {self.api_key[:10]}...")
        except:
            st.error("❌ API key not configured. Please add EODHD_API_KEY to Streamlit secrets.")
            st.stop()
        
        # Test with just 5 major stocks first
        self.test_symbols = ['HBL', 'UBL', 'MCB', 'PSO', 'OGDC']

    def test_api_connection(self, symbol):
        """Test if we can get data for a single stock"""
        ticker = f"{symbol}.KAR"
        url = f"https://eodhd.com/api/real-time/{ticker}?api_token={self.api_key}&fmt=json"
        
        st.write(f"🔍 Testing {symbol} -> {ticker}")
        st.write(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            st.write(f"Response Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                st.write(f"Raw Response: {data}")
                
                if data and 'close' in data and data['close']:
                    return {
                        'symbol': symbol,
                        'close': data['close'],
                        'volume': data.get('volume', 0),
                        'status': 'SUCCESS'
                    }
                else:
                    return {'symbol': symbol, 'status': 'NO_DATA', 'response': data}
            else:
                return {'symbol': symbol, 'status': f'HTTP_ERROR_{response.status_code}'}
                
        except Exception as e:
            return {'symbol': symbol, 'status': f'EXCEPTION: {str(e)}'}

def main():
    st.title("🐛 PSX Scanner - DEBUG Mode")
    st.markdown("### Testing API Connection and Data Availability")
    
    scanner = PSXDebugScanner()
    
    st.info("Testing API connection with 5 major PSX stocks...")
    
    if st.button("🚀 RUN API DIAGNOSTIC", type="primary"):
        results = []
        
        for symbol in scanner.test_symbols:
            with st.expander(f"Testing {symbol}", expanded=True):
                result = scanner.test_api_connection(symbol)
                results.append(result)
        
        # Summary
        st.markdown("---")
        st.subheader("📊 Diagnostic Results")
        
        success_count = len([r for r in results if r['status'] == 'SUCCESS'])
        
        if success_count > 0:
            st.success(f"✅ {success_count}/5 stocks returned data!")
            st.info("The API is working! The issue might be with the other stock symbols.")
        else:
            st.error("❌ No stocks returned data. Possible issues:")
            st.write("1. **API Key invalid** or expired")
            st.write("2. **Wrong symbol format** (.KAR might not be correct)")
            st.write("3. **EODHD doesn't have PSX data** on free plan")
            st.write("4. **API endpoint changed**")
            
            # Show detailed results
            for result in results:
                st.write(f"- {result['symbol']}: {result['status']}")

if __name__ == "__main__":
    main()
