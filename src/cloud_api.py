"""
Cloud API Client for User Bots
================================
Simple client that asks cloud whether to take trades and reports outcomes.
NO RL LOGIC - just communicates with cloud.
"""

import logging
import requests
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class CloudAPIClient:
    """
    Simple API client for user bots to communicate with cloud RL brain.
    
    User bots use this to:
    1. Ask "should I take this trade?" before executing
    2. Report "here's what happened" after trade closes
    """
    
    def __init__(self, api_url: str, license_key: str, timeout: int = 10, max_retries: int = 2):
        """
        Initialize cloud API client.
        
        Args:
            api_url: Cloud API URL (e.g., "https://quotrading-flask-api.azurewebsites.net")
            license_key: User's license key for authentication
            timeout: Request timeout in seconds (default 10s)
            max_retries: Number of retry attempts on connection failure (default 2)
        """
        self.api_url = api_url.rstrip('/')
        self.license_key = license_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.license_valid = True  # Set to False only on 401 license errors
        
        logger.info(f"🌐 Cloud API client initialized: {self.api_url} (retries: {max_retries})")
    
    def ask_should_take_trade(self, state: Dict) -> Tuple[bool, float, str]:
        """
        Ask cloud RL brain whether to take this trade.
        
        Args:
            state: Current market conditions {rsi, vwap_distance, atr, volume_ratio,
                   hour, day_of_week, recent_pnl, streak, side, price}
        
        Returns:
            (take_trade, confidence, reason)
            
        Example:
            take, conf, reason = client.ask_should_take_trade({
                'rsi': 45.2,
                'vwap_distance': 0.02,
                'atr': 2.5,
                'volume_ratio': 1.3,
                'hour': 14,
                'day_of_week': 2,
                'recent_pnl': -50.0,
                'streak': -1,
                'side': 'long',
                'price': 6767.75
            })
            
            if take:
                # Execute trade
                ...
        """
        # Only skip if license is permanently invalid
        if not self.license_valid:
            logger.error("❌ License invalid - trading disabled")
            return False, 0.0, "License invalid - trading disabled"
        
        # Try with retries on EVERY call (always tries to reconnect)
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry attempt {attempt}/{self.max_retries}...")
                
                response = requests.post(
                    f"{self.api_url}/api/rl/analyze-signal",
                    json={
                        "license_key": self.license_key,
                        "state": state
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    take_trade = data.get('take_trade', False)
                    confidence = data.get('confidence', 0.5)
                    reason = data.get('reason', 'Cloud decision')
                    
                    logger.info(f"☁️ Cloud decision: {reason}")
                    return take_trade, confidence, reason
                
                elif response.status_code == 401:
                    logger.error("❌ License validation failed - check license key")
                    self.license_valid = False
                    return False, 0.0, "License invalid - trading disabled"
                
                else:
                    # Server error - retry if we have attempts left
                    if attempt < self.max_retries:
                        logger.warning(f"⚠️ Cloud API error {response.status_code} - will retry")
                        last_error = f"HTTP {response.status_code}"
                        continue
                    else:
                        logger.warning(f"⚠️ Cloud API error {response.status_code} after {self.max_retries} retries - using fallback")
                        return self._fallback_decision(state)
                    
            except requests.Timeout:
                if attempt < self.max_retries:
                    logger.warning(f"⏱️ Cloud API timeout after {self.timeout}s - will retry")
                    last_error = "Timeout"
                    continue
                else:
                    logger.warning(f"⏱️ Cloud API timeout after {self.max_retries} retries - using fallback")
                    return self._fallback_decision(state)
                
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ Cloud API error: {e} - will retry")
                    last_error = str(e)
                    continue
                else:
                    logger.warning(f"⚠️ Cloud API error after {self.max_retries} retries: {e} - using fallback")
                    return self._fallback_decision(state)
        
        # Should never reach here, but just in case
        return self._fallback_decision(state)
    
    def report_trade_outcome(self, state: Dict, took_trade: bool, pnl: float, duration: float, execution_data: Dict = None) -> bool:
        """
        Report trade outcome to cloud RL brain.
        
        Args:
            state: Market state when trade was taken (same as sent to ask_should_take_trade)
            took_trade: Whether trade was actually taken
            pnl: Profit/loss in dollars
            duration: Trade duration in seconds
            execution_data: Execution quality metrics for RL learning (optional)
                - order_type_used: "passive", "aggressive", "mixed"
                - entry_slippage_ticks: Actual slippage in ticks
                - partial_fill: Whether partial fill occurred
                - fill_ratio: Percentage filled (0.66 = 2 of 3)
                - exit_reason: How trade closed
                - held_full_duration: Whether hit target/stop vs time exit
        
        Returns:
            True if successfully reported, False otherwise
            
        Example:
            client.report_trade_outcome(
                state=original_state,
                took_trade=True,
                pnl=125.50,
                duration=1800,
                execution_data={
                    "order_type_used": "passive",
                    "entry_slippage_ticks": 1.5,
                    "partial_fill": False,
                    "fill_ratio": 1.0,
                    "exit_reason": "target_reached",
                    "held_full_duration": True
                }
            )
        """
        # Skip reporting if license is invalid
        if not self.license_valid:
            logger.debug("License invalid - skipping outcome report")
            return False
        
        try:
            payload = {
                "license_key": self.license_key,
                "state": state,
                "took_trade": took_trade,
                "pnl": pnl,
                "duration": duration
            }
            
            # Add execution data if provided
            if execution_data:
                payload["execution_data"] = execution_data
            
            response = requests.post(
                f"{self.api_url}/api/rl/submit-outcome",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                total_exp = data.get('total_experiences', '?')
                win_rate = data.get('win_rate', 0) * 100
                logger.info(f"✅ Outcome reported to cloud ({total_exp} experiences, {win_rate:.0f}% WR)")
                return True
            else:
                logger.warning(f"⚠️ Failed to report outcome: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.debug(f"Non-critical: Could not report outcome to cloud: {e}")
            return False
    
    def _fallback_decision(self, state: Dict) -> Tuple[bool, float, str]:
        """
        Fallback decision when cloud is unavailable.
        
        Conservative approach: Skip signals when cloud is down to avoid bad trades.
        Users can configure this behavior in config.json.
        
        Args:
            state: Market state
        
        Returns:
            (take_trade, confidence, reason)
        """
        # Conservative: skip when cloud is down
        # Alternative: use basic rules (e.g., RSI < 30 for longs)
        return False, 0.0, "⚠️ Cloud unavailable - skipping for safety"
    
    def set_license_valid(self, valid: bool):
        """
        Set license validity status.
        Only call this if you need to re-enable after fixing license issues.
        """
        self.license_valid = valid
        status = "valid" if valid else "invalid"
        logger.info(f"License marked as {status}")
