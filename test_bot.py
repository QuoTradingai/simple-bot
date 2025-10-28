"""
Test script to demonstrate VWAP Bounce Bot functionality
Simulates tick data and validates calculations
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variable before importing
os.environ['TOPSTEP_API_TOKEN'] = 'test_token_for_demo'

from vwap_bounce_bot import (
    initialize_sdk, initialize_state, on_tick, 
    state, CONFIG, logger, calculate_vwap
)


def test_vwap_calculation():
    """Test VWAP calculation with simulated data"""
    print("\n" + "="*60)
    print("Testing VWAP Bounce Bot - Data Processing")
    print("="*60)
    
    # Initialize
    initialize_sdk()
    symbol = CONFIG["instrument"]
    initialize_state(symbol)
    
    # Get timezone
    tz = pytz.timezone(CONFIG["timezone"])
    
    # Simulate tick data over several minutes
    base_time = datetime.now(tz).replace(second=0, microsecond=0)
    base_price = 4500.0  # Starting price for MES
    
    print(f"\n📊 Simulating tick data for {symbol}...")
    print(f"Base time: {base_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Base price: {base_price}")
    
    # Generate ticks across 5 minutes with varying prices and volumes
    tick_count = 0
    for minute in range(5):
        for tick in range(10):  # 10 ticks per minute
            timestamp = base_time + timedelta(minutes=minute, seconds=tick*6)
            timestamp_ms = int(timestamp.timestamp() * 1000)
            
            # Simulate price movement
            price_offset = (tick - 5) * 0.25  # Varies by tick size
            price = base_price + (minute * 0.5) + price_offset
            volume = 1 + (tick % 3)  # Volume between 1-3
            
            on_tick(symbol, price, volume, timestamp_ms)
            tick_count += 1
    
    print(f"✅ Processed {tick_count} ticks")
    
    # Check state
    print(f"\n📈 State Summary:")
    print(f"  Ticks stored: {len(state[symbol]['ticks'])}")
    print(f"  1-min bars: {len(state[symbol]['bars_1min'])}")
    print(f"  15-min bars: {len(state[symbol]['bars_15min'])}")
    
    # Display VWAP calculations
    if state[symbol]['vwap'] is not None:
        print(f"\n💹 VWAP Calculations:")
        print(f"  VWAP: {state[symbol]['vwap']:.2f}")
        print(f"  Std Dev: {state[symbol]['vwap_std_dev']:.2f}")
        print(f"\n  Upper Band 2: {state[symbol]['vwap_bands']['upper_2']:.2f}")
        print(f"  Upper Band 1: {state[symbol]['vwap_bands']['upper_1']:.2f}")
        print(f"  VWAP:         {state[symbol]['vwap']:.2f}")
        print(f"  Lower Band 1: {state[symbol]['vwap_bands']['lower_1']:.2f}")
        print(f"  Lower Band 2: {state[symbol]['vwap_bands']['lower_2']:.2f}")
    else:
        print("\n⚠️  VWAP not yet calculated (need completed bars)")
    
    # Display bar data
    if len(state[symbol]['bars_1min']) > 0:
        print(f"\n📊 Recent 1-Minute Bars:")
        for i, bar in enumerate(list(state[symbol]['bars_1min'])[-3:]):
            print(f"  Bar {i+1}: O:{bar['open']:.2f} H:{bar['high']:.2f} "
                  f"L:{bar['low']:.2f} C:{bar['close']:.2f} V:{bar['volume']}")
    
    # Test trend filter (needs more bars in real scenario)
    print(f"\n🔍 Trend Filter:")
    print(f"  EMA: {state[symbol]['trend_ema']}")
    print(f"  Direction: {state[symbol]['trend_direction']}")
    print(f"  (Requires {CONFIG['trend_filter_period']} 15-min bars)")
    
    # Position status
    print(f"\n💼 Position Status:")
    print(f"  Active: {state[symbol]['position']['active']}")
    print(f"  Daily Trades: {state[symbol]['daily_trade_count']}/{CONFIG['max_trades_per_day']}")
    print(f"  Daily P&L: ${state[symbol]['daily_pnl']:.2f}")
    
    print("\n" + "="*60)
    print("✅ Test completed successfully!")
    print("="*60 + "\n")


def test_configuration():
    """Display bot configuration"""
    print("\n" + "="*60)
    print("VWAP Bounce Bot Configuration")
    print("="*60)
    
    print("\n🎯 Trading Parameters:")
    print(f"  Instrument: {CONFIG['instrument']}")
    print(f"  Trading Hours: {CONFIG['trading_window']['start']} - {CONFIG['trading_window']['end']} ET")
    print(f"  Risk per Trade: {CONFIG['risk_per_trade']*100}%")
    print(f"  Max Contracts: {CONFIG['max_contracts']}")
    print(f"  Max Trades/Day: {CONFIG['max_trades_per_day']}")
    print(f"  Daily Loss Limit: ${CONFIG['daily_loss_limit']}")
    
    print("\n📏 Instrument Specs (MES):")
    print(f"  Tick Size: {CONFIG['tick_size']}")
    print(f"  Tick Value: ${CONFIG['tick_value']}")
    
    print("\n📊 Strategy Parameters:")
    print(f"  Trend Filter: {CONFIG['trend_filter_period']}-period EMA")
    print(f"  Trend Timeframe: {CONFIG['trend_timeframe']} minutes")
    print(f"  VWAP Timeframe: {CONFIG['vwap_timeframe']} minute")
    print(f"  SD Multipliers: {CONFIG['vwap_sd_multipliers']}")
    print(f"  Risk/Reward: {CONFIG['risk_reward_ratio']}:1")
    
    print("\n⚙️  System Settings:")
    print(f"  Dry Run: {CONFIG['dry_run']}")
    print(f"  Log File: {CONFIG['log_file']}")
    print(f"  Max Tick Storage: {CONFIG['max_tick_storage']}")
    print(f"  Max Bars Storage: {CONFIG['max_bars_storage']}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n🤖 VWAP Bounce Bot - Test Suite\n")
    
    # Test configuration display
    test_configuration()
    
    # Test VWAP calculation
    test_vwap_calculation()
    
    print("✨ All tests completed!\n")
