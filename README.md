# Fyers F&O Algorithmic Trading Framework

An open-source, lightweight, and modular Python framework designed for automated Futures and Options (F&O) derivatives trading in the Indian stock market using Fyers API v3.

## 🚀 Key Features
- **Real-Time WebSocket Streaming:** Low-latency tick-by-tick market data processing and live option chain updates.
- **Automated Option Execution:** Dynamic ATM/OTM strike selection, order routing, and position tracking.
- **Strict Risk Management:** Built-in automated stop-loss (SL), trailing targets, and max daily drawdown circuit breakers.
- **Edge & Cloud Ready:** Optimized asynchronous architecture (`asyncio`) capable of running 24/7 on low-power edge devices and cloud servers.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Broker Integration:** `fyers-apiv3`
- **Core Libraries:** `asyncio`, `websockets`, `pandas`, `numpy`

## 📂 Project Structure
- `main.py` - Core execution loop and strategy runner
- `config_sample.py` - Configuration template for API credentials and risk parameters

## ⚠️ Disclaimer
This open-source framework is intended strictly for educational and quantitative research purposes. Algorithmic trading involves financial risk.
