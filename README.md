# VWAP Bounce Bot

A sophisticated VWAP-based mean reversion trading bot for futures markets.

## 📁 Project Structure

This project is organized into two main directories:

### `src/` - Production Trading Bot
The production trading system for live and paper trading. Clean, user-focused, and ready to deploy.

```
src/
├── main.py              # Main entry point for production trading
├── config.py            # Configuration management
├── quotrading_engine.py # Main trading engine (7500+ lines)
├── signal_confidence.py # RL-based signal confidence scoring
├── regime_detection.py  # Market regime detection
├── broker_interface.py  # Broker API integration
├── monitoring.py        # Health checks and logging
└── ...                  # Other production modules
```

**Usage:**
```bash
# Run live trading
python src/main.py

# Run paper trading (dry-run mode)
python src/main.py --dry-run

# Override symbol
python src/main.py --symbol ES
```

### `dev/` - Development & Backtesting Environment
Complete backtesting framework for testing and development. Uses the actual production code for accurate simulation.

```
dev/
├── run_backtest.py      # Main entry point for backtests
├── backtesting.py       # Backtesting engine
├── __init__.py          # Module initialization
└── README.md            # Detailed dev documentation
```

**Usage:**
```bash
# Run backtest for last 30 days
python dev/run_backtest.py --days 30

# Run backtest with date range
python dev/run_backtest.py --start 2024-01-01 --end 2024-01-31

# Save results to report
python dev/run_backtest.py --days 30 --report results.txt

# Use tick-by-tick replay
python dev/run_backtest.py --days 7 --use-tick-data
```

See [`dev/README.md`](dev/README.md) for detailed backtesting documentation.

## 🎯 Why This Structure?

**Clean Separation:**
- **Production users** get a simple, focused trading bot without backtesting complexity
- **Developers** get full backtesting capabilities without cluttering production code
- **Maintainability** is improved with clear separation of concerns

**Shared Code:**
- Dev environment imports and uses the actual production trading logic
- Ensures backtests accurately reflect what the live bot will do
- No code duplication between backtest and production

## 🚀 Quick Start

### Production Trading

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your broker credentials
   ```

3. **Run the bot:**
   ```bash
   # Paper trading first!
   python src/main.py --dry-run
   
   # Live trading (requires CONFIRM_LIVE_TRADING=1 in .env)
   python src/main.py
   ```

### Backtesting & Development

1. **Prepare historical data:**
   Place CSV files in `data/historical_data/`:
   - `ES_1min.csv` - 1-minute OHLCV bars
   - `ES_ticks.csv` - Tick data (optional)

2. **Run backtest:**
   ```bash
   python dev/run_backtest.py --days 30
   ```

3. **Review results:**
   See trade-by-trade breakdown, performance metrics, and RL learning summary

## 🧠 Key Features

### Signal RL (Reinforcement Learning)
- **Confidence scoring** for each trade signal
- **Learns from experience** stored in `data/signal_experience.json`
- **Improves over time** as it sees more market conditions

### Pattern Matching
- **VWAP bounce patterns** for mean reversion
- **Standard deviation bands** for entry/exit zones
- **Volume and trend filters** for signal quality

### Regime Detection
- **Identifies market conditions:**
  - HIGH_VOL_TRENDING
  - HIGH_VOL_CHOPPY
  - LOW_VOL_TRENDING
  - LOW_VOL_RANGING
  - NORMAL
- **Adapts strategy** based on current regime

### Trade Management
- **ATR-based stops** for volatility-adjusted risk
- **Profit targets** with risk-reward ratios
- **Breakeven** moves stop to entry after threshold
- **Trailing stops** to lock in profits
- **Time decay** tightens stops as trade ages
- **Partial exits** at multiple profit levels

### Production Rules
- **UTC maintenance** respects 5:00-6:00 PM Eastern window
- **Auto-flatten** closes positions at 4:45 PM Eastern
- **Entry windows** only trades during allowed hours
- **Friday special** closes before weekend

## 📊 Data Requirements

### For Production (Live Trading)
- Broker API credentials
- Real-time market data feed

### For Backtesting
Place in `data/historical_data/`:

**1-minute bars** (`ES_1min.csv`):
```csv
timestamp,open,high,low,close,volume
2024-01-01T00:00:00,4725.50,4726.25,4724.75,4725.75,1234
```

**Tick data** (optional, `ES_ticks.csv`):
```csv
timestamp,price,size
2024-01-01T00:00:00.123,4725.50,5
```

## 🔧 Configuration

Configuration is managed in `src/config.py` with environment variable overrides via `.env`:

```python
# Key settings
instrument = "ES"              # Symbol to trade
max_contracts = 3              # Position size limit
risk_per_trade = 0.012         # 1.2% risk per trade
max_trades_per_day = 9999      # Daily trade limit
```

See `.env.example` for all available settings.

## 📈 Performance Monitoring

### Health Checks
Production bot runs a health check server on port 8080:
```bash
curl http://localhost:8080/health
```

### Logs
Logs are written to `logs/` directory with rotation.

### Metrics
Real-time performance metrics tracked including:
- Win rate
- Profit factor
- Sharpe ratio
- Max drawdown
- RL learning progress

## 🔒 Safety Features

- **Dry-run mode** for paper trading
- **Daily loss limits** with auto-shutdown
- **Position size limits** user-configurable
- **Maintenance window** auto-flatten
- **Error recovery** automatic reconnection
- **State persistence** survives restarts

## 🤝 Development Workflow

1. **Make changes** to production code in `src/`
2. **Test in backtest** using `dev/run_backtest.py`
3. **Verify RL learning** check experience growth
4. **Paper trade** with `--dry-run`
5. **Go live** when confident

## 📚 Documentation

- [Dev Environment README](dev/README.md) - Detailed backtesting guide
- [Configuration Guide](.env.example) - All environment variables
- Code comments - Inline documentation throughout

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always paper trade before going live.

## 📝 License

See LICENSE file for details.

## 🙏 Support

For issues and questions, please open a GitHub issue.

---

**Remember:**
- `src/` for production trading
- `dev/` for backtesting and development
- Always paper trade new strategies first!
