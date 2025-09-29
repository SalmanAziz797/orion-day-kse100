import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="PSX Scanner - Yahoo Finance",
    page_icon="🎲",
    layout="wide"
)

class YahooPSXScanner:
    def __init__(self):
        self.strategy_params = {
            'rsi_oversold': 26,
            'volume_surge': 2.5,
            'min_confidence': 7.0,
            'target_gain': 2.8,
            'stop_loss': 0.8
        }
        
        # Yahoo Finance uses .PA for Pakistan stocks
        self.psx_symbols = [
            'HBL.PA', 'UBL.PA', 'MCB.PA', 'BAHL.PA', 'ENGRO.PA',
            'EFERT.PA', 'LUCK.PA', 'PSO.PA', 'OGDC.PA', 'PPL.PA',
            'TRG.PA', 'SYS.PA', 'FFC.PA', 'HUBC.PA', 'KEL.PA',
            'BAFL.PA', 'ATRL.PA', 'POL.PA', 'SNGP.PA'
        ]
        
        self.base_volumes = {
            'HBL.PA': 50000, 'UBL.PA': 45000, 'MCB.PA': 30000,
            'BAHL.PA': 25000, 'ENGRO.PA': 60000, 'EFERT.PA': 40000,
            'LUCK.PA': 35000, 'PSO.PA': 55000, 'OGDC.PA': 48000,
            'PPL.PA': 52000, 'TRG.PA': 52000, 'SYS.PA': 38000,
            'FFC.PA': 42000, 'HUBC.PA': 40000, 'KEL.PA': 30000,
            'BAFL.PA': 35000, 'ATRL.PA': 35000, 'POL.PA': 45000,
            'SNGP.PA': 38000, 'DEFAULT': 30000
        }

    def fetch_yahoo_data(self, symbol):
        """Fetch data from Yahoo Finance - let's see what we get!"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")
            
            if not hist.empty and len(hist) > 0:
                latest = hist.iloc[-1]
                
                # Debug: Show what we actually got
                debug_info = {
                    'symbol': symbol,
                    'close': latest['Close'],
                    'volume': latest['Volume'],
                    'high': latest['High'],
                    'low': latest['Low'],
                    'open': latest['Open'],
                    'date': latest.name.strftime('%Y-%m-%d'),
                    'data_points': len(hist),
                    'success': True
                }
                return debug_info
            else:
                return {'symbol': symbol, 'success': False, 'error': 'No data returned'}
                
        except Exception as e:
            return {'symbol': symbol, 'success': False, 'error': str(e)}

    def calculate_rsi(self, prices, window=14):
        """Calculate RSI - let's hope the prices are somewhat accurate"""
        if len(prices) < window + 1:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = pd.Series(gains).rolling(window=window).mean()
        avg_losses = pd.Series(losses).rolling(window=window).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50

    def fetch_historical_data(self, symbol):
        """Fetch historical data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2mo")
            return hist['Close'].tolist() if not hist.empty else None
        except:
            return None

    def analyze_stock(self, symbol):
        """Apply elite strategy using whatever data Yahoo gives us"""
        try:
            # Get whatever data Yahoo has
            data = self.fetch_yahoo_data(symbol)
            
            # Show exactly what we got
            st.write(f"**{symbol} Data:** Close: {data.get('close', 'N/A')}, Volume: {data.get('volume', 'N/A')}")
            
            if not data['success']:
                return None, data['error']
            
            # Validate data quality
            if data['close'] <= 0 or data['volume'] <= 0:
                return None, "Suspicious data values"
            
            # Get historical data
            historical_prices = self.fetch_historical_data(symbol)
            if not historical_prices or len(historical_prices) < 15:
                return None, "Insufficient history"
            
            # Calculate RSI with whatever data we have
            rsi = self.calculate_rsi(historical_prices)
            
            base_vol = self.base_volumes.get(symbol, self.base_volumes['DEFAULT'])
            volume_ratio = data['volume'] / base_vol if base_vol > 0 else 1
            
            bullish_candle = data['close'] > data['open']
            
            daily_range = data['high'] - data['low']
            price_strength = (data['close'] - data['low']) / daily_range if daily_range > 0 else 0.5
            
            # 🎯 ELITE STRATEGY (with questionable data!)
            if (rsi < self.strategy_params['rsi_oversold'] and 
                volume_ratio > self.strategy_params['volume_surge'] and
                bullish_candle and price_strength > 0.6):
                
                rsi_factor = (self.strategy_params['rsi_oversold'] - rsi) / 8
                volume_factor = min(volume_ratio / 2.0, 2.5)
                confidence = 6.0 + (rsi_factor * 2.5) + (volume_factor - 1) + 0.8
                confidence = min(max(confidence, 0), 10)
                
                if confidence >= self.strategy_params['min_confidence']:
                    target_price = data['close'] * (1 + self.strategy_params['target_gain'] / 100)
                    stop_loss = data['close'] * (1 - self.strategy_params['stop_loss'] / 100)
                    
                    signal = {
                        'symbol': symbol.replace('.PA', ''),
                        'price': data['close'],
                        'rsi': round(rsi, 1),
                        'volume_ratio': round(volume_ratio, 1),
                        'confidence': round(confidence, 1),
                        'target': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'signal': 'ELITE_BUY',
                        'reason': f'Oversold bounce (RSI: {rsi:.1f}, Volume: {volume_ratio:.1f}x)',
                        'date': data['date'],
                        'data_quality': 'YAHOO_FINANCE'  # Warning label!
                    }
                    return signal, "Signal found (Yahoo data)"
            
            return None, "Conditions not met"
            
        except Exception as e:
            return None, f"Error: {str(e)}"

    def run_scan(self):
        """Run scan and show exactly what data we're getting"""
        st.info(f"🔍 Testing {len(self.psx_symbols)} PSX stocks via Yahoo Finance...")
        st.warning("⚠️ **DATA QUALITY UNKNOWN** - This is an experiment!")
        
        signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        
        for i, symbol in enumerate(self.psx_symbols):
            status_text.text(f"Testing {symbol}... ({i+1}/{len(self.psx_symbols)})")
            
            # Show raw data for each stock
            with st.expander(f"📊 {symbol} Raw Data", expanded=False):
                signal, reason = self.analyze_stock(symbol)
            
            if signal:
                signals.append(signal)
                results.append(f"✅ {symbol}: {reason}")
            else:
                results.append(f"❌ {symbol}: {reason}")
            
            progress_bar.progress((i + 1) / len(self.psx_symbols))
            time.sleep(1)  # Be nice to Yahoo
            
        return signals, results

