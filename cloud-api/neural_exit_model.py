"""
Neural Exit Model for Cloud API
Loads exit_model.pth and provides exit parameter predictions
"""
import torch
import torch.nn as nn
import numpy as np
import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ExitParamsNet(nn.Module):
    """
    Neural network to predict optimal exit parameters
    64 input features → 6 exit parameters
    """
    
    def __init__(self, input_size=64):
        super(ExitParamsNet, self).__init__()
        
        self.network = nn.Sequential(
            # Layer 1: 64 → 128
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Layer 2: 128 → 64
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Output: 64 → 6
            nn.Linear(64, 6),
            nn.Sigmoid()  # 0-1 range, will denormalize
        )
    
    def forward(self, x):
        return self.network(x)


class NeuralExitPredictor:
    """
    Cloud-ready exit parameter predictor
    """
    
    def __init__(self, model_path: str = "exit_model.pth"):
        self.model = None
        self.model_path = model_path
        self.device = torch.device('cpu')
        
        if os.path.exists(model_path):
            self.load_model()
        else:
            logger.warning(f"⚠️  Exit model not found: {model_path}")
    
    def load_model(self):
        """Load trained exit model"""
        try:
            self.model = ExitParamsNet(input_size=64)
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.eval()
            logger.info(f"✅ Exit model loaded: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load exit model: {e}")
            self.model = None
    
    def prepare_features(self, state: Dict) -> np.ndarray:
        """
        Convert trade state to 64-feature vector
        MUST match train_exit_model.py feature order exactly
        """
        from datetime import datetime
        
        # Mappings
        regime_map = {
            'NORMAL': 0, 'NORMAL_TRENDING': 1, 'HIGH_VOL_TRENDING': 2,
            'HIGH_VOL_CHOPPY': 3, 'LOW_VOL_TRENDING': 4, 'LOW_VOL_RANGING': 5,
            'UNKNOWN': 0
        }
        session_map = {'Asia': 0, 'London': 1, 'NY': 2}
        outcome_map = {'WIN': 1, 'LOSS': 0}
        exit_reason_map = {
            'take_profit': 0, 'stop_loss': 1, 'trailing_stop': 2,
            'time_limit': 3, 'partial_exit': 4
        }
        
        # Extract timestamp features
        entry_hour = state.get('entry_hour', 12)
        entry_minute = state.get('entry_minute', 0)
        exit_hour = state.get('exit_hour', 12)
        exit_minute = state.get('exit_minute', 0)
        
        # Build 64-feature vector (EXACT order from train_exit_model.py)
        features = [
            # Market Context (8)
            regime_map.get(state.get('market_regime', 'NORMAL'), 0),  # 0
            state.get('rsi', 50.0),                                   # 1
            state.get('volume_ratio', 1.0),                           # 2
            state.get('atr', 2.0),                                    # 3
            state.get('vix', 15.0),                                   # 4
            float(state.get('volatility_regime_change', False)),      # 5
            state.get('volume_at_exit', 1.0),                         # 6
            state.get('market_state', 0),                             # 7
            
            # Trade Context (7)
            state.get('entry_confidence', 0.5),                       # 8
            float(state.get('side', 'LONG') == 'SHORT'),              # 9
            session_map.get(state.get('session', 'NY'), 2),           # 10
            state.get('bid_ask_spread_ticks', 0.5),                   # 11
            state.get('commission_cost', 0.0),                        # 12
            state.get('slippage_ticks', 0.0),                         # 13
            regime_map.get(state.get('regime', 'NORMAL'), 0),         # 14
            
            # Time Features (5)
            state.get('hour', 12),                                    # 15
            state.get('day_of_week', 0),                              # 16
            state.get('duration', 10.0),                              # 17
            state.get('time_in_breakeven_bars', 0),                   # 18
            state.get('bars_until_breakeven', 0),                     # 19
            
            # Performance Metrics (5)
            state.get('mae', 0.0),                                    # 20
            state.get('mfe', 0.0),                                    # 21
            state.get('max_r_achieved', 0.0),                         # 22
            state.get('min_r_achieved', 0.0),                         # 23
            state.get('r_multiple', 0.0),                             # 24
            
            # Exit Strategy State (7)
            float(state.get('breakeven_activated', False)),           # 25
            float(state.get('trailing_activated', False)),            # 26
            float(state.get('stop_hit', False)),                      # 27
            state.get('exit_param_update_count', 0),                  # 28
            state.get('stop_adjustment_count', 0),                    # 29
            state.get('rejected_partial_count', 0),                   # 30
            state.get('bars_until_trailing', 0),                      # 31
            
            # Results (5)
            state.get('pnl', 0.0),                                    # 32
            outcome_map.get(state.get('outcome', 'LOSS'), 0),         # 33
            float(state.get('win', False)),                           # 34
            exit_reason_map.get(state.get('exit_reason', 'stop_loss'), 1),  # 35
            state.get('max_profit_reached', 0.0),                     # 36
            
            # ADVANCED (8)
            state.get('atr_change_percent', 0.0),                     # 37
            state.get('avg_atr_during_trade', 2.0),                   # 38
            state.get('peak_r_multiple', 0.0),                        # 39
            state.get('profit_drawdown_from_peak', 0.0),              # 40
            state.get('high_volatility_bars', 0),                     # 41
            state.get('wins_in_last_5_trades', 0),                    # 42
            state.get('losses_in_last_5_trades', 0),                  # 43
            state.get('minutes_until_close', 240.0),                  # 44
            
            # TEMPORAL (5)
            entry_hour,                                               # 45
            entry_minute,                                             # 46
            exit_hour,                                                # 47
            exit_minute,                                              # 48
            state.get('bars_held', 0),                                # 49
            
            # POSITION TRACKING (3)
            state.get('entry_bar', 0),                                # 50
            state.get('exit_bar', 0),                                 # 51
            state.get('contracts', 1),                                # 52
            
            # TRADE CONTEXT (3)
            state.get('trade_number_in_session', 0),                  # 53
            state.get('cumulative_pnl_before_trade', 0.0),            # 54
            state.get('entry_price', 6500.0) / 10000.0,               # 55: normalized
            
            # PERFORMANCE (4)
            state.get('peak_unrealized_pnl', 0.0),                    # 56
            state.get('opportunity_cost', 0.0),                       # 57
            state.get('max_drawdown_percent', 0.0),                   # 58
            state.get('drawdown_bars', 0),                            # 59
            
            # STRATEGY MILESTONES (4)
            state.get('breakeven_activation_bar', 0),                 # 60
            state.get('trailing_activation_bar', 0),                  # 61
            state.get('duration_bars', 0),                            # 62
            float(state.get('held_through_sessions', False)),         # 63
        ]
        
        return np.array(features, dtype=np.float32)
    
    def denormalize_params(self, normalized_tensor):
        """Convert [0-1] outputs to actual exit parameters"""
        ranges = {
            'take_profit_pct': (0.4, 2.0),        # 0.4% - 2.0%
            'stop_loss_pct': (0.2, 1.5),          # 0.2% - 1.5%
            'time_limit_minutes': (10, 120),      # 10-120 minutes
            'trailing_stop_pct': (0.15, 0.8),     # 0.15% - 0.8%
            'break_even_pct': (0.1, 0.5),         # 0.1% - 0.5%
            'partial_take_pct': (0.3, 1.2),       # 0.3% - 1.2%
        }
        
        param_names = [
            'take_profit_pct',
            'stop_loss_pct',
            'time_limit_minutes',
            'trailing_stop_pct',
            'break_even_pct',
            'partial_take_pct'
        ]
        
        result = {}
        values = normalized_tensor.detach().numpy()
        
        for i, name in enumerate(param_names):
            min_val, max_val = ranges[name]
            result[name] = float(min_val + values[i] * (max_val - min_val))
        
        return result
    
    def predict(self, state: Dict) -> Dict:
        """
        Predict optimal exit parameters
        
        Returns:
            dict with 6 exit parameters
        """
        if self.model is None:
            # Fallback to conservative defaults
            return {
                'take_profit_pct': 1.0,
                'stop_loss_pct': 0.5,
                'time_limit_minutes': 60,
                'trailing_stop_pct': 0.3,
                'break_even_pct': 0.2,
                'partial_take_pct': 0.6
            }
        
        try:
            features = self.prepare_features(state)
            features_tensor = torch.from_numpy(features).float()
            
            with torch.no_grad():
                normalized_output = self.model(features_tensor)
            
            params = self.denormalize_params(normalized_output)
            return params
            
        except Exception as e:
            logger.error(f"Exit prediction failed: {e}")
            # Return conservative defaults
            return {
                'take_profit_pct': 1.0,
                'stop_loss_pct': 0.5,
                'time_limit_minutes': 60,
                'trailing_stop_pct': 0.3,
                'break_even_pct': 0.2,
                'partial_take_pct': 0.6
            }
