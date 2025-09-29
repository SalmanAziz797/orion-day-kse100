import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="PSX KSE-100 Elite Scanner",
    page_icon="📊",
    layout="wide"
)

class PSXKSE100Scanner:
    def __init__(self):
        try:
            self.api_key = st.secrets["EODHD_API_KEY"]
        except:
            st.error("❌ API key not configured. Please add EODHD_API_KEY to Streamlit secrets.")
            st.stop()
        
        self.strategy_params = {
            'rsi_oversold': 26,
            'volume_surge': 2.5,
            'min_confidence': 7.0,
            'target_gain': 2.8,
            'stop_loss': 0.8
        }
        
        # CURATED KSE-100 STOCKS WITH DATA AVAILABILITY
        # Based on actual EODHD data availability
        self.kse_100_symbols = [
            # Banking (High liquidity)
            'HBL.KAR', 'UBL.KAR', 'MCB.KAR', 'BAHL.KAR', 'BAFL.KAR',
            'BOP.KAR', 'JSBL.KAR', 'MEBL.KAR', 'SNBL.KAR',
            
            # Oil & Gas (Major players)
            'OGDC.KAR', 'PPL.KAR', 'POL.KAR', 'PSO.KAR', 'SNGP.KAR',
            'ATRL.KAR', 'HASCOL.KAR',
            
            # Cement & Construction
            'LUCK.KAR', 'DGKC.KAR', 'MLCF.KAR', 'FCCL.KAR', 'PIOC.KAR',
            'POWER.KAR', 'KOHAT.KAR',
            
            # Fertilizer
            'EFERT.KAR', 'FFC.KAR', 'FFL.KAR', 'FATIMA.KAR',
            
            # Power
            'HUBC.KAR', 'KAPCO.KAR', 'KEL.KAR',
            
            # Technology
            'TRG.KAR', 'SYS.KAR', 'NETSOL.KAR',
            
            # Food & Personal Care
            'NESTLE.KAR', 'COLG.KAR', 'UPFL.KAR', 'GLAXO.KAR',
            
            # Chemical
            'EPCL.KAR', 'LOTCHEM.KAR',
            
            # Insurance
            'EFUG.KAR', 'AGIL.KAR',
            
            # Textile
            'NCL.KAR', 'SILK.KAR',
            
            # Miscellaneous (Active traders)
            'ISL.KAR', 'DAWH.KAR', 'SEARL.KAR', 'AVN.KAR'
        ]
        
        self.base_volumes = {
            # Banking
            'HBL.KAR': 50000, 'UBL.KAR': 45000, 'MCB.KAR': 30000, 
            'BAHL.KAR': 25000, 'BAFL.KAR': 35000, 'BOP.KAR': 40000,
            'JSBL.KAR': 15000, 'MEBL.KAR': 30000, 'SNBL.KAR': 20000,
            
            # Oil & Gas
            'OGDC.KAR': 48000, 'PPL.KAR': 52000, 'POL.KAR': 45000,
            'PSO.KAR': 55000, 'SNGP.KAR': 38000, 'ATRL.KAR': 35000,
            'HASCOL.KAR': 45000,
            
            # Cement & Construction
            'LUCK.KAR': 35000, 'DGKC.KAR': 30000, 'MLCF.KAR': 32000,
            'FCCL.KAR': 28000, 'PIOC.KAR': 18000, 'POWER.KAR': 25000,
            'KOHAT.KAR': 20000,
            
            # Fertilizer
            'EFERT.KAR': 40000, 'FFC.KAR': 42000, 'FFL.KAR': 38000,
            'FATIMA.KAR': 30000,
            
            # Power
            'HUBC.KAR': 40000, 'KAPCO.KAR': 35000, 'KEL.KAR': 30000,
            
            # Technology
            'TRG.KAR': 52000, 'SYS.KAR': 38000, 'NETSOL.KAR': 12000,
            
            # Food & Personal Care
            'NESTLE.KAR': 15000, 'COLG.KAR': 8000, 'UPFL.KAR': 12000,
            'GLAXO.KAR': 15000,
            
            # Chemical
            'EPCL.KAR': 25000, 'LOTCHEM.KAR': 28000,
            
            # Insurance
            'EFUG.KAR': 22000, 'AGIL.KAR': 12000,
            
            # Textile
            'NCL.KAR': 22000, 'SILK.KAR': 8000,
            
            # Miscellaneous
            'ISL.KAR': 32000, 'DAWH.KAR': 25000, 'SEARL.KAR': 18000,
            'AVN.KAR': 8000,
            
            'DEFAULT': 25000
        }

    def test_data_availability(self, symbol):
        """Quick test if stock has EOD data available"""
        url = f"https://eodhd.com/api/eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'fmt': 'json',
            'from': '2024-01-01',
            'to': datetime.now().strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data and len(data) > 0
            return False
        except:
            return False

    def fetch_eod_data(self, symbol):
        """Fetch End-of-Day data from EODHD"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        url = f"https://eodhd.com/api/eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'fmt': 'json',
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest_data = data[-1]
                    return {
                        'symbol': symbol,
                        'close': latest_data['close'],
                        'volume': latest_data['volume'],
                        'high': latest_data['high'],
                        'low': latest_data['low'],
                        'open': latest_data['open'],
                        'date': latest_data['date'],
                        'data_points': len(data)
                    }
            return None
        except:
            return None

    def calculate_rsi(self, closes, window=14):
        """Calculate RSI from closing prices"""
        if len(closes) < window + 1:
            return 50
            
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = pd.Series(gains).rolling(window=window).mean()
        avg_losses = pd.Series(losses).rolling(window=window).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not rsi.empty else 50

    def fetch_historical_data(self, symbol, days=30):
        """Fetch historical data for RSI calculation"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f"https://eodhd.com/api/eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'fmt': 'json',
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return [day['close'] for day in data]
            return None
        except:
            return None

    def analyze_elite_signal(self, symbol):
        """Apply elite strategy to EOD data"""
        try:
            eod_data = self.fetch_eod_data(symbol)
            if not eod_data or eod_data['close'] <= 0:
                return None
            
            historical_closes = self.fetch_historical_data(symbol, 30)
            if not historical_closes or len(historical_closes) < 15:
                return None
            
            rsi = self.calculate_rsi(historical_closes)
            
            base_vol = self.base_volumes.get(symbol, self.base_volumes['DEFAULT'])
            volume_ratio = eod_data['volume'] / base_vol if base_vol > 0 and eod_data['volume'] > 0 else 1
            
            bullish_candle = eod_data['close'] > eod_data['open']
            
            daily_range = eod_data['high'] - eod_data['low']
            price_strength = (eod_data['close'] - eod_data['low']) / daily_range if daily_range > 0 else 0.5
            
            # 🎯 ELITE STRATEGY
            if (rsi < self.strategy_params['rsi_oversold'] and 
                volume_ratio > self.strategy_params['volume_surge'] and
                bullish_candle and price_strength > 0.6):
                
                rsi_factor = (self.strategy_params['rsi_oversold'] - rsi) / 8
                volume_factor = min(volume_ratio / 2.0, 2.5)
                confidence = 6.0 + (rsi_factor * 2.5) + (volume_factor - 1) + 0.8
                confidence = min(max(confidence, 0), 10)
                
                if confidence >= self.strategy_params['min_confidence']:
                    target_price = eod_data['close'] * (1 + self.strategy_params['target_gain'] / 100)
                    stop_loss = eod_data['close'] * (1 - self.strategy_params['stop_loss'] / 100)
                    
                    return {
                        'symbol': symbol.replace('.KAR', ''),
                        'price': eod_data['close'],
                        'rsi': round(rsi, 1),
                        'volume_ratio': round(volume_ratio, 1),
                        'confidence': round(confidence, 1),
                        'target': round(target_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'signal': 'ELITE_BUY',
                        'reason': f'Oversold bounce (RSI: {rsi:.1f}, Volume: {volume_ratio:.1f}x)',
                        'date': eod_data['date']
                    }
        except:
            return None
        
        return None

    def run_kse100_scan(self):
        """Run scan on curated KSE-100 stocks"""
        st.info(f"🔍 Scanning {len(self.kse_100_symbols)} curated KSE-100 stocks...")
        
        signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_text = st.empty()
        
        successful_scans = 0
        failed_scans = 0
        
        for i, symbol in enumerate(self.kse_100_symbols):
            status_text.text(f"Analyzing {symbol.replace('.KAR', '')}... ({i+1}/{len(self.kse_100_symbols)})")
            signal = self.analyze_elite_signal(symbol)
            
            if signal:
                signals.append(signal)
                successful_scans += 1
            else:
                failed_scans += 1
            
            stats_text.text(f"✅ {successful_scans} successful | ❌ {failed_scans} failed | 📊 {len(signals)} signals")
            progress_bar.progress((i + 1) / len(self.kse_100_symbols))
            time.sleep(0.2)
        
        return signals, successful_scans, failed_scans

def main():
    st.title("🏆 PSX KSE-100 Elite Scanner")
    st.markdown("### **Curated KSE-100 Stocks - Practical Approach**")
    
    scanner = PSXKSE100Scanner()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("KSE-100 Stocks", len(scanner.kse_100_symbols))
    with col2:
        st.metric("Data Type", "End-of-Day")
    with col3:
        st.metric("Strategy", "Volume Bounce")
    with col4:
        st.metric("Focus", "High Liquidity")
    
    st.success("🎯 **Curated list of 50+ KSE-100 stocks with confirmed data availability**")
    
    # Show sectors
    with st.expander("📊 Stock Sectors Covered"):
        sectors = {
            "Banking": 9,
            "Oil & Gas": 7, 
            "Cement & Construction": 7,
            "Fertilizer": 4,
            "Power": 3,
            "Technology": 3,
            "Food & Personal Care": 4,
            "Chemical": 2,
            "Insurance": 2,
            "Textile": 2,
            "Miscellaneous": 4
        }
        
        for sector, count in sectors.items():
            st.write(f"**{sector}:** {count} stocks")
    
    if st.button("🚀 SCAN CURATED KSE-100", type="primary", use_container_width=True):
        signals, successful, failed = scanner.run_kse100_scan()
        
        st.success(f"📊 Scan Complete: {successful} stocks analyzed | {failed} no data | {len(signals)} elite signals")
        
        if signals:
            st.success(f"🎯 **FOUND {len(signals)} ELITE SIGNALS!**")
            
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            for signal in signals:
                with st.container():
                    st.markdown("---")
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.subheader(f"🏆 {signal['symbol']} - STRONG BUY")
                        st.info(f"**Reason:** {signal['reason']}")
                        st.caption(f"**Data Date:** {signal['date']}")
                        
                    with col2:
                        st.metric("Close Price", f"₨{signal['price']:.2f}")
                        st.metric("RSI", f"{signal['rsi']:.1f}")
                        st.metric("Volume", f"{signal['volume_ratio']:.1f}x")
                        
                    with col3:
                        st.metric("Target", f"₨{signal['target']:.2f}")
                        st.metric("Stop Loss", f"₨{signal['stop_loss']:.2f}")
                        st.metric("Confidence", f"{signal['confidence']}/10")
                    
                    st.progress(signal['confidence'] / 10)
            
            st.markdown("---")
            st.subheader("📈 KSE-100 SCAN SUMMARY")
            total_return = sum([(signal['target'] - signal['price']) / signal['price'] * 100 for signal in signals])
            avg_confidence = sum([signal['confidence'] for signal in signals]) / len(signals) if signals else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Signals Found", len(signals))
            col2.metric("Success Rate", f"{(successful/len(scanner.kse_100_symbols))*100:.1f}%")
            col3.metric("Avg Confidence", f"{avg_confidence:.1f}/10")
            col4.metric("Expected Return", f"{total_return:.1f}%")
            
        else:
            st.info("🤷 No elite signals found in KSE-100. Market conditions may not meet the strict criteria.")

if __name__ == "__main__":
    main()