def main():
    st.title("🎲 PSX Scanner - Yahoo Finance Experiment")
    st.markdown("### **Let's See What Garbage Data We Get!** 🗑️")
    
    st.error("""
    **WARNING:** Yahoo Finance PSX data is known to be:
    - ❌ Inaccurate prices
    - ❌ Wrong volumes  
    - ❌ Delayed updates
    - ❌ Missing stocks
    """)
    
    st.info("💡 **This is just for testing - don't trade with this data!**")
    
    scanner = YahooPSXScanner()
    
    if st.button("🚀 RUN YAHOO FINANCE EXPERIMENT", type="primary"):
        signals, results = scanner.run_scan()
        
        st.markdown("---")
        
        if signals:
            st.success(f"🎲 **FOUND {len(signals)} 'SIGNALS' (with questionable data)**")
            
            for signal in signals:
                with st.container():
                    st.markdown("---")
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.subheader(f"🎰 {signal['symbol']} - 'BUY'")
                        st.warning(f"**Data Source:** {signal['data_quality']}")
                        st.info(f"**Reason:** {signal['reason']}")
                        st.caption(f"**Date:** {signal['date']}")
                        
                    with col2:
                        st.metric("Price", f"₨{signal['price']:.2f}")
                        st.metric("RSI", f"{signal['rsi']:.1f}")
                        st.metric("Volume", f"{signal['volume_ratio']:.1f}x")
                        
                    with col3:
                        st.metric("Target", f"₨{signal['target']:.2f}")
                        st.metric("Stop Loss", f"₨{signal['stop_loss']:.2f}")
                        st.metric("Confidence", f"{signal['confidence']}/10")
                    
                    st.progress(signal['confidence'] / 10)
        else:
            st.info("🤷 No signals found with Yahoo data")
        
        with st.expander("📋 Detailed Results (The Ugly Truth)"):
            for result in results:
                st.write(result)

if __name__ == "__main__":
    main()
