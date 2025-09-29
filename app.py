import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="PSX Stock Discovery",
    page_icon="🔍",
    layout="wide"
)

class PSXStockDiscovery:
    def __init__(self):
        try:
            self.api_key = st.secrets["EODHD_API_KEY"]
            st.success("✅ API Key loaded")
        except:
            st.error("❌ API key not configured")
            st.stop()

    def get_all_psx_tickers(self):
        """Get ALL PSX tickers from EODHD"""
        url = f"https://eodhd.com/api/exchange-symbol-list/KAR"
        params = {
            'api_token': self.api_key,
            'fmt': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data
            return None
        except Exception as e:
            st.error(f"❌ Failed to fetch tickers: {str(e)}")
            return None

    def test_stock_data(self, symbol):
        """Test if a stock has EOD data"""
        url = f"https://eodhd.com/api/eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'fmt': 'json',
            'from': '2024-01-01',
            'to': '2024-01-05'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data and len(data) > 0
            return False
        except:
            return False

def main():
    st.title("🔍 PSX Stock Discovery Tool")
    st.markdown("### Finding which PSX stocks actually have data on EODHD")
    
    discoverer = PSXStockDiscovery()
    
    if st.button("🚀 DISCOVER PSX STOCKS WITH DATA", type="primary"):
        
        # Step 1: Get all tickers
        with st.spinner("📋 Fetching all PSX tickers from EODHD..."):
            all_tickers = discoverer.get_all_psx_tickers()
            
        if not all_tickers:
            st.error("Failed to get ticker list")
            return
            
        st.success(f"✅ Found {len(all_tickers)} total PSX symbols")
        
        # Show sample of what we got
        with st.expander("📊 Sample of PSX Symbols Found", expanded=True):
            sample_df = pd.DataFrame(all_tickers[:10])  # Show first 10
            st.dataframe(sample_df)
        
        # Step 2: Test data availability for first 20 stocks
        st.info("🧪 Testing data availability for first 20 stocks...")
        
        tested_stocks = []
        progress_bar = st.progress(0)
        
        for i, ticker_info in enumerate(all_tickers[:20]):  # Test first 20
            symbol = f"{ticker_info['Code']}.KAR"
            
            with st.expander(f"Testing {symbol}", expanded=False):
                st.write(f"**Name:** {ticker_info.get('Name', 'N/A')}")
                st.write(f"**Country:** {ticker_info.get('Country', 'N/A')}")
                st.write(f"**Exchange:** {ticker_info.get('Exchange', 'N/A')}")
                
                has_data = discoverer.test_stock_data(symbol)
                if has_data:
                    st.success("✅ HAS EOD DATA")
                    tested_stocks.append({
                        'symbol': symbol,
                        'name': ticker_info.get('Name', ''),
                        'has_data': True
                    })
                else:
                    st.error("❌ NO EOD DATA")
                    tested_stocks.append({
                        'symbol': symbol,
                        'name': ticker_info.get('Name', ''),
                        'has_data': False
                    })
            
            progress_bar.progress((i + 1) / 20)
        
        # Step 3: Show results
        st.markdown("---")
        st.subheader("🎯 DISCOVERY RESULTS")
        
        stocks_with_data = [s for s in tested_stocks if s['has_data']]
        stocks_no_data = [s for s in tested_stocks if not s['has_data']]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Stocks WITH Data", len(stocks_with_data))
        with col2:
            st.metric("Stocks NO Data", len(stocks_no_data))
        
        if stocks_with_data:
            st.success("🎉 FOUND STOCKS WITH DATA!")
            st.write("**Working stocks:**")
            for stock in stocks_with_data:
                st.write(f"- {stock['symbol']} : {stock['name']}")
            
            st.info("💡 **Next step:** We can now build the scanner using these verified stocks!")
        else:
            st.error("😞 No stocks returned data. There might be an issue with the EODHD API or your plan.")

if __name__ == "__main__":
    main()
