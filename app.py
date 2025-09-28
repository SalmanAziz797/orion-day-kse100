import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="PSX Elite Scanner - SECURE",
    page_icon="🏆",
    layout="wide"
)

class PSXEliteScanner:
    def __init__(self):
        # ✅ SECURE: Get API key from Streamlit secrets
        try:
            self.api_key = st.secrets["EODHD_API_KEY"]
        except:
            st.error("❌ API key not configured. Please add EODHD_API_KEY to Streamlit secrets.")
            st.stop()
        
        # Elite Strategy Parameters
        self.strategy_params = {
            'rsi_oversold': 26,
            'volume_surge': 2.5,
            'min_confidence': 7.0,
            'target_gain': 2.8,
            'stop_loss': 0.8
        }
        
        # PSX stocks with EODHD tickers
        self.psx_stocks = {
            'HBL': 'HBL.KAR', 'UBL': 'UBL.KAR', 'MCB': 'MCB.KAR',
            'BAHL': 'BAHL.KAR', 'ENGRO': 'ENGRO.KAR', 'EFERT': 'EFERT.KAR', 
            'LUCK': 'LUCK.KAR', 'PSO': 'PSO.KAR', 'OGDC': 'OGDC.KAR',
            'TRG': 'TRG.KAR', 'SYS': 'SYS.KAR'
        }

    def test_api_connection(self):
        """Test EODHD API connection securely"""
        try:
            url = f"https://eodhd.com/api/real-time/HBL.KAR?api_token={self.api_key}&fmt=json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data and 'close' in data
            return False
        except:
            return False

    def fetch_stock_data(self, symbol):
        """Fetch real-time data from EODHD"""
        ticker = self.psx_stocks[symbol]
        url = f"https://eodhd.com/api/real-time/{ticker}?api_token={self.api_key}&fmt=json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'close' in data and data['close']:
                    return {
                        'symbol': symbol,
                        'close': data['close'],
                        'volume': data.get('volume', 0),
                        'high': data.get('high', data['close']),
                        'low': data.get('low', data['close']),
                        'open': data.get('open', data['close']),
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
            return None
        except:
            return None

    def analyze_elite_signal(self, symbol):
        """Apply elite volume power bounce strategy"""
        stock_data = self.fetch_stock_data(symbol)
        if not stock_data:
            return None
        
        # Calculate indicators
        base_volumes = {'HBL': 50000, 'UBL': 45000, 'MCB': 30000, 'TRG': 52000}
        base_vol = base_volumes.get(symbol, 40000)
        volume_ratio = stock_data['volume'] / base_vol if base_vol > 0 else 1
        
        price_change = stock_data['close'] - stock_data['open']
        change_percent = (price_change / stock_data['open']) * 100 if stock_data['open'] > 0 else 0
        rsi = max(0, min(100, 50 - change_percent))
        
        bullish_candle = stock_data['close'] > stock_data['open']
        daily_range = stock_data['high'] - stock_data['low']
        price_strength = (stock_data['close'] - stock_data['low']) / daily_range if daily_range > 0 else 0.5
        
        # 🎯 Elite Strategy Conditions
        if (rsi < self.strategy_params['rsi_oversold'] and 
            volume_ratio > self.strategy_params['volume_surge'] and
            bullish_candle and price_strength > 0.6):
            
            # Calculate confidence
            rsi_factor = (self.strategy_params['rsi_oversold'] - rsi) / 8
            volume_factor = min(volume_ratio / 2.0, 2.5)
            confidence = 6.0 + (rsi_factor * 2.5) + (volume_factor - 1) + 0.8
            confidence = min(max(confidence, 0), 10)
            
            if confidence >= self.strategy_params['min_confidence']:
                target_price = stock_data['close'] * (1 + self.strategy_params['target_gain'] / 100)
                stop_loss = stock_data['close'] * (1 - self.strategy_params['stop_loss'] / 100)
                
                return {
                    'symbol': symbol,
                    'price': stock_data['close'],
                    'rsi': rsi,
                    'volume_ratio': volume_ratio,
                    'confidence': round(confidence, 1),
                    'target': round(target_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'signal': 'ELITE_BUY',
                    'reason': f'Oversold bounce (RSI: {rsi:.1f}, Volume: {volume_ratio:.1f}x)',
                    'time': stock_data['timestamp']
                }
        return None

def main():
    st.title("🏆 PSX Elite Scanner - SECURE")
    st.markdown("### **Protected Deployment**")
    
    scanner = PSXEliteScanner()
    
    # API Status Check
    if scanner.test_api_connection():
        st.success("✅ EODHD API Connected Securely")
        
        # Stock Selection
        selected_stocks = st.multiselect(
            "Select PSX Stocks:",
            options=list(scanner.psx_stocks.keys()),
            default=['HBL', 'UBL', 'TRG'],
        )
        
        if st.button("🚀 SCAN FOR ELITE SIGNALS", type="primary"):
            if not selected_stocks:
                st.warning("Please select stocks to scan")
            else:
                signals = []
                progress_bar = st.progress(0)
                
                for i, symbol in enumerate(selected_stocks):
                    signal = scanner.analyze_elite_signal(symbol)
                    if signal:
                        signals.append(signal)
                    progress_bar.progress((i + 1) / len(selected_stocks))
                    time.sleep(0.5)
                
                # Display Results
                if signals:
                    st.success(f"🎯 Found {len(signals)} Elite Signals!")
                    for signal in signals:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.subheader(f"🏆 {signal['symbol']} - BUY")
                                st.info(signal['reason'])
                            with col2:
                                st.metric("Price", f"₨{signal['price']:.2f}")
                                st.metric("RSI", f"{signal['rsi']:.1f}")
                            with col3:
                                st.metric("Target", f"₨{signal['target']:.2f}")
                                st.metric("Confidence", f"{signal['confidence']}/10")
                            st.progress(signal['confidence'] / 10)
                else:
                    st.info("No elite signals found")
    else:
        st.error("❌ API Connection Failed - Check Secrets Configuration")

if __name__ == "__main__":
    main()
