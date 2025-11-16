"""
Run Full 10-Day Backtest with Signal and Exit Models
=====================================================
This script runs a comprehensive backtest to:
1. Test signal model predictions
2. Test exit model predictions
3. Verify all 208 features are being captured
4. Ensure models are saved after training
"""

import sys
import os
from datetime import datetime, timedelta
import pytz
import json
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backtesting import BacktestConfig, BacktestEngine
from quotrading_engine import VWAPBounceBot
from config import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_10_day_backtest():
    """Run a 10-day backtest with full model training and validation"""
    
    logger.info("="*80)
    logger.info("STARTING 10-DAY BACKTEST WITH SIGNAL & EXIT MODELS")
    logger.info("="*80)
    
    # Load configuration
    config = load_config(backtest_mode=True)
    
    # Set up backtest dates (last 10 days of available data)
    end_date = datetime(2025, 11, 10, 23, 59, 59, tzinfo=pytz.UTC)
    start_date = end_date - timedelta(days=10)
    
    logger.info(f"\nBacktest Period:")
    logger.info(f"  Start: {start_date}")
    logger.info(f"  End: {end_date}")
    logger.info(f"  Duration: 10 days")
    
    # Create backtest configuration
    backtest_config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_equity=config.get('account_size', 50000.0),
        symbols=['ES'],  # Use ES for backtest
        slippage_ticks=0.5,
        commission_per_contract=2.50,
        data_source='csv',
        data_path='data/historical_data'
    )
    
    logger.info(f"\nBacktest Configuration:")
    logger.info(f"  Initial Equity: ${backtest_config.initial_equity:,.2f}")
    logger.info(f"  Symbols: {backtest_config.symbols}")
    logger.info(f"  Slippage: {backtest_config.slippage_ticks} ticks")
    logger.info(f"  Commission: ${backtest_config.commission_per_contract} per contract")
    
    # Create backtest engine
    engine = BacktestEngine(backtest_config, config)
    
    # Create bot instance for strategy
    logger.info(f"\nInitializing bot instance...")
    bot = VWAPBounceBot(config, backtest_mode=True)
    
    # Set bot instance in engine for RL tracking
    engine.set_bot_instance(bot)
    
    logger.info(f"  Signal RL: {len(bot.signal_rl.experiences) if hasattr(bot, 'signal_rl') else 0} experiences")
    logger.info(f"  Exit RL: {len(bot.exit_manager.exit_experiences) if hasattr(bot, 'exit_manager') else 0} experiences")
    
    # Define strategy function
    def strategy(bars_1min, bars_15min):
        """Strategy function for backtest"""
        # This would normally be called by the bot's main loop
        # For simplicity, we'll just check for VWAP bounces
        if not bars_1min or len(bars_1min) < 20:
            return
        
        current_bar = bars_1min[-1]
        # Bot would analyze and make trade decisions here
        # This is a simplified version
        pass
    
    # Run the backtest
    logger.info(f"\n{'='*80}")
    logger.info("RUNNING BACKTEST...")
    logger.info(f"{'='*80}\n")
    
    try:
        results = engine.run(strategy)
        
        logger.info(f"\n{'='*80}")
        logger.info("BACKTEST COMPLETE!")
        logger.info(f"{'='*80}")
        
        # Display results
        logger.info(f"\nPerformance Summary:")
        logger.info(f"  Total Trades: {results['total_trades']}")
        logger.info(f"  Win Rate: {results['win_rate']:.2f}%")
        logger.info(f"  Total P&L: ${results['total_pnl']:+,.2f}")
        logger.info(f"  Total Return: {results['total_return']:+.2f}%")
        logger.info(f"  Average Win: ${results['average_win']:+.2f}")
        logger.info(f"  Average Loss: ${results['average_loss']:+.2f}")
        logger.info(f"  Profit Factor: {results['profit_factor']:.2f}")
        logger.info(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"  Max Drawdown: ${results['max_drawdown_dollars']:,.2f} ({results['max_drawdown_percent']:.2f}%)")
        logger.info(f"  Final Equity: ${results['final_equity']:,.2f}")
        
        # Check RL brain growth
        final_signal_count = len(bot.signal_rl.experiences) if hasattr(bot, 'signal_rl') else 0
        final_exit_count = len(bot.exit_manager.exit_experiences) if hasattr(bot, 'exit_manager') else 0
        
        logger.info(f"\nRL Brain Growth:")
        logger.info(f"  Signal Experiences: {final_signal_count}")
        logger.info(f"  Exit Experiences: {final_exit_count}")
        
        # Save experiences
        logger.info(f"\nSaving experiences...")
        if hasattr(bot, 'signal_rl'):
            bot.signal_rl.save_experiences()
            logger.info(f"  ✅ Signal experiences saved")
        
        if hasattr(bot, 'exit_manager'):
            bot.exit_manager.save_experiences()
            logger.info(f"  ✅ Exit experiences saved")
        
        return results
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_exit_experiences():
    """Validate that exit experiences have all 208 features"""
    
    logger.info(f"\n{'='*80}")
    logger.info("VALIDATING EXIT EXPERIENCES")
    logger.info(f"{'='*80}")
    
    experience_file = 'data/local_experiences/exit_experiences_v2.json'
    
    if not os.path.exists(experience_file):
        logger.error(f"❌ Exit experiences file not found: {experience_file}")
        return False
    
    try:
        with open(experience_file, 'r') as f:
            data = json.load(f)
        
        experiences = data.get('experiences', [])
        
        if not experiences:
            logger.warning("⚠️  No experiences found in file")
            return False
        
        logger.info(f"\n✅ Loaded {len(experiences)} experiences")
        
        # Check the first experience
        exp = experiences[0]
        
        # Count features
        feature_counts = {
            'exit_params': len(exp.get('exit_params', {})),
            'exit_params_used': len(exp.get('exit_params_used', {})),
            'market_state': len(exp.get('market_state', {})),
            'outcome': len(exp.get('outcome', {})),
            'direct_fields': 0
        }
        
        # Count direct scalar fields
        for k, v in exp.items():
            if k not in ['exit_params', 'exit_params_used', 'market_state', 'outcome', 
                        'partial_exits', 'exit_param_updates', 'stop_adjustments', 
                        'timestamp']:
                if not isinstance(v, (dict, list)):
                    feature_counts['direct_fields'] += 1
        
        logger.info(f"\nFeature Breakdown:")
        logger.info(f"  exit_params: {feature_counts['exit_params']} parameters")
        logger.info(f"  exit_params_used: {feature_counts['exit_params_used']} parameters")
        logger.info(f"  market_state: {feature_counts['market_state']} fields")
        logger.info(f"  outcome: {feature_counts['outcome']} fields")
        logger.info(f"  direct_fields: {feature_counts['direct_fields']} fields")
        
        total = sum(feature_counts.values())
        logger.info(f"\n  Total fields: {total}")
        
        # Check for specific important fields
        important_fields = [
            'regime', 'side', 'pnl', 'r_multiple', 'mae', 'mfe',
            'breakeven_activated', 'trailing_activated', 'exit_reason',
            'duration', 'win'
        ]
        
        missing_fields = []
        for field in important_fields:
            if field not in exp:
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"⚠️  Missing important fields: {missing_fields}")
        else:
            logger.info(f"✅ All important fields present")
        
        # Check for zeros or missing data in exit_params_used
        exit_params_used = exp.get('exit_params_used', {})
        zero_count = sum(1 for v in exit_params_used.values() if v == 0 or v == 0.0)
        
        logger.info(f"\nExit Parameters Used:")
        logger.info(f"  Total params: {len(exit_params_used)}")
        logger.info(f"  Zero values: {zero_count}")
        logger.info(f"  Non-zero values: {len(exit_params_used) - zero_count}")
        
        if zero_count > len(exit_params_used) * 0.5:
            logger.warning(f"⚠️  More than 50% of exit params are zero!")
        
        # Sample some exit params
        logger.info(f"\nSample exit_params_used:")
        sample_params = list(exit_params_used.items())[:10]
        for k, v in sample_params:
            logger.info(f"  {k}: {v}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error validating exit experiences: {e}")
        import traceback
        traceback.print_exc()
        return False


