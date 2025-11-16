"""
Train Exit Neural Network on Historical Exit Experiences
Learns optimal exit parameters based on market context
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
from sklearn.model_selection import train_test_split
from neural_exit_model import ExitParamsNet, normalize_exit_params

class ExitDataset(Dataset):
    """Dataset of historical exit experiences"""
    
    def __init__(self, features, labels):
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


def load_exit_experiences():
    """Load exit experiences from JSON"""
    print("=" * 80)
    print("LOADING EXIT TRAINING DATA")
    print("=" * 80)
    
    with open('data/local_experiences/exit_experiences_v2.json') as f:
        data = json.load(f)
    
    experiences = data['experiences']
    print(f"Total exit experiences: {len(experiences):,}")
    
    # Filter to winning trades only (learn from success)
    winning_exits = [e for e in experiences if e.get('win', False)]
    print(f"Winning exits (learning targets): {len(winning_exits):,}")
    print(f"Win rate: {len(winning_exits)/len(experiences)*100:.1f}%")
    print()
    
    # Prepare features and labels
    features = []
    labels = []
    
    # Regime mapping
    regime_map = {
        'NORMAL': 0,
        'NORMAL_TRENDING': 0,
        'OVERBOUGHT': 1,
        'OVERSOLD': 1,
        'CHOPPY': 2,
        'HIGH_VOLUME': 0,
        'LOW_VOLUME': 0,
        'TRENDING': 0,
        'UNKNOWN': 0
    }
    
    side_map = {'LONG': 0, 'long': 0, 'SHORT': 1, 'short': 1}
    
    for exp in experiences:
        try:
            # Extract ALL fields directly (208 total: 66 outcome + 10 market_state + 132 exit_params)
            market_state = exp.get('market_state', {})
            outcome = exp.get('outcome', {})
            exit_params_current = exp.get('exit_params', {})
            # Extract ALL fields directly (208 total: 66 outcome + 10 market_state + 132 exit_params)
            market_state = exp.get('market_state', {})
            outcome = exp.get('outcome', {})
            exit_params_current = exp.get('exit_params', {})
            
            # Build feature vector from ALL 208 fields (normalized 0-1)
            # MARKET STATE (10 features)
            market_features = [
                market_state.get('rsi', 50.0) / 100.0,
                min(market_state.get('vix', 15.0) / 50.0, 1.0),
                min(market_state.get('atr', 2.0) / 10.0, 1.0),
                min(market_state.get('volume_ratio', 1.0) / 5.0, 1.0),
                market_state.get('hour', 12) / 24.0,
                market_state.get('day_of_week', 2) / 6.0,
                market_state.get('streak', 0) / 10.0,
                np.clip(market_state.get('recent_pnl', 0.0) / 1000.0, -1, 1),
                np.clip(market_state.get('vwap_distance', 0.0) / 50.0, -1, 1),
                np.clip(market_state.get('peak_pnl', 0.0) / 1000.0, 0, 1),
            ]
            
            # OUTCOME (66 features - all normalized) - use sorted keys for consistency
            outcome_features = []
            outcome_keys_order = sorted(outcome.keys())  # Use actual keys from JSON, sorted alphabetically
            
            # Normalize each outcome field
            for key in outcome_keys_order:
                val = outcome.get(key, 0.0)
                # Apply normalization based on field type
                if key in ['breakeven_activated', 'trailing_activated', 'stop_hit', 'held_through_sessions',
                          'volatility_regime_change', 'partial_1_triggered', 'partial_2_triggered', 'partial_3_triggered']:
                    outcome_features.append(float(val))  # Boolean 0/1
                elif key == 'exit_reason':
                    # Encode exit reason
                    exit_map = {'stop_loss': 0, 'target': 0.25, 'time': 0.5, 'partial': 0.75, 'trailing': 1.0,
                               'profit_drawdown': 0.2, 'sideways_market_exit': 0.3, 'volatility_spike': 0.4}
                    outcome_features.append(exit_map.get(val, 0))
                elif key in ['pnl', 'peak_pnl', 'cumulative_pnl_before_trade', 'daily_pnl_before_trade',
                            'peak_unrealized_pnl', 'opportunity_cost', 'net_profit_after_costs']:
                    outcome_features.append(np.clip(val / 1000.0, -1, 1))  # +/- $1000
                elif key in ['profit_ticks', 'initial_risk_ticks', 'profit_ticks_gross']:
                    outcome_features.append(np.clip(val / 100.0, -5, 5))  # +/- 100 ticks
                elif key in ['final_r_multiple', 'max_r_achieved', 'min_r_achieved', 'r_multiple', 'peak_r_multiple']:
                    outcome_features.append(np.clip(val / 10.0, -1, 1))  # +/- 10R
                elif key in ['entry_hour', 'exit_hour']:
                    outcome_features.append(val / 24.0)  # 0-1
                elif key in ['entry_minute', 'exit_minute']:
                    outcome_features.append(val / 60.0)  # 0-1
                elif key in ['duration', 'bars_held', 'duration_bars', 'bars_until_breakeven',
                            'time_in_breakeven_bars', 'bars_until_trailing', 'entry_bar', 'exit_bar',
                            'breakeven_activation_bar', 'trailing_activation_bar', 'drawdown_bars',
                            'high_volatility_bars']:
                    outcome_features.append(min(val / 300.0, 1.0))  # Cap at 300 bars
                elif key in ['mae', 'mfe', 'max_profit_reached', 'profit_drawdown_from_peak']:
                    outcome_features.append(np.clip(val / 500.0, -1, 1))  # +/- $500
                elif key in ['exit_param_update_count', 'stop_adjustment_count']:
                    outcome_features.append(min(val / 50.0, 1.0))  # Cap at 50
                elif key in ['atr_change_percent', 'max_drawdown_percent', 'daily_loss_proximity_pct']:
                    outcome_features.append(np.clip(val / 100.0, -1, 1))  # +/- 100%
                elif key in ['avg_atr_during_trade', 'atr']:
                    outcome_features.append(min(val / 10.0, 1.0))  # Cap at 10
                elif key in ['entry_price']:
                    outcome_features.append(val / 10000.0)  # Normalize by typical ES price
                elif key in ['daily_loss_limit']:
                    outcome_features.append(val / 2000.0)  # Normalize by $2000
                elif key in ['wins_in_last_5_trades', 'losses_in_last_5_trades']:
                    outcome_features.append(val / 5.0)  # 0-1
                elif key in ['contracts', 'partial_1_contracts', 'partial_2_contracts',
                            'partial_3_contracts', 'remaining_contracts_at_exit']:
                    outcome_features.append(min(val / 5.0, 1.0))  # Cap at 5 contracts
                elif key in ['partial_1_price', 'partial_2_price', 'partial_3_price']:
                    outcome_features.append(val / 10000.0 if val > 0 else 0)  # Normalize by typical ES price
                elif key in ['trade_number_in_session']:
                    outcome_features.append(min(val / 10.0, 1.0))  # Cap at 10 trades
                elif key in ['minutes_until_close']:
                    outcome_features.append(min(val / 480.0, 1.0))  # Cap at 8 hours
                elif key in ['commission_paid', 'slippage_ticks', 'volume_at_exit', 'partial_exits_taken']:
                    outcome_features.append(min(val / 10.0, 1.0))  # Generic normalization
                else:
                    outcome_features.append(min(val, 1.0))  # Default: clip at 1
            
            # EXIT PARAMS (131 features from EXIT_PARAMS config, excluding current_atr)
            exit_param_features = []
            # Use exit_params_config order to ensure consistency
            from exit_params_config import EXIT_PARAMS
            for param_name in EXIT_PARAMS.keys():
                val = exit_params_current.get(param_name, 0.0)
                # Normalize based on typical ranges
                if 'min_r' in param_name or 'target' in param_name or '_r' in param_name:
                    exit_param_features.append(np.clip(val / 10.0, 0, 1))  # R-multiples 0-10
                elif 'ticks' in param_name or 'distance' in param_name:
                    exit_param_features.append(np.clip(val / 50.0, 0, 1))  # Ticks 0-50
                elif 'multiplier' in param_name or 'atr' in param_name:
                    exit_param_features.append(np.clip(val / 5.0, 0, 1))  # ATR multiples 0-5
                elif 'bars' in param_name or 'timeout' in param_name:
                    exit_param_features.append(min(val / 200.0, 1.0))  # Bars 0-200
                elif 'threshold' in param_name or 'pct' in param_name:
                    exit_param_features.append(np.clip(val / 100.0, 0, 1))  # Percentages 0-100
                else:
                    exit_param_features.append(np.clip(val, 0, 1))  # Default 0-1
            
            # Add current_atr as 132nd feature (market context at time of trade)
            current_atr_val = exit_params_current.get('current_atr', market_state.get('atr', 2.0))
            exit_param_features.append(min(current_atr_val / 10.0, 1.0))
            
            # Combine all features (10 + 66 + 132 = 208)
            feature_vec = market_features + outcome_features + exit_param_features
            
            # Extract exit params (labels) - ALL 131 PARAMETERS
            # Use exit_params_used field (complete 131-param dict)
            exit_params_used = exp.get('exit_params_used', {})
            
            # If old data without exit_params_used, skip or use fallback
            if not exit_params_used:
                # Try old format (only 6 params)
                exit_params_used = exp.get('exit_params', {})
                if not exit_params_used:
                    continue  # Skip if no exit params at all
            
            # Normalize all 131 parameters to 0-1 range
            label_vec = normalize_exit_params(exit_params_used)
            
            # Validate we have 131 labels (not 6 from old model)
            if len(label_vec) == 131:
                features.append(feature_vec)
                labels.append(label_vec)
            else:
                print(f"Warning: Expected 131 exit params, got {len(label_vec)} - skipping experience")
                
        except Exception as e:
            print(f"Warning: Skipping experience due to error: {e}")
            continue
    
    print(f"Valid training samples: {len(features):,}")
    print()
    
    return np.array(features), np.array(labels)


def train_exit_model():
    """Train the exit parameters neural network"""
    
    # Load data
    X, y = load_exit_experiences()
    
    if len(X) < 100:
        print("ERROR: Need at least 100 exit experiences to train")
        return
    
    # Split train/val
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train):,} samples")
    print(f"Validation set: {len(X_val):,} samples")
    print()
    
    # Create datasets
    train_dataset = ExitDataset(X_train, y_train)
    val_dataset = ExitDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    # Initialize model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on: {device}")
    print()
    
    model = ExitParamsNet(input_size=64, hidden_size=64).to(device)  # 64 inputs (actual count from feature vector)
    
    # Use MSE loss (predicting continuous values)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
    
    # Training loop
    print("Starting training...")
    print()
    
    best_val_loss = float('inf')
    patience = 20
    patience_counter = 0
    
    num_epochs = 150
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for features, labels in train_loader:
            features, labels = features.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for features, labels in val_loader:
                features, labels = features.to(device), labels.to(device)
                outputs = model(features)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        # Update scheduler
        scheduler.step(val_loss)
        
        # Print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train Loss: {train_loss:.4f}")
            print(f"  Val Loss: {val_loss:.4f}")
            print()
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Save best model
            torch.save({
                'model_state_dict': model.state_dict(),
                'input_size': 62,
                'hidden_size': 64,
                'val_loss': val_loss
            }, 'data/exit_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                print()
                break
    
    print("=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Model saved to: data/exit_model.pth")
    print()
    print("Next steps:")
    print("  1. Integrate into local_exit_manager.py")
    print("  2. Run full_backtest.py to test improved exits")
    print("  3. Compare R-multiple and profit vs pattern matching")


if __name__ == '__main__':
    train_exit_model()
