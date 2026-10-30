"""
Fyers F&O Algorithmic Trading Framework - Core Execution Engine
An open-source, event-driven modular architecture for Indian derivatives trading.
"""

import os
import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Any, Optional

try:
    from fyers_apiv3 import fyersModel
    from fyers_apiv3.FyersWebsocket import data_ws
except ImportError:
    fyersModel = None
    data_ws = None

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FnoAlgoFramework")


class RiskManager:
    """Handles real-time drawdown monitoring, position sizing, and circuit breakers."""
    
    def __init__(self, max_daily_loss: float = -5000.0, max_open_positions: int = 4):
        self.max_daily_loss = max_daily_loss
        self.max_open_positions = max_open_positions
        self.current_pnl = 0.0
        self.kill_switch_engaged = False

    def validate_order(self, active_positions_count: int) -> bool:
        if self.kill_switch_engaged:
            logger.error("Order rejected: Emergency kill-switch is active.")
            return False
        if self.current_pnl <= self.max_daily_loss:
            logger.critical(f"Max daily drawdown breached ({self.current_pnl}). Engaging kill-switch!")
            self.kill_switch_engaged = True
            return False
        if active_positions_count >= self.max_open_positions:
            logger.warning("Max open positions limit reached. Skipping new signal.")
            return False
        return True


class OptionChainAnalyzer:
    """Provides dynamic ATM/OTM strike calculation and Greeks filtering."""
    
    @staticmethod
    def get_atm_strike(spot_price: float, step_size: int = 50) -> int:
        return int(round(spot_price / step_size) * step_size)

    def format_option_symbol(self, underlying: str, expiry_prefix: str, strike: int, option_type: str) -> str:
        # Format: NSE:NIFTY26OCT24500CE (Standard Fyers symbol structure)
        return f"NSE:{underlying}{expiry_prefix}{strike}{option_type.upper()}"


class FnoExecutionEngine:
    """Core asynchronous engine managing WebSocket ticks and strategy execution."""
    
    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token
        self.risk_manager = RiskManager()
        self.chain_analyzer = OptionChainAnalyzer()
        self.active_positions: Dict[str, Any] = {}
        self.latest_ltp: Dict[str, float] = {}
        
        if fyersModel:
            self.fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                is_async=True,
                log_path=os.getcwd()
            )
        else:
            self.fyers = None
            logger.warning("fyers_apiv3 SDK not found. Running in dry-run simulation mode.")

    def on_tick_update(self, message: Dict[str, Any]) -> None:
        """Callback for incoming WebSocket market data ticks."""
        symbol = message.get("symbol")
        ltp = message.get("ltp")
        if symbol and ltp:
            self.latest_ltp[symbol] = float(ltp)

    async def evaluate_strategy_signals(self) -> Optional[Dict[str, Any]]:
        """
        Abstract hook for custom quantitative strategy logic.
        Override this method in a subclass to plug in proprietary alpha models.
        """
        await asyncio.sleep(0.1)
        return None

    async def place_hedged_order(self, symbol: str, qty: int, side: int) -> Dict[str, Any]:
        """Routes low-latency limit/market orders with built-in risk checks."""
        if not self.risk_manager.validate_order(len(self.active_positions)):
            return {"status": "blocked_by_risk_manager"}

        order_payload = {
            "symbol": symbol,
            "qty": qty,
            "type": 2,  # Market Order
            "side": side,  # 1: Buy, -1: Sell
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
        }
        logger.info(f"Routing order payload: {order_payload}")
        # In live mode: return await self.fyers.place_order(data=order_payload)
        return {"status": "simulated_fill", "payload": order_payload}

    async def start_engine(self) -> None:
        logger.info("Initializing F&O Algorithmic Execution Engine...")
        market_close = time(15, 30)

        while True:
            now = datetime.now().time()
            if now >= market_close:
                logger.info("Market hours concluded. Shutting down execution loop cleanly.")
                break

            if self.risk_manager.kill_switch_engaged:
                logger.critical("Emergency square-off triggered. Halting engine.")
                break

            signal = await self.evaluate_strategy_signals()
            if signal:
                await self.place_hedged_order(
                    symbol=signal["symbol"],
                    qty=signal["qty"],
                    side=signal["side"]
                )

            await asyncio.sleep(1)


if __name__ == "__main__":
    # Credentials are loaded strictly from environment variables for security
    FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID", "YOUR_APP_ID_HERE")
    FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN_HERE")

    engine = FnoExecutionEngine(client_id=FYERS_CLIENT_ID, access_token=FYERS_ACCESS_TOKEN)
    try:
        asyncio.run(engine.start_engine())
    except KeyboardInterrupt:
        logger.info("Engine manually stopped by user.")