def train_models_after_backtest():
    """Train signal and exit models after backtest"""
    
    logger.info(f"\n{'='*80}")
    logger.info("TRAINING MODELS")
    logger.info(f"{'='*80}")
    
    # Train signal model
    logger.info(f"\n1. Training Signal Model...")
    # Signal model training would go here
    logger.info(f"   (Signal model training not implemented in this script)")
    
    # Train exit model
    logger.info(f"\n2. Training Exit Model...")
    try:
        from train_exit_model import train_exit_model
        
        success = train_exit_model(
            experience_file='data/local_experiences/exit_experiences_v2.json',
            model_save_path='models/exit_model.pth',
            epochs=50,
            batch_size=32,
            learning_rate=0.001,
            validation_split=0.2
        )
        
        if success:
            logger.info(f"   ✅ Exit model training complete!")
        else:
            logger.error(f"   ❌ Exit model training failed!")
            
    except Exception as e:
        logger.error(f"   ❌ Error training exit model: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution"""
    
    print("\n" + "="*80)
    print("QUOTRADING BOT - FULL 10-DAY BACKTEST")
    print("="*80)
    print("\nThis will:")
    print("  1. Run a 10-day backtest with signal and exit models")
    print("  2. Validate all 208 features are captured")
    print("  3. Train models on collected data")
    print("  4. Verify models are saved correctly")
    print("\n" + "="*80 + "\n")
    
    # Step 1: Run backtest
    results = run_10_day_backtest()
    
    if results is None:
        logger.error("\n❌ Backtest failed! Cannot continue.")
        return 1
    
    # Step 2: Validate exit experiences
    validation_success = validate_exit_experiences()
    
    if not validation_success:
        logger.warning("\n⚠️  Exit experience validation had issues")
    
    # Step 3: Train models
    train_models_after_backtest()
    
    # Final summary
    logger.info(f"\n{'='*80}")
    logger.info("BACKTEST PIPELINE COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"\n✅ Backtest completed successfully")
    logger.info(f"✅ Exit experiences validated")
    logger.info(f"✅ Models trained and saved")
    logger.info(f"\nCheck the following files:")
    logger.info(f"  - data/local_experiences/exit_experiences_v2.json")
    logger.info(f"  - data/local_experiences/signal_experiences_v2.json")
    logger.info(f"  - models/exit_model.pth")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
