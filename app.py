import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="PSX Manual Elite Scanner",
    page_icon="🎯",
    layout="wide"
)

class ManualPSXScanner:
    def __init__(self):
        self.strategy_params = {
            'rsi_oversold': 26,
            'volume_surge': 2.5, 
            'min_confidence': 7.0,
            'target_gain': 2.8,
            'stop_loss': 0.8
        }
        
        # Base volumes for volume ratio calculation
        self.base_volumes = {
            'HBL': 50000, 'UBL': 45000, 'MCB': 30000, 'BAHL': 25000,
            'ENGRO': 60000, 'EFERT': 40000, 'LUCK': 35000, 'PSO': 55000,
            'OGDC': 48000, 'TRG': 52000, 'SYS': 38000, 'NESTLE': 15000,
            'FFC': 42000, 'FFL': 38000, 'PPL': 52000, 'POL': 45000,
            'ATRL': 35000, 'HUBC': 40000, 'KEL': 30000, 'HASCOL': 45000,
            'BOP': 40000, 'MEBL': 30000, 'SNGP': 38000, 'FCCL': 28000,
            'MLCF': 32000, 'DGKC': 30000, 'DEFAULT': 30000
        }

    def calculate_rsi(self, prices, window=14):
        """Calculate RSI from price data - YOUR ACCURATE NUMBERS"""
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

    def analyze_manual_data(self, symbol, current_data, historical_data):
        """Apply elite strategy to YOUR accurate manual data"""
        try:
            # Extract current day data
            close = current_data['close']
            volume = current_data['volume'] 
            high = current_data['high']
            low = current_data['low']
            open_price = current_data['open']
            
            # Calculate RSI from YOUR historical data
            rsi = self.calculate_rsi(historical_data)
            
            # Volume ratio calculation
            base_vol = self.base_volumes.get(symbol, self.base_volumes['DEFAULT'])
            volume_ratio = volume / base_vol if base_vol > 0 else 1
            
            bullish_candle = close > open_price
            
            daily_range = high - low
            price_strength = (close - low) / daily_range if daily_range > 0 else 0.5
            
            # 🎯 ELITE VOLUME POWER BOUNCE STRATEGY
            if (rsi < self.strategy_params['rsi_oversold'] and 
                volume_ratio > self.strategy_params['volume_surge'] and
                bullish_candle and price_strength > 0.6):
                
                # Calculate confidence score
                rsi_factor = (self.strategy_params['rsi_oversold'] - rsi) / 8
                volume_factor = min(volume_ratio / 2.0, 2.5)
                confidence = 6.0 + (rsi_factor * 2.5) + (volume_factor - 1) + 0.8
                confidence = min(max(confidence, 0), 10)
                
                if confidence >= self.strategy_params['min_confidence']:
                    target_price = close * (1 + self.strategy_params['target_gain'] / 100)
                    stop_loss = close * (1 - self.strategy_params['stop_loss'] / 100)
                    
                    return {
                        'symbol': symbol,
                        'price': close,
                        'rsi': round(rsi, 1),
                        'volume_ratio': round(volume_ratio, 1),
                        'confidence': round(confidence, 1),
                        'target': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'signal': 'ELITE_BUY',
                        'reason': f'Oversold bounce (RSI: {rsi:.1f}, Volume: {volume_ratio:.1f}x)',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'data_source': 'MANUAL_ACCURATE'
                    }
            
            return None
            
        except Exception as e:
            return None

