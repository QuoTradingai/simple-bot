"""
Exit Neural Network Model - 79 BACKTEST-LEARNABLE PARAMETERS
Predicts optimal exit parameters based on market context
Comprehensive exit management covering all trading scenarios
"""
import torch
import torch.nn as nn
import sys
import os

# Import parameter definitions
sys.path.append(os.path.dirname(__file__))
from exit_params_config import EXIT_PARAMS, get_param_ranges, get_default_exit_params

class ExitParamsNet(nn.Module):
    """
    Neural network to predict optimal exit parameters
    
    Inputs (208 features - COMPLETE feature coverage from ALL JSON fields):
        exit_params_used (132): All exit parameters that were used in the trade
        market_state (9): atr, day_of_week, hour, recent_pnl, rsi, streak, vix, volume_ratio, vwap_distance
        root numeric (26): bars_until_breakeven, bars_until_trailing, bid_ask_spread_ticks, etc.
        encoded categorical (4): regime, side, exit_reason, session
        list aggregates (9): partial_exits, exit_param_updates, stop_adjustments (count, has_any, reserved)
        outcome numeric (28): atr_change_percent, avg_atr_during_trade, bars_held, contracts, etc.
        
    This captures EVERYTHING from the JSON experience so the model can learn from:
    - What exit parameters were previously used (exit_params_used)
    - Market conditions (market_state)
    - Trade performance (outcome)
    - Trade context (root fields)
    - List-based features (partial exits, updates, adjustments)
    
    Outputs (132 exit parameters - to predict):
        All exit parameters from exit_params_config.py
    """
    
    def __init__(self, input_size=208, hidden_size=256):
        super(ExitParamsNet, self).__init__()
        
        # Architecture: 208 inputs → 256 → 256 → 256 → 132 outputs
        # 208 inputs: ALL features from JSON (exit_params_used + market + outcome + root)
        # 132 outputs: comprehensive exit parameters to predict
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(256, 132),  # 132 exit parameters to predict
            nn.Sigmoid()  # Output 0-1, will denormalize later
        )
    
    def forward(self, x):
        return self.network(x)


def denormalize_exit_params(normalized_params):
    """
    Convert normalized [0-1] outputs back to real exit parameters
    
    Args:
        normalized_params: Tensor of shape [batch, 68] with values 0-1
    
    Returns:
        dict with actual exit parameter values (59 backtest-learnable params)
    """
    # Get ranges from central config
    ranges = get_param_ranges()
    param_names = list(EXIT_PARAMS.keys())
    
    # Get ranges from central config
    ranges = get_param_ranges()
    param_names = list(EXIT_PARAMS.keys())
    
    # Handle both single predictions and batches
    if len(normalized_params.shape) == 1:
        # Single prediction
        result = {}
        for i, name in enumerate(param_names):
            min_val, max_val = ranges[name]
            value = min_val + normalized_params[i].item() * (max_val - min_val)
            result[name] = value
        return result
    else:
        # Batch predictions
        results = []
        for batch_idx in range(normalized_params.shape[0]):
            result = {}
            for i, name in enumerate(param_names):
                min_val, max_val = ranges[name]
                value = min_val + normalized_params[batch_idx, i].item() * (max_val - min_val)
                result[name] = value
            results.append(result)
        return results


def normalize_exit_params(exit_params):
    """
    Normalize exit parameters to [0-1] range for training
    
    Args:
        exit_params: dict with exit parameter values
    
    Returns:
        list of 68 normalized values [0-1]
    """
    ranges = get_param_ranges()
    defaults = get_default_exit_params()
    param_names = list(EXIT_PARAMS.keys())
    
    normalized = []
    for name in param_names:
        min_val, max_val = ranges[name]
        # Use default if missing
        value = exit_params.get(name, defaults[name])
        norm = (value - min_val) / (max_val - min_val)
        norm = max(0.0, min(1.0, norm))  # Clip to [0, 1]
        normalized.append(norm)
    
    return normalized