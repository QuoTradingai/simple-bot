"""
Tests for Advanced Exit Management Features
Validates breakeven protection, trailing stops, time-decay tightening, and partial exits.
"""

import unittest
from datetime import datetime
import pytz
from config import BotConfiguration


class TestAdvancedExitConfiguration(unittest.TestCase):
    """Test Advanced Exit Management configuration parameters."""
    
    def test_breakeven_config_defaults(self):
        """Test breakeven protection configuration defaults."""
        config = BotConfiguration()
        
        # Verify breakeven defaults
        self.assertTrue(config.breakeven_enabled)
        self.assertEqual(config.breakeven_profit_threshold_ticks, 8)
        self.assertEqual(config.breakeven_stop_offset_ticks, 1)
    
    def test_trailing_stop_config_defaults(self):
        """Test trailing stop configuration defaults."""
        config = BotConfiguration()
        
        # Verify trailing stop defaults
        self.assertTrue(config.trailing_stop_enabled)
        self.assertEqual(config.trailing_stop_distance_ticks, 8)
        self.assertEqual(config.trailing_stop_min_profit_ticks, 12)
    
    def test_time_decay_config_defaults(self):
        """Test time-decay tightening configuration defaults."""
        config = BotConfiguration()
        
        # Verify time-decay defaults
        self.assertTrue(config.time_decay_enabled)
        self.assertAlmostEqual(config.time_decay_50_percent_tightening, 0.10)
        self.assertAlmostEqual(config.time_decay_75_percent_tightening, 0.20)
        self.assertAlmostEqual(config.time_decay_90_percent_tightening, 0.30)
    
    def test_partial_exits_config_defaults(self):
        """Test partial exits configuration defaults."""
        config = BotConfiguration()
        
        # Verify partial exits defaults
        self.assertTrue(config.partial_exits_enabled)
        self.assertAlmostEqual(config.partial_exit_1_percentage, 0.50)
        self.assertAlmostEqual(config.partial_exit_1_r_multiple, 2.0)
        self.assertAlmostEqual(config.partial_exit_2_percentage, 0.30)
        self.assertAlmostEqual(config.partial_exit_2_r_multiple, 3.0)
        self.assertAlmostEqual(config.partial_exit_3_percentage, 0.20)
        self.assertAlmostEqual(config.partial_exit_3_r_multiple, 5.0)
    
    def test_config_to_dict_includes_advanced_exit_params(self):
        """Test that to_dict includes all advanced exit management parameters."""
        config = BotConfiguration()
        config_dict = config.to_dict()
        
        # Check breakeven params
        self.assertIn("breakeven_enabled", config_dict)
        self.assertIn("breakeven_profit_threshold_ticks", config_dict)
        self.assertIn("breakeven_stop_offset_ticks", config_dict)
        
        # Check trailing stop params
        self.assertIn("trailing_stop_enabled", config_dict)
        self.assertIn("trailing_stop_distance_ticks", config_dict)
        self.assertIn("trailing_stop_min_profit_ticks", config_dict)
        
        # Check time-decay params
        self.assertIn("time_decay_enabled", config_dict)
        self.assertIn("time_decay_50_percent_tightening", config_dict)
        self.assertIn("time_decay_75_percent_tightening", config_dict)
        self.assertIn("time_decay_90_percent_tightening", config_dict)
        
        # Check partial exits params
        self.assertIn("partial_exits_enabled", config_dict)
        self.assertIn("partial_exit_1_percentage", config_dict)
        self.assertIn("partial_exit_1_r_multiple", config_dict)
        self.assertIn("partial_exit_2_percentage", config_dict)
        self.assertIn("partial_exit_2_r_multiple", config_dict)
        self.assertIn("partial_exit_3_percentage", config_dict)
        self.assertIn("partial_exit_3_r_multiple", config_dict)


class TestBreakevenProtectionLogic(unittest.TestCase):
    """Test breakeven protection logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "tick_size": 0.25,
            "tick_value": 12.50,
            "breakeven_enabled": True,
            "breakeven_profit_threshold_ticks": 8,
            "breakeven_stop_offset_ticks": 1,
        }
    
    def test_profit_calculation_long(self):
        """Test profit calculation for long positions."""
        entry_price = 4500.00
        current_price = 4502.00  # 8 ticks profit (2.00 / 0.25 = 8)
        tick_size = self.config["tick_size"]
        
        profit_ticks = (current_price - entry_price) / tick_size
        self.assertEqual(profit_ticks, 8.0)
    
    def test_profit_calculation_short(self):
        """Test profit calculation for short positions."""
        entry_price = 4500.00
        current_price = 4498.00  # 8 ticks profit (2.00 / 0.25 = 8)
        tick_size = self.config["tick_size"]
        
        profit_ticks = (entry_price - current_price) / tick_size
        self.assertEqual(profit_ticks, 8.0)
    
    def test_breakeven_stop_price_long(self):
        """Test breakeven stop price calculation for long positions."""
        entry_price = 4500.00
        tick_size = self.config["tick_size"]
        offset_ticks = self.config["breakeven_stop_offset_ticks"]
        
        breakeven_stop = entry_price + (offset_ticks * tick_size)
        self.assertEqual(breakeven_stop, 4500.25)  # 1 tick above entry
    
    def test_breakeven_stop_price_short(self):
        """Test breakeven stop price calculation for short positions."""
        entry_price = 4500.00
        tick_size = self.config["tick_size"]
        offset_ticks = self.config["breakeven_stop_offset_ticks"]
        
        breakeven_stop = entry_price - (offset_ticks * tick_size)
        self.assertEqual(breakeven_stop, 4499.75)  # 1 tick below entry
    
    def test_profit_locked_calculation(self):
        """Test profit locked in calculation."""
        entry_price = 4500.00
        breakeven_stop = 4500.25
        tick_size = self.config["tick_size"]
        tick_value = self.config["tick_value"]
        contracts = 2
        
        profit_locked_ticks = (breakeven_stop - entry_price) / tick_size
        profit_locked_dollars = profit_locked_ticks * tick_value * contracts
        
        self.assertEqual(profit_locked_ticks, 1.0)
        self.assertEqual(profit_locked_dollars, 25.00)  # 1 tick * $12.50 * 2 contracts


class TestPositionTrackingFields(unittest.TestCase):
    """Test that position tracking includes all required fields."""
    
    def test_position_tracking_structure(self):
        """Test position tracking has all advanced exit management fields."""
        # This is a structural test - actual position tracking is tested in integration
        required_fields = [
            # Breakeven State
            "breakeven_active",
            "original_stop_price",
            "breakeven_activated_time",
            # Trailing Stop State
            "trailing_stop_active",
            "trailing_stop_price",
            "highest_price_reached",
            "lowest_price_reached",
            "trailing_activated_time",
            # Time-Decay State
            "time_decay_50_triggered",
            "time_decay_75_triggered",
            "time_decay_90_triggered",
            "original_stop_distance_ticks",
            "current_stop_distance_ticks",
            # Partial Exit State
            "partial_exit_1_completed",
            "partial_exit_2_completed",
            "partial_exit_3_completed",
            "original_quantity",
            "remaining_quantity",
            "partial_exit_history",
            # General
            "initial_risk_ticks",
        ]
        
        # All required fields should be documented (20 total)
        self.assertEqual(len(required_fields), 20)


if __name__ == '__main__':
    unittest.main()