def main():
    st.title("🎯 PSX Manual Elite Scanner")
    st.markdown("### **Input YOUR Accurate Data - No Shady APIs**")
    
    st.success("💪 **YOU control the data quality - No more API lies!**")
    
    scanner = ManualPSXScanner()
    
    # Manual Data Input Section
    st.markdown("---")
    st.subheader("📥 Enter Today's Trading Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox(
            "Select Stock:",
            ['HBL', 'UBL', 'MCB', 'BAHL', 'ENGRO', 'EFERT', 'LUCK', 'PSO', 'OGDC', 
             'TRG', 'SYS', 'FFC', 'HUBC', 'KEL', 'BAFL', 'ATRL', 'POL', 'SNGP']
        )
    
    with col2:
        close = st.number_input("Close Price (₨)", min_value=0.0, value=271.31, step=0.01)
        volume = st.number_input("Volume", min_value=0, value=75000, step=1000)
    
    with col3:
        high = st.number_input("High Price (₨)", min_value=0.0, value=275.50, step=0.01)
        low = st.number_input("Low Price (₨)", min_value=0.0, value=269.80, step=0.01)
        open_price = st.number_input("Open Price (₨)", min_value=0.0, value=270.50, step=0.01)
    
    # Historical Data Input
    st.markdown("---")
    st.subheader("📊 Enter Historical Closing Prices (Last 15+ days)")
    
    st.info("💡 Enter the last 15+ closing prices for accurate RSI calculation")
    
    historical_input = st.text_area(
        "Historical Closes (comma-separated):",
        "270.10, 269.50, 268.80, 267.90, 269.20, 270.50, 271.80, 270.20, 269.80, 268.50, 267.20, 268.80, 270.10, 271.50, 272.20",
        help="Enter at least 15 previous closing prices separated by commas"
    )
    
    if st.button("🚀 ANALYZE WITH ELITE STRATEGY", type="primary"):
        # Process historical data
        try:
            historical_prices = [float(x.strip()) for x in historical_input.split(',')]
            
            if len(historical_prices) < 15:
                st.error("❌ Need at least 15 historical prices for accurate RSI")
                return
                
            # Add today's close to historical data for RSI calculation
            historical_prices.append(close)
            
            # Prepare current data
            current_data = {
                'close': close,
                'volume': volume,
                'high': high,
                'low': low,
                'open': open_price
            }
            
            # Analyze with elite strategy
            signal = scanner.analyze_manual_data(symbol, current_data, historical_prices)
            
            st.markdown("---")
            st.subheader("📈 ANALYSIS RESULTS")
            
            if signal:
                st.success(f"🎯 **ELITE SIGNAL DETECTED!**")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.subheader(f"🏆 {signal['symbol']} - STRONG BUY")
                    st.info(f"**Reason:** {signal['reason']}")
                    st.success(f"**Data Quality:** {signal['data_source']}")
                    
                with col2:
                    st.metric("Current Price", f"₨{signal['price']:.2f}")
                    st.metric("RSI", f"{signal['rsi']:.1f}")
                    st.metric("Volume Ratio", f"{signal['volume_ratio']:.1f}x")
                    
                with col3:
                    st.metric("Target", f"₨{signal['target']:.2f}")
                    st.metric("Stop Loss", f"₨{signal['stop_loss']:.2f}")
                    st.metric("Confidence", f"{signal['confidence']}/10")
                
                # Strategy validation
                st.markdown("---")
                st.subheader("✅ STRATEGY VALIDATION")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"RSI < 26: {'✅' if signal['rsi'] < 26 else '❌'} ({signal['rsi']:.1f})")
                with col2:
                    st.write(f"Volume > 2.5x: {'✅' if signal['volume_ratio'] > 2.5 else '❌'} ({signal['volume_ratio']:.1f}x)")
                with col3:
                    st.write(f"Bullish Candle: {'✅' if close > open_price else '❌'}")
                with col4:
                    st.write(f"Signal Quality: {'🟢 HIGH' if signal['confidence'] >= 8 else '🟡 MEDIUM'}")
                
                st.progress(signal['confidence'] / 10)
                
            else:
                st.info("🤷 No elite signal detected with current data")
                st.write("**Strategy conditions not met:**")
                st.write("- RSI must be below 26 (oversold)")
                st.write("- Volume must be > 2.5x average") 
                st.write("- Bullish candle pattern required")
                st.write("- Strong price position in daily range")
                
        except ValueError:
            st.error("❌ Invalid historical data format. Use numbers separated by commas.")

    # Quick Analysis for Multiple Stocks
    st.markdown("---")
    st.subheader("📊 Quick Multi-Stock Analysis")
    
    st.info("💡 **Template for analyzing multiple stocks quickly**")
    
    template = """HBL, 271.31, 75000, 275.50, 269.80, 270.50, 270.10,269.50,268.80,267.90,269.20,270.50,271.80,270.20,269.80,268.50,267.20,268.80,270.10,271.50,272.20
UBL, 200.50, 60000, 202.80, 198.20, 199.80, 199.80,198.50,197.20,199.10,200.80,201.20,199.50,198.80,200.20,201.50,200.80,199.20,198.50,199.80,200.50
MCB, 199.25, 40000, 201.50, 197.80, 198.50, 198.50,197.80,199.20,200.50,199.80,198.20,197.50,199.80,200.20,198.80,197.20,198.50,199.80,200.50,201.20"""
    
    st.code(template, language="text")
    st.caption("Format: Symbol, Close, Volume, High, Low, Open, HistoricalPrices...")

if __name__ == "__main__":
    main()
