#!/usr/bin/env python
"""
Demo script showing configuration management and broker abstraction.
Demonstrates how to use the new config.py and broker_interface.py modules.
"""

import logging
from config import load_config, log_config
from broker_interface import create_broker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_configuration():
    """Demonstrate configuration loading and validation."""
    print("\n" + "=" * 70)
    print("CONFIGURATION MANAGEMENT DEMO")
    print("=" * 70)
    
    # Load development configuration
    print("\n1. Loading development configuration...")
    config = load_config("development")
    
    # Log configuration safely
    log_config(config, logger)
    
    # Show that we can access config values
    print("\n2. Configuration values:")
    print(f"   Instrument: {config.instrument}")
    print(f"   Risk per trade: {config.risk_per_trade * 100:.1f}%")
    print(f"   Max contracts: {config.max_contracts}")
    print(f"   Broker type: {config.broker_type}")
    print(f"   Environment: {config.environment}")
    
    # Demonstrate validation
    print("\n3. Configuration validation:")
    try:
        config.validate()
        print("   ✓ Configuration is valid")
    except ValueError as e:
        print(f"   ✗ Configuration invalid: {e}")
    
    return config


def demo_broker_abstraction(config):
    """Demonstrate broker abstraction layer."""
    print("\n" + "=" * 70)
    print("BROKER ABSTRACTION DEMO")
    print("=" * 70)
    
    # Create broker based on config
    print(f"\n1. Creating {config.broker_type} broker...")
    broker = create_broker(
        broker_type=config.broker_type,
        api_token=config.api_token,
        starting_equity=config.mock_starting_equity
    )
    print(f"   ✓ Created: {type(broker).__name__}")
    
    # Connect to broker
    print("\n2. Connecting to broker...")
    if broker.connect():
        print("   ✓ Connected successfully")
    else:
        print("   ✗ Connection failed")
        return
    
    # Check account equity
    print("\n3. Checking account equity...")
    equity = broker.get_account_equity()
    print(f"   Account equity: ${equity:,.2f}")
    
    # Place a test order
    print("\n4. Placing test market order...")
    order = broker.place_market_order(config.instrument, "BUY", 1)
    if order:
        print(f"   ✓ Order placed: {order.get('order_id')}")
        print(f"     Status: {order.get('status')}")
        print(f"     Filled: {order.get('filled_quantity')} contracts")
    else:
        print("   ✗ Order failed")
    
    # Check position
    print("\n5. Checking position...")
    position = broker.get_position_quantity(config.instrument)
    print(f"   Current position: {position} contracts")
    
    # Place exit order
    if position != 0:
        print("\n6. Placing exit order...")
        side = "SELL" if position > 0 else "BUY"
        exit_order = broker.place_market_order(config.instrument, side, abs(position))
        if exit_order:
            print(f"   ✓ Exit order placed: {exit_order.get('order_id')}")
        else:
            print("   ✗ Exit order failed")
        
        # Check position again
        position = broker.get_position_quantity(config.instrument)
        print(f"   Position after exit: {position} contracts")
    
    # Disconnect
    print("\n7. Disconnecting from broker...")
    broker.disconnect()
    print("   ✓ Disconnected")


def demo_environment_switching():
    """Demonstrate switching between environments."""
    print("\n" + "=" * 70)
    print("ENVIRONMENT SWITCHING DEMO")
    print("=" * 70)
    
    environments = ["development", "staging", "production"]
    
    for env in environments:
        print(f"\n{env.upper()} environment:")
        try:
            config = load_config(env)
            print(f"  Broker: {config.broker_type}")
            print(f"  Dry run: {config.dry_run}")
            print(f"  Max trades: {config.max_trades_per_day}")
            
            if env == "production":
                print(f"  API token: {'configured' if config.api_token else 'NOT CONFIGURED'}")
        except ValueError as e:
            print(f"  ✗ Configuration error: {e}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("VWAP BOUNCE BOT - CONFIGURATION & BROKER DEMO")
    print("=" * 70)
    
    try:
        # Demo 1: Configuration management
        config = demo_configuration()
        
        # Demo 2: Broker abstraction
        demo_broker_abstraction(config)
        
        # Demo 3: Environment switching
        demo_environment_switching()
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nKey takeaways:")
        print("  ✓ Configuration is type-safe and validated")
        print("  ✓ Can switch environments without code changes")
        print("  ✓ Broker abstraction allows testing without SDK")
        print("  ✓ Strategy code is broker-agnostic")
        print("  ✓ Ready for TopStep SDK integration")
        print()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
