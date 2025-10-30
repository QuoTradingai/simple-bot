"""
Open-to-Open Gap Momentum Strategy for ES/NQ
Trades overnight gaps at session open with ATR-based sizing and stops
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

class GapMomentumStrategy:
    """
    Gap momentum strategy:
    - Measures overnight gap from previous regular close to Globex open
    - Long if gap > +0.05%, Short if gap < -0.05%
    - ATR-based position sizing and stops
    - Exit at next session open or intraday stop
    """
    
    def __init__(self, config):
        self.config = config
        
        # Strategy parameters
        self.gap_threshold_pct = config.get('gap_threshold_pct', 0.05)  # 0.05%
        self.atr_period = config.get('atr_period', 5)
        self.atr_stop_multiple = config.get('atr_stop_multiple', 2.0)
        self.risk_per_trade = config.get('risk_per_trade', 500)  # $500 per trade
        self.max_contracts = config.get('max_contracts', 4)
        self.entry_delay_minutes = config.get('entry_delay_minutes', 1)  # Wait 1 min after open
        
        # ES/NQ specifications
        self.tick_size = config.get('tick_size', 0.25)  # ES = 0.25
        self.tick_value = config.get('tick_value', 12.50)  # ES = $12.50
        self.slippage_ticks = config.get('slippage_ticks', 1.5)
        self.commission = config.get('commission', 2.50)
        
        # Session times (ET)
        self.regular_close_time = time(16, 0)  # 4:00 PM ET
        self.globex_open_time = time(18, 0)    # 6:00 PM ET (Sunday-Thursday)
        self.regular_open_time = time(9, 30)   # 9:30 AM ET
        
        # State
        self.position = None
        self.trades = []
        self.equity = config.get('initial_equity', 50000)
        self.prev_regular_close = None
        
    def calculate_atr(self, bars, period=5):
        """Calculate ATR in ticks"""
        if len(bars) < period:
            return None
            
        highs = [b['high'] for b in bars[-period:]]
        lows = [b['low'] for b in bars[-period:]]
        closes = [b['close'] for b in bars[-period-1:]]
        
        true_ranges = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i-1] - lows[i-1],
                abs(highs[i-1] - closes[i-1]),
                abs(lows[i-1] - closes[i-1])
            )
            true_ranges.append(tr)
        
        atr_price = np.mean(true_ranges)
        atr_ticks = atr_price / self.tick_size
        return atr_ticks
    
    def calculate_position_size(self, atr_ticks):
        """Calculate contracts based on ATR and risk target"""
        if atr_ticks is None or atr_ticks <= 0:
            return 1
        
        # Dollar risk per contract
        dollar_risk_per_contract = atr_ticks * self.tick_value
        
        # Contracts = risk target / risk per contract
        contracts = int(self.risk_per_trade / dollar_risk_per_contract)
        
        # Apply limits
        contracts = max(1, min(contracts, self.max_contracts))
        
        return contracts
    
    def check_gap_signal(self, current_bar, timestamp):
        """Check for gap trading signal at market open"""
        if self.prev_regular_close is None:
            return None
        
        # Calculate overnight gap
        globex_open = current_bar['open']
        gap_pct = ((globex_open / self.prev_regular_close) - 1) * 100
        
        logger.info(f"Gap: {gap_pct:.3f}% (Open: {globex_open}, Prev Close: {self.prev_regular_close})")
        
        # Check gap threshold
        if gap_pct > self.gap_threshold_pct:
            return 'long'
        elif gap_pct < -self.gap_threshold_pct:
            return 'short'
        
        return None
    
    def enter_position(self, side, entry_price, contracts, stop_price, timestamp):
        """Enter a new position"""
        # Apply slippage
        if side == 'long':
            fill_price = entry_price + (self.slippage_ticks * self.tick_size)
        else:
            fill_price = entry_price - (self.slippage_ticks * self.tick_size)
        
        self.position = {
            'side': side,
            'contracts': contracts,
            'entry_price': fill_price,
            'stop_price': stop_price,
            'entry_time': timestamp
        }
        
        logger.info(f"ENTER {side.upper()}: {contracts} contracts @ {fill_price}, Stop: {stop_price}")
    
    def check_exit_conditions(self, current_bar, timestamp):
        """Check if position should be exited"""
        if self.position is None:
            return False, None, None
        
        pos = self.position
        current_price = current_bar['close']
        
        # Check stop loss
        if pos['side'] == 'long':
            if current_bar['low'] <= pos['stop_price']:
                return True, pos['stop_price'], 'stop_loss'
        else:
            if current_bar['high'] >= pos['stop_price']:
                return True, pos['stop_price'], 'stop_loss'
        
        # Check if next session open (exit at open-to-open)
        bar_time = timestamp.time()
        if bar_time >= self.regular_open_time:
            return True, current_price, 'session_open_exit'
        
        return False, None, None
    
    def exit_position(self, exit_price, reason, timestamp):
        """Close current position"""
        if self.position is None:
            return
        
        pos = self.position
        
        # Apply slippage
        if pos['side'] == 'long':
            fill_price = exit_price - (self.slippage_ticks * self.tick_size)
        else:
            fill_price = exit_price + (self.slippage_ticks * self.tick_size)
        
        # Calculate P&L
        if pos['side'] == 'long':
            price_change = fill_price - pos['entry_price']
        else:
            price_change = pos['entry_price'] - fill_price
        
        ticks = price_change / self.tick_size
        pnl = (ticks * self.tick_value * pos['contracts']) - (self.commission * pos['contracts'])
        
        # Record trade
        trade = {
            'entry_time': pos['entry_time'],
            'exit_time': timestamp,
            'side': pos['side'],
            'contracts': pos['contracts'],
            'entry_price': pos['entry_price'],
            'exit_price': fill_price,
            'stop_price': pos['stop_price'],
            'pnl': pnl,
            'exit_reason': reason
        }
        
        self.trades.append(trade)
        self.equity += pnl
        
        logger.info(f"EXIT {pos['side'].upper()}: {pos['contracts']} contracts @ {fill_price}, P&L: ${pnl:+.2f}, Reason: {reason}")
        
        self.position = None
    
    def process_bar(self, bar, timestamp):
        """Process a single bar"""
        bar_time = timestamp.time()
        
        # Update previous regular close
        if bar_time == self.regular_close_time:
            self.prev_regular_close = bar['close']
            logger.debug(f"Regular close updated: {self.prev_regular_close}")
        
        # Check for gap signal at Globex open
        if bar_time == self.globex_open_time and self.position is None:
            signal = self.check_gap_signal(bar, timestamp)
            
            if signal:
                # Calculate ATR and position size
                # Note: In real implementation, use recent bars for ATR
                atr_ticks = self.calculate_atr([bar], self.atr_period)
                if atr_ticks:
                    contracts = self.calculate_position_size(atr_ticks)
                    
                    # Calculate stop
                    if signal == 'long':
                        stop_price = bar['open'] - (atr_ticks * self.atr_stop_multiple * self.tick_size)
                    else:
                        stop_price = bar['open'] + (atr_ticks * self.atr_stop_multiple * self.tick_size)
                    
                    self.enter_position(signal, bar['open'], contracts, stop_price, timestamp)
        
        # Check exit conditions
        if self.position:
            should_exit, exit_price, reason = self.check_exit_conditions(bar, timestamp)
            if should_exit:
                self.exit_position(exit_price, reason, timestamp)
    
    def get_results(self):
        """Calculate and return backtest results"""
        if not self.trades:
            return {
                'total_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'final_equity': self.equity
            }
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = (len(wins) / len(self.trades)) * 100 if self.trades else 0
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        
        gross_profit = sum(t['pnl'] for t in wins)
        gross_loss = abs(sum(t['pnl'] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_trades': len(self.trades),
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_equity': self.equity,
            'total_return': ((self.equity / self.config['initial_equity']) - 1) * 100,
            'trades': self.trades
        }


def run_gap_backtest(symbol='ES', days=90):
    """Run gap momentum backtest"""
    logger.info("="*60)
    logger.info("GAP MOMENTUM BACKTEST")
    logger.info("="*60)
    
    config = {
        'gap_threshold_pct': 0.04,  # 0.04% gap threshold
        'atr_period': 5,
        'atr_stop_multiple': 2.0,
        'risk_per_trade': 500,
        'max_contracts': 4,
        'entry_delay_minutes': 1,
        'tick_size': 0.25,
        'tick_value': 12.50,
        'slippage_ticks': 1.5,
        'commission': 2.50,
        'initial_equity': 50000
    }
    
    strategy = GapMomentumStrategy(config)
    
    # Load historical data
    # TODO: Replace with actual data loading
    logger.warning("Gap strategy requires actual 1-minute bar data with session markers")
    logger.warning("This is a skeleton - integrate with your historical data source")
    
    results = strategy.get_results()
    
    logger.info("="*60)
    logger.info("RESULTS")
    logger.info("="*60)
    logger.info(f"Total Trades: {results['total_trades']}")
    logger.info(f"Total P&L: ${results['total_pnl']:+,.2f}")
    logger.info(f"Win Rate: {results['win_rate']:.2f}%")
    logger.info(f"Average Win: ${results['avg_win']:+.2f}")
    logger.info(f"Average Loss: ${results['avg_loss']:+.2f}")
    logger.info(f"Profit Factor: {results['profit_factor']:.2f}")
    logger.info(f"Final Equity: ${results['final_equity']:,.2f}")
    logger.info(f"Total Return: {results['total_return']:+.2f}%")
    logger.info("="*60)
    
    return results


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_gap_backtest()
