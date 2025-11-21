#!/usr/bin/env python3
"""
Development Backtesting Environment for VWAP Bounce Bot

This is the development/testing environment that:
- Runs backtests to test bot performance
- Loads signal RL locally from data/signal_experience.json
- Includes pattern matching and all trading logic
- Handles all regimes (HIGH_VOL_TRENDING, HIGH_VOL_CHOPPY, etc.)
- Follows same UTC maintenance and flatten rules as production
- Does everything the live bot does with all trade management

Separated from production bot for clean architecture.
"""

import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from types import ModuleType
import pytz

# Add parent directory to path to import from src/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

# Import backtesting framework from dev
from backtesting import BacktestConfig, BacktestEngine, ReportGenerator

# Import production bot modules
from config import load_config
from monitoring import setup_logging
from signal_confidence import SignalConfidenceRL


def parse_arguments():
    """Parse command-line arguments for backtest"""
    parser = argparse.ArgumentParser(
        description='VWAP Bounce Bot - Development Backtesting Environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest for last 30 days (bar-by-bar with 1-minute bars)
  python dev/run_backtest.py --days 30
  
  # Run backtest with specific date range
  python dev/run_backtest.py --start 2024-01-01 --end 2024-01-31
  
  # Run backtest with tick-by-tick replay (requires tick data)
  python dev/run_backtest.py --days 7 --use-tick-data
  
  # Save backtest report to file
  python dev/run_backtest.py --days 30 --report backtest_results.txt
        """
    )
    
    parser.add_argument(
        '--start',
        type=str,
        help='Backtest start date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end',
        type=str,
        help='Backtest end date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        help='Backtest for last N days (alternative to --start/--end)'
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Path to historical data directory (default: <project_root>/data/historical_data)'
    )
    
    parser.add_argument(
        '--initial-equity',
        type=float,
        default=50000.0,
        help='Initial equity for backtesting (default: 50000)'
    )
    
    parser.add_argument(
        '--report',
        type=str,
        help='Save backtest report to specified file'
    )
    
    parser.add_argument(
        '--use-tick-data',
        action='store_true',
        help='Use tick-by-tick replay instead of bar-by-bar (requires tick data files)'
    )
    
    parser.add_argument(
        '--symbol',
        type=str,
        help='Override trading symbol (default: MES)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    return parser.parse_args()


def initialize_rl_brains_for_backtest() -> Tuple[Any, ModuleType]:
    """
    Initialize RL brain (signal confidence) for backtest mode.
    This ensures experience files are loaded before the backtest runs.
    
    Returns:
        Tuple of (rl_brain, bot_module) where rl_brain is the SignalConfidenceRL 
        instance and bot_module is the loaded trading engine module
    """
    logger = logging.getLogger('backtest')
    
    # Import the bot module to access its RL brain
    # Note: We need to import it dynamically since quotrading_engine is the actual module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "quotrading_engine",
        os.path.join(PROJECT_ROOT, "src/quotrading_engine.py")
    )
    bot_module = importlib.util.module_from_spec(spec)
    sys.modules['quotrading_engine'] = bot_module
    
    # Also make it available as vwap_bounce_bot for compatibility
    sys.modules['vwap_bounce_bot'] = bot_module
    
    # Load the module
    spec.loader.exec_module(bot_module)
    
    # Initialize RL brain with experience file
    signal_exp_file = os.path.join(PROJECT_ROOT, "data/signal_experience.json")
    rl_brain = SignalConfidenceRL(
        experience_file=signal_exp_file,
        backtest_mode=True
    )
    
    # Set it on the bot module if it has rl_brain attribute
    if hasattr(bot_module, 'rl_brain'):
        bot_module.rl_brain = rl_brain
    
    logger.info(f"✅ RL BRAIN INITIALIZED for backtest - {len(rl_brain.experiences)} signal experiences loaded")
    
    return rl_brain, bot_module


def run_backtest_with_params(
    symbol: str, 
    days: int, 
    initial_equity: float, 
    params: Dict[str, Any], 
    return_bars: bool = False
) -> Union[Dict[str, Any], Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Run a backtest with custom parameters and return results.
    This is a helper function for continuous learning and parameter optimization.
    
    Args:
        symbol: Trading symbol (e.g., 'ES')
        days: Number of days to backtest
        initial_equity: Starting equity
        params: Dictionary of parameters to override in config
        return_bars: If True, return (results, bars) tuple for regime classification
        
    Returns:
        Dictionary with backtest results (pnl, win_rate, trades, etc.)
        OR (results_dict, bars_list) if return_bars=True
    """
    import config as cfg
    
    logger = logging.getLogger('continuous_learner')
    
    # Map learning parameter names to actual config variable names
    param_mapping = {
        # Core signal parameters
        'vwap_std_dev_1': 'vwap_std_dev_1',
        'vwap_std_dev_2': 'vwap_std_dev_2',
        'vwap_std_dev_3': 'vwap_std_dev_3',
        'rsi_period': 'rsi_period',
        'rsi_oversold': 'rsi_oversold',
        'rsi_overbought': 'rsi_overbought',
        
        # Risk management
        'stop_loss_atr_multiplier': 'stop_loss_atr_multiplier',
        'profit_target_atr_multiplier': 'profit_target_atr_multiplier',
        
        # Breakeven
        'breakeven_profit_threshold_ticks': 'breakeven_profit_threshold_ticks',
        'breakeven_stop_offset_ticks': 'breakeven_stop_offset_ticks',
        
        # Trailing
        'trailing_stop_distance_ticks': 'trailing_stop_distance_ticks',
        'trailing_stop_min_profit_ticks': 'trailing_stop_min_profit_ticks',
        
        # Time decay
        'time_decay_50_percent_tightening': 'time_decay_50_percent_tightening',
        'time_decay_75_percent_tightening': 'time_decay_75_percent_tightening',
        'time_decay_90_percent_tightening': 'time_decay_90_percent_tightening',
        
        # Partial exits
        'partial_exit_1_percentage': 'partial_exit_1_percentage',
        'partial_exit_1_r_multiple': 'partial_exit_1_r_multiple',
        'partial_exit_2_percentage': 'partial_exit_2_percentage',
        'partial_exit_2_r_multiple': 'partial_exit_2_r_multiple',
        
        # Filters
        'volume_multiplier_threshold': 'volume_multiplier_threshold',
        'trend_ema_period': 'trend_ema_period',
        'max_trades_per_day': 'max_trades_per_day',
    }
    
    original_values = {}
    for param_key, value in params.items():
        # Get config variable name
        config_var = param_mapping.get(param_key, param_key)
        
        if hasattr(cfg, config_var):
            original_values[config_var] = getattr(cfg, config_var)
            setattr(cfg, config_var, value)
            logger.debug(f"Set {config_var} = {value}")
    
    try:
        # Calculate date range
        tz = pytz.timezone("US/Eastern")
        end_date = datetime.now(tz)
        start_date = end_date - timedelta(days=days)
        
        # Create backtest config
        backtest_config = BacktestConfig(
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            initial_equity=initial_equity
        )
        
        # Get bot config - create instance and convert to dict
        bot_cfg_instance = cfg.load_config(backtest_mode=True)
        bot_config_dict = {k: getattr(bot_cfg_instance, k) for k in dir(bot_cfg_instance) if not k.startswith('_')}
        
        # Initialize backtest engine with proper parameters
        engine = BacktestEngine(config=backtest_config, bot_config=bot_config_dict)
        
        # Initialize RL brain and bot module
        rl_brain, bot_module = initialize_rl_brains_for_backtest()
        
        # Import bot functions from the loaded module
        initialize_state = bot_module.initialize_state
        check_for_signals = bot_module.check_for_signals
        check_exit_conditions = bot_module.check_exit_conditions
        check_daily_reset = bot_module.check_daily_reset
        state = bot_module.state
        inject_complete_bar = bot_module.inject_complete_bar
        
        # Initialize bot state
        initialize_state(symbol)
        
        # Set bot instance for RL tracking
        class BotRLReferences:
            def __init__(self):
                self.signal_rl = rl_brain
        
        bot_ref = BotRLReferences()
        engine.set_bot_instance(bot_ref)
        
        # Store bars for regime classification if needed
        all_bars = []
        
        # Define strategy function
        def vwap_strategy_backtest(bars_1min, bars_15min=None):
            """Strategy function for backtest"""
            if return_bars:
                all_bars.extend(bars_1min)
            
            for bar in bars_1min:
                timestamp = bar['timestamp']
                timestamp_ms = int(timestamp.timestamp() * 1000)
                
                # Check for new trading day
                timestamp_et = timestamp.astimezone(tz)
                check_daily_reset(symbol, timestamp_et)
                
                # Inject complete OHLCV bar to preserve high/low ranges for ATR calculation
                inject_complete_bar(symbol, bar)
                
                # Update engine with bot position
                if symbol in state and 'position' in state[symbol]:
                    pos = state[symbol]['position']
                    
                    if pos.get('active') and engine.current_position is None:
                        engine.current_position = {
                            'symbol': symbol,
                            'side': pos['side'],
                            'quantity': pos.get('quantity', 1),
                            'entry_price': pos['entry_price'],
                            'entry_time': pos.get('entry_time', timestamp),
                            'stop_price': pos.get('stop_price'),
                            'target_price': pos.get('target_price')
                        }
                    elif not pos.get('active') and engine.current_position is not None:
                        engine._close_position(timestamp, bar['close'], 'bot_exit')
        
        # Run backtest
        results = engine.run_with_strategy(vwap_strategy_backtest)
        
        # Extract metrics using get_summary() method
        metrics = engine.metrics
        summary = metrics.get_summary()
        
        result_dict = {
            'total_pnl': summary['total_pnl'],
            'win_rate': summary['win_rate'],
            'profit_factor': summary['profit_factor'],
            'sharpe_ratio': summary['sharpe_ratio'],
            'max_drawdown': summary['max_drawdown_dollars'],
            'total_trades': summary['total_trades'],
            'winning_trades': len([t for t in metrics.trades if t.pnl > 0]),
            'losing_trades': len([t for t in metrics.trades if t.pnl < 0]),
            'avg_win': summary['average_win'],
            'avg_loss': summary['average_loss'],
            'largest_win': max([t.pnl for t in metrics.trades]) if metrics.trades else 0,
            'largest_loss': min([t.pnl for t in metrics.trades]) if metrics.trades else 0
        }
        
        logger.info(f"Backtest completed: {result_dict['total_trades']} trades, ${result_dict['total_pnl']:+,.2f}")
        
        # Save RL experiences after backtest completion
        try:
            if rl_brain is not None and hasattr(rl_brain, 'save_experience'):
                rl_brain.save_experience()
                logger.debug("Signal RL experiences saved")
        except Exception as save_error:
            logger.warning(f"Failed to save signal RL experiences: {save_error}")
        
        if return_bars:
            return result_dict, all_bars
        else:
            return result_dict
        
    except Exception as e:
        import traceback
        logger.error(f"Backtest failed with params {params}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_result = {
            'total_pnl': -99999,
            'win_rate': 0,
            'profit_factor': 0,
            'sharpe_ratio': -999,
            'max_drawdown': 99999,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0
        }
        
        if return_bars:
            return error_result, []
        else:
            return error_result
        
    finally:
        # Restore original config values
        for key, value in original_values.items():
            setattr(cfg, key, value)


def run_backtest(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run backtesting mode - completely independent of broker API.
    Uses historical data to replay market conditions and simulate trading.
    
    This backtest environment:
    - Loads signal RL from data/signal_experience.json
    - Uses pattern matching for signal detection
    - Handles all market regimes
    - Follows UTC maintenance and flatten rules
    - Executes all trade management logic
    - Everything the live bot does
    
    Args:
        args: Parsed command-line arguments from argparse
        
    Returns:
        Dictionary with backtest performance metrics
    """
    logger = logging.getLogger('backtest')
    logger.info("="*60)
    logger.info("STARTING BACKTEST MODE (Development Environment)")
    logger.info("Backtesting does NOT use broker API - runs on historical data only")
    logger.info("="*60)
    
    # Set backtest mode environment variable
    os.environ['BOT_BACKTEST_MODE'] = 'true'
    
    # Load configuration
    bot_config = load_config(backtest_mode=True)
    
    # Override symbol if specified
    if args.symbol:
        bot_config.instrument = args.symbol
    
    # Determine date range
    tz = pytz.timezone(bot_config.timezone)
    
    if args.start and args.end:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    elif args.days:
        end_date = datetime.now(tz)
        start_date = end_date - timedelta(days=args.days)
    else:
        # Default: last 7 days
        end_date = datetime.now(tz)
        start_date = end_date - timedelta(days=7)
        
    # Create backtest configuration
    data_path = args.data_path if args.data_path else os.path.join(PROJECT_ROOT, "data/historical_data")
    
    backtest_config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_equity=args.initial_equity,
        symbols=[args.symbol] if args.symbol else [bot_config.instrument],
        data_path=data_path,
        use_tick_data=args.use_tick_data
    )
    
    logger.info(f"Backtest Configuration:")
    logger.info(f"  Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"  Initial Equity: ${backtest_config.initial_equity:,.2f}")
    logger.info(f"  Symbols: {', '.join(backtest_config.symbols)}")
    logger.info(f"  Data Path: {backtest_config.data_path}")
    logger.info(f"  Replay Mode: {'Tick-by-tick' if args.use_tick_data else 'Bar-by-bar (1-minute bars)'}")
    
    # Create backtest engine
    bot_config_dict = bot_config.to_dict()
    engine = BacktestEngine(backtest_config, bot_config_dict)
    
    # Initialize RL brain and bot module
    rl_brain, bot_module = initialize_rl_brains_for_backtest()
    
    # Import bot functions from the loaded module
    initialize_state = bot_module.initialize_state
    on_tick = bot_module.on_tick
    check_for_signals = bot_module.check_for_signals
    check_exit_conditions = bot_module.check_exit_conditions
    check_daily_reset = bot_module.check_daily_reset
    state = bot_module.state
    
    # Initialize bot state for backtesting
    symbol = bot_config_dict['instrument']
    initialize_state(symbol)
    
    # Create a simple object to hold RL brain reference for tracking
    class BotRLReferences:
        def __init__(self):
            self.signal_rl = rl_brain
    
    # Set bot instance for RL tracking
    bot_ref = BotRLReferences()
    engine.set_bot_instance(bot_ref)
    
    # Use Eastern timezone for daily reset checks (follows production rules)
    eastern_tz = pytz.timezone("US/Eastern")
    
    def vwap_strategy_backtest(bars_1min: List[Dict[str, Any]], bars_15min: List[Dict[str, Any]]) -> None:
        """
        Actual VWAP Bounce strategy integrated with backtest engine.
        Processes historical data through the real bot logic.
        
        This executes:
        - Signal RL for confidence scoring
        - Pattern matching for signal detection
        - Regime detection for market adaptation
        - All trade management (stops, targets, breakeven, trailing)
        - UTC maintenance and flatten rules
        """
        for bar in bars_1min:
            # Extract bar data
            timestamp = bar['timestamp']
            price = bar['close']
            volume = bar['volume']
            timestamp_ms = int(timestamp.timestamp() * 1000)
            
            # Check for new trading day (resets daily counters following production rules)
            timestamp_eastern = timestamp.astimezone(eastern_tz)
            check_daily_reset(symbol, timestamp_eastern)
            
            # Process tick through actual bot logic
            # This includes all signal detection, pattern matching, regime handling
            on_tick(symbol, price, volume, timestamp_ms)
            
            # Check for entry signals after each bar
            # Uses RL confidence, pattern matching, and regime-aware logic
            check_for_signals(symbol)
            
            # Check for exit signals
            # Handles stops, targets, breakeven, trailing, time decay
            check_exit_conditions(symbol)
            
            # Update backtest engine with current position from bot state
            if symbol in state and 'position' in state[symbol]:
                pos = state[symbol]['position']
                
                # If bot has active position and backtest engine doesn't have it, record it
                if pos.get('active') and engine.current_position is None:
                    engine.current_position = {
                        'symbol': symbol,
                        'side': pos['side'],
                        'quantity': pos.get('quantity', 1),
                        'entry_price': pos['entry_price'],
                        'entry_time': pos.get('entry_time', timestamp),
                        'stop_price': pos.get('stop_price'),
                        'target_price': pos.get('target_price')
                    }
                    logger.info(f"Backtest: {pos['side'].upper()} position entered at {pos['entry_price']}")
                    
                # If bot closed position (active=False), close it in backtest engine too
                elif not pos.get('active') and engine.current_position is not None:
                    exit_price = price
                    exit_time = timestamp
                    exit_reason = 'bot_exit'
                    engine._close_position(exit_time, exit_price, exit_reason)
                    logger.info(f"Backtest: Position closed at {exit_price}, reason: {exit_reason}")
        
    # Run backtest with integrated strategy
    results = engine.run_with_strategy(vwap_strategy_backtest)
    
    # Save RL experiences after backtest completion
    print("\nSaving RL experiences...")
    try:
        if rl_brain is not None and hasattr(rl_brain, 'save_experience'):
            rl_brain.save_experience()
            print("✅ Signal RL experiences saved")
    except Exception as e:
        print(f"⚠️ Failed to save signal RL experiences: {e}")
    
    # Generate report
    report_gen = ReportGenerator(engine.metrics)
    
    # Track RL learning progress
    print("\n" + "="*60)
    print("RL BRAIN LEARNING SUMMARY")
    print("="*60)
    
    # Read the experience files directly
    try:
        import json
        signal_exp_file = os.path.join(PROJECT_ROOT, "data/signal_experience.json")
        with open(signal_exp_file, 'r') as f:
            signal_data = json.load(f)
            signal_count = len(signal_data['experiences'])
            signal_wins = len([e for e in signal_data['experiences'] if e['reward'] > 0])
            signal_losses = len([e for e in signal_data['experiences'] if e['reward'] < 0])
            signal_wr = (signal_wins / signal_count * 100) if signal_count > 0 else 0
            
            print(f"[SIGNALS] {signal_count} total experiences")
            print(f"  Wins: {signal_wins} | Losses: {signal_losses} | Win Rate: {signal_wr:.1f}%")
    except Exception as e:
        print(f"Could not load signal experiences: {e}")
        
    print("="*60)
    
    # Print results to console
    logger.info("\n" + "="*60)
    logger.info("BACKTEST RESULTS")
    logger.info("="*60)
    logger.info(report_gen.generate_trade_breakdown())
    logger.info("\n")
    
    # Save report if requested
    if args.report:
        report_gen.save_report(args.report)
        logger.info(f"Report saved to: {args.report}")
    
    logger.info("="*60)
    logger.info("BACKTEST COMPLETE")
    logger.info("="*60)
    
    return results


def main():
    """Main entry point for development backtesting"""
    args = parse_arguments()
    
    # Setup logging
    config_dict = {'log_directory': os.path.join(PROJECT_ROOT, 'logs')}
    logger = setup_logging(config_dict)
    
    # Set log level
    logger.setLevel(getattr(logging, args.log_level))
    
    logger.info("="*60)
    logger.info("VWAP Bounce Bot - Development Backtest Environment")
    logger.info("="*60)
    logger.info("Features:")
    logger.info("  ✅ Signal RL loaded from data/signal_experience.json")
    logger.info("  ✅ Pattern matching for signal detection")
    logger.info("  ✅ Regime detection and adaptation")
    logger.info("  ✅ All trade management (stops, targets, breakeven, trailing)")
    logger.info("  ✅ UTC maintenance and flatten rules")
    logger.info("  ✅ Everything the live bot does")
    logger.info("="*60 + "\n")
    
    # Run backtest
    try:
        results = run_backtest(args)
        
        # Exit with success/failure based on results
        if results and results.get('total_trades', 0) > 0:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
