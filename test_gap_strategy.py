"""
Test gap momentum strategy using existing historical data infrastructure
"""

import os
import sys
import logging
from datetime import datetime, timedelta, time
import numpy as np

from backtesting import BacktestConfig, HistoricalDataLoader

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run_gap_backtest(symbol='ES', days=90):
    """Run gap momentum backtest"""
    
    logger.info("="*70)
    logger.info("OPEN-TO-OPEN GAP MOMENTUM BACKTEST")
    logger.info("="*70)
    logger.info("")
    
    # Configuration
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_equity=50000.0,
        data_path='./historical_data'
    )
    
    # Strategy parameters
    gap_threshold_pct = 0.15  # 0.15% gap minimum (filter weak gaps)
    atr_period = 5
    atr_stop_multiple = 3.5  # Wider stop (was 2.0)
    risk_per_trade = 800  # $800 risk per trade (was $500)
    max_contracts = 4
    
    # ES specifications
    tick_size = 0.25
    tick_value = 12.50
    slippage_ticks = 1.5
    commission = 2.50
    
    # Load data
    data_loader = HistoricalDataLoader(config)
    bars = data_loader.load_bar_data(symbol, "1min")
    
    if not bars:
        logger.error("No data loaded!")
        return
    
    logger.info(f"Loaded {len(bars)} 1-minute bars")
    logger.info(f"Date Range: {bars[0]['timestamp']} to {bars[-1]['timestamp']}")
    logger.info("")
    
    # Strategy state
    position = None
    trades = []
    equity = config.initial_equity
    prev_regular_close = None
    recent_bars = []
    min_hold_minutes = 30  # Don't exit on stop for first 30 minutes
    
    # Session times (simplified - checking hour only)
    regular_close_hour = 16  # 4 PM
    globex_open_hour = 18    # 6 PM
    regular_open_hour = 9    # 9:30 AM
    regular_open_minute = 30
    
    def calculate_atr(bars_list):
        """Calculate ATR in ticks"""
        if len(bars_list) < atr_period:
            return None
        
        true_ranges = []
        for i in range(1, min(atr_period + 1, len(bars_list))):
            h = bars_list[-i]['high']
            l = bars_list[-i]['low']
            prev_c = bars_list[-i-1]['close'] if i < len(bars_list) else bars_list[-i]['close']
            
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            true_ranges.append(tr)
        
        if not true_ranges:
            return None
            
        atr_price = np.mean(true_ranges)
        atr_ticks = atr_price / tick_size
        return atr_ticks
    
    def calculate_contracts(atr_ticks):
        """Calculate position size based on ATR"""
        if atr_ticks is None or atr_ticks <= 0:
            return 1
        
        dollar_risk = atr_ticks * tick_value * atr_stop_multiple
        contracts = int(risk_per_trade / dollar_risk)
        return max(1, min(contracts, max_contracts))
    
    # Process each bar
    for i, bar in enumerate(bars):
        ts = bar['timestamp']
        recent_bars.append(bar)
        
        # Track regular close
        if ts.hour == regular_close_hour and ts.minute == 0:
            prev_regular_close = bar['close']
            logger.debug(f"{ts}: Regular close = {prev_regular_close:.2f}")
        
        # Check for gap signal at Globex open
        if (ts.hour == globex_open_hour and ts.minute == 0 and 
            prev_regular_close is not None and position is None):
            
            globex_open = bar['open']
            gap_pct = ((globex_open / prev_regular_close) - 1) * 100
            
            logger.info(f"{ts}: Gap = {gap_pct:+.3f}% (Open: {globex_open:.2f}, Prev Close: {prev_regular_close:.2f})")
            
            signal = None
            if gap_pct > gap_threshold_pct:
                signal = 'long'
            elif gap_pct < -gap_threshold_pct:
                signal = 'short'
            
            if signal:
                # Calculate ATR and size
                atr_ticks = calculate_atr(recent_bars)
                if atr_ticks:
                    contracts = calculate_contracts(atr_ticks)
                    
                    # Entry with slippage
                    if signal == 'long':
                        entry_price = globex_open + (slippage_ticks * tick_size)
                        stop_price = globex_open - (atr_ticks * atr_stop_multiple * tick_size)
                    else:
                        entry_price = globex_open - (slippage_ticks * tick_size)
                        stop_price = globex_open + (atr_ticks * atr_stop_multiple * tick_size)
                    
                    position = {
                        'side': signal,
                        'contracts': contracts,
                        'entry_price': entry_price,
                        'stop_price': stop_price,
                        'entry_time': ts,
                        'atr_ticks': atr_ticks
                    }
                    
                    logger.info(f"  → ENTER {signal.upper()}: {contracts} contracts @ {entry_price:.2f}")
                    logger.info(f"     Stop: {stop_price:.2f}, ATR: {atr_ticks:.1f} ticks")
        
        # Check exit conditions
        if position:
            pos = position
            should_exit = False
            exit_price = None
            reason = None
            
            # Calculate time in trade
            time_in_trade = (ts - pos['entry_time']).total_seconds() / 60
            
            # Stop loss (only after minimum hold period)
            if time_in_trade >= min_hold_minutes:
                if pos['side'] == 'long':
                    if bar['low'] <= pos['stop_price']:
                        should_exit = True
                        exit_price = pos['stop_price']
                        reason = 'STOP LOSS'
                else:
                    if bar['high'] >= pos['stop_price']:
                        should_exit = True
                        exit_price = pos['stop_price']
                        reason = 'STOP LOSS'
            
            # Session open exit (next day)
            if ts.hour == regular_open_hour and ts.minute == regular_open_minute:
                should_exit = True
                exit_price = bar['open']
                reason = 'SESSION OPEN'
            
            # Execute exit
            if should_exit:
                # Apply slippage
                if pos['side'] == 'long':
                    fill_price = exit_price - (slippage_ticks * tick_size)
                else:
                    fill_price = exit_price + (slippage_ticks * tick_size)
                
                # Calculate P&L
                if pos['side'] == 'long':
                    price_change = fill_price - pos['entry_price']
                else:
                    price_change = pos['entry_price'] - fill_price
                
                ticks = price_change / tick_size
                pnl = (ticks * tick_value * pos['contracts']) - (commission * pos['contracts'])
                
                equity += pnl
                
                trade = {
                    'entry_time': pos['entry_time'],
                    'exit_time': ts,
                    'side': pos['side'],
                    'contracts': pos['contracts'],
                    'entry_price': pos['entry_price'],
                    'exit_price': fill_price,
                    'stop_price': pos['stop_price'],
                    'pnl': pnl,
                    'reason': reason,
                    'ticks': ticks,
                    'atr': pos['atr_ticks']
                }
                
                trades.append(trade)
                
                logger.info(f"{ts}: EXIT {pos['side'].upper()}: {pos['contracts']} contracts @ {fill_price:.2f}")
                logger.info(f"  → {reason}, P&L: ${pnl:+,.2f} ({ticks:+.1f} ticks)")
                logger.info("")
                
                position = None
    
    # Results
    logger.info("="*70)
    logger.info("BACKTEST RESULTS")
    logger.info("="*70)
    logger.info("")
    
    if not trades:
        logger.info("No trades executed!")
        return
    
    total_pnl = sum(t['pnl'] for t in trades)
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] < 0]
    
    win_rate = (len(wins) / len(trades)) * 100
    avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
    avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
    
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999
    
    total_return = ((equity / config.initial_equity) - 1) * 100
    
    logger.info(f"Total Trades:       {len(trades)}")
    logger.info(f"Winning Trades:     {len(wins)} ({win_rate:.2f}%)")
    logger.info(f"Losing Trades:      {len(losses)}")
    logger.info("")
    logger.info(f"Total P&L:          ${total_pnl:+,.2f}")
    logger.info(f"Average Win:        ${avg_win:+,.2f}")
    logger.info(f"Average Loss:       ${avg_loss:+,.2f}")
    logger.info(f"Profit Factor:      {profit_factor:.2f}")
    logger.info("")
    logger.info(f"Starting Equity:    ${config.initial_equity:,.2f}")
    logger.info(f"Final Equity:       ${equity:,.2f}")
    logger.info(f"Total Return:       {total_return:+.2f}%")
    logger.info("")
    logger.info("="*70)
    logger.info("TRADE LOG")
    logger.info("="*70)
    
    for i, t in enumerate(trades, 1):
        logger.info(f"Trade #{i}: {t['entry_time'].strftime('%Y-%m-%d')} {t['side'].upper()}")
        logger.info(f"  Entry: {t['entry_price']:.2f} @ {t['entry_time'].strftime('%H:%M')}")
        logger.info(f"  Exit:  {t['exit_price']:.2f} @ {t['exit_time'].strftime('%H:%M')} ({t['reason']})")
        logger.info(f"  P&L:   ${t['pnl']:+,.2f} ({t['ticks']:+.1f} ticks, {t['contracts']} contracts)")
        logger.info("")
    
    logger.info("="*70)


if __name__ == '__main__':
    run_gap_backtest()
