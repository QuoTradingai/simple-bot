"""
Test License Expiration Handling
Tests the periodic license validation and graceful shutdown logic
"""
import sys
import os
from datetime import datetime, time as datetime_time
from unittest.mock import Mock, patch, MagicMock
import pytz

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock event loop module to avoid aiohttp dependency
sys.modules['event_loop'] = MagicMock()
sys.modules['error_recovery'] = MagicMock()
sys.modules['bid_ask_manager'] = MagicMock()
sys.modules['notifications'] = MagicMock()
sys.modules['signal_confidence'] = MagicMock()
sys.modules['regime_detection'] = MagicMock()
sys.modules['cloud_api'] = MagicMock()
sys.modules['broker_interface'] = MagicMock()
sys.modules['config'] = MagicMock()


class TestLicenseExpiration:
    """Test license expiration handling scenarios"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.eastern_tz = pytz.timezone('US/Eastern')
        
    def test_license_validation_success(self):
        """Test successful license validation"""
        from quotrading_engine import handle_license_check_event, bot_status
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "license_valid": True,
            "message": "Valid license"
        }
        
        with patch('requests.post', return_value=mock_response):
            with patch('quotrading_engine.cloud_api_client', MagicMock()):
                with patch('quotrading_engine.CONFIG', {"quotrading_license": "TEST-KEY"}):
                    # Should not raise exception
                    handle_license_check_event({})
                    
                    # Trading should remain enabled
                    assert bot_status.get("license_expired", False) == False
                    print("✅ License validation success test passed")
    
    def test_license_expired_immediate_stop(self):
        """Test immediate stop when license expires during normal trading hours"""
        from quotrading_engine import handle_license_check_event, bot_status, state
        
        # Reset bot status
        bot_status.clear()
        bot_status.update({
            "trading_enabled": True,
            "emergency_stop": False
        })
        
        # Mock expired license response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "license_valid": False,
            "message": "License expired"
        }
        
        # Mock current time - Wednesday at 2 PM ET (normal trading)
        mock_time = self.eastern_tz.localize(datetime(2024, 1, 10, 14, 0, 0))  # Wednesday
        
        with patch('requests.post', return_value=mock_response):
            with patch('quotrading_engine.cloud_api_client', MagicMock()):
                with patch('quotrading_engine.CONFIG', {"quotrading_license": "TEST-KEY"}):
                    with patch('quotrading_engine.get_current_time', return_value=mock_time):
                        with patch('quotrading_engine.get_trading_state', return_value='entry_window'):
                            with patch('quotrading_engine.broker', None):
                                # Run check
                                handle_license_check_event({})
                                
                                # Should stop immediately
                                assert bot_status["license_expired"] == True
                                assert bot_status["trading_enabled"] == False
                                assert bot_status["emergency_stop"] == True
                                print("✅ Immediate stop test passed")
    
    def test_license_expired_friday_delayed_stop(self):
        """Test delayed stop when license expires on Friday before market close"""
        from quotrading_engine import handle_license_check_event, bot_status
        
        # Reset bot status
        bot_status.clear()
        bot_status.update({
            "trading_enabled": True,
            "emergency_stop": False
        })
        
        # Mock expired license response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "license_valid": False,
            "message": "License expired"
        }
        
        # Mock current time - Friday at 3 PM ET (before close at 5 PM)
        mock_time = self.eastern_tz.localize(datetime(2024, 1, 12, 15, 0, 0))  # Friday
        
        with patch('requests.post', return_value=mock_response):
            with patch('quotrading_engine.cloud_api_client', MagicMock()):
                with patch('quotrading_engine.CONFIG', {
                    "quotrading_license": "TEST-KEY",
                    "flatten_time": datetime_time(16, 45),
                    "forced_flatten_time": datetime_time(17, 0)
                }):
                    with patch('quotrading_engine.get_current_time', return_value=mock_time):
                        with patch('quotrading_engine.get_trading_state', return_value='entry_window'):
                            with patch('quotrading_engine.broker', None):
                                # Run check
                                handle_license_check_event({})
                                
                                # Should NOT stop immediately - wait for market close
                                assert bot_status.get("license_expired") == True
                                assert bot_status.get("stop_at_market_close") == True
                                # Trading still enabled until market close
                                print("✅ Friday delayed stop test passed")
    
    def test_license_expired_maintenance_window_delayed_stop(self):
        """Test delayed stop when license expires during flatten mode (before maintenance)"""
        from quotrading_engine import handle_license_check_event, bot_status
        
        # Reset bot status
        bot_status.clear()
        bot_status.update({
            "trading_enabled": True,
            "emergency_stop": False
        })
        
        # Mock expired license response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "license_valid": False,
            "message": "License expired"
        }
        
        # Mock current time - Wednesday at 4:50 PM ET (flatten mode, before maintenance at 5 PM)
        mock_time = self.eastern_tz.localize(datetime(2024, 1, 10, 16, 50, 0))  # Wednesday
        
        with patch('requests.post', return_value=mock_response):
            with patch('quotrading_engine.cloud_api_client', MagicMock()):
                with patch('quotrading_engine.CONFIG', {
                    "quotrading_license": "TEST-KEY",
                    "flatten_time": datetime_time(16, 45),
                    "forced_flatten_time": datetime_time(17, 0)
                }):
                    with patch('quotrading_engine.get_current_time', return_value=mock_time):
                        with patch('quotrading_engine.get_trading_state', return_value='flatten_mode'):
                            with patch('quotrading_engine.broker', None):
                                # Run check
                                handle_license_check_event({})
                                
                                # Should NOT stop immediately - wait for maintenance
                                assert bot_status.get("license_expired") == True
                                assert bot_status.get("stop_at_maintenance") == True
                                print("✅ Maintenance window delayed stop test passed")
    
    def test_license_check_blocks_new_trades(self):
        """Test that expired license blocks new trades in safety check"""
        from quotrading_engine import check_safety_conditions, bot_status
        
        # Set license as expired
        bot_status.clear()
        bot_status["license_expired"] = True
        bot_status["license_expiry_reason"] = "License expired"
        
        # Check safety conditions
        is_safe, reason = check_safety_conditions("ES")
        
        # Should not be safe to trade
        assert is_safe == False
        assert "License expired" in reason
        print("✅ Safety check blocks trades when license expired")
    
    def test_license_validation_network_error(self):
        """Test that network errors don't stop trading"""
        from quotrading_engine import handle_license_check_event, bot_status
        import requests
        
        # Reset bot status
        bot_status.clear()
        bot_status.update({
            "trading_enabled": True,
            "emergency_stop": False
        })
        
        # Mock network timeout
        with patch('requests.post', side_effect=requests.Timeout("Connection timeout")):
            with patch('quotrading_engine.cloud_api_client', MagicMock()):
                with patch('quotrading_engine.CONFIG', {"quotrading_license": "TEST-KEY"}):
                    # Run check
                    handle_license_check_event({})
                    
                    # Should NOT stop trading on network error
                    assert bot_status.get("license_expired", False) == False
                    assert bot_status["trading_enabled"] == True
                    print("✅ Network error handling test passed")


def run_tests():
    """Run all tests"""
    test_suite = TestLicenseExpiration()
    
    print("=" * 70)
    print("TESTING LICENSE EXPIRATION HANDLING")
    print("=" * 70)
    
    # Test 1: Successful validation
    print("\n1. Testing successful license validation...")
    test_suite.setup_method()
    try:
        test_suite.test_license_validation_success()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 2: Immediate stop
    print("\n2. Testing immediate stop on expiration...")
    test_suite.setup_method()
    try:
        test_suite.test_license_expired_immediate_stop()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 3: Friday delayed stop
    print("\n3. Testing Friday delayed stop...")
    test_suite.setup_method()
    try:
        test_suite.test_license_expired_friday_delayed_stop()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 4: Maintenance window delayed stop
    print("\n4. Testing maintenance window delayed stop...")
    test_suite.setup_method()
    try:
        test_suite.test_license_expired_maintenance_window_delayed_stop()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 5: Safety check blocks trades
    print("\n5. Testing safety check blocks trades...")
    test_suite.setup_method()
    try:
        test_suite.test_license_check_blocks_new_trades()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test 6: Network error handling
    print("\n6. Testing network error handling...")
    test_suite.setup_method()
    try:
        test_suite.test_license_validation_network_error()
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
