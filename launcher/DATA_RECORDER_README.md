# Market Data Recorder

## Overview

The Market Data Recorder is a standalone tool for capturing live market data from your broker for backtesting purposes. It operates completely separately from the main trading system.

## Features

- **Multi-Symbol Recording**: Record multiple ticker symbols simultaneously
- **Comprehensive Data Capture**: 
  - Quotes (Bid/Ask prices and sizes)
  - Trades (Price, Size, Side)
  - Market Depth/DOM (Order book levels)
  - Precise timestamps
- **Single CSV Output**: All data consolidated into one file, separated by symbol
- **Easy to Use**: Simple GUI interface
- **Independent**: Does not interfere with your trading operations

## Installation

The Data Recorder requires the broker SDK dependencies to connect to your broker and stream market data.

### Step 1: Install Broker SDK Dependencies

Edit `requirements.txt` and uncomment the broker SDK section (lines 13-27):

```bash
# Broker SDK dependencies (optional - install only if using compatible broker)
# Uncomment the following lines if your broker supports the Project-X SDK:
project-x-py>=3.5.9
cachetools>=6.1.0
deprecated>=1.2.18
httpx[http2]>=0.27.0
lz4>=4.4.4
msgpack-python>=0.5.6
numpy>=2.3.2
orjson>=3.11.1
plotly>=6.3.0
polars>=1.31.0
pydantic>=2.11.7
pytz>=2025.2
pyyaml>=6.0.2
rich>=14.1.0
signalrcore>=0.9.5
```

Remove the `#` comment symbols from each line.

### Step 2: Install Requirements

```bash
pip install -r requirements.txt
```

**Note**: If you encounter any installation issues, you may need to install some packages individually or use a specific Python version (3.9-3.11 recommended).

## Usage

### Starting the Recorder

1. Run the launcher:
```bash
python launcher/DataRecorder_Launcher.py
```

2. Enter your broker credentials:
   - Broker: Select your broker (currently TopStep supported)
   - Username: Your broker username/email
   - API Token: Your broker API token

3. Select symbols to record:
   - Check one or more symbols you want to record
   - Supports: ES, MES, NQ, MNQ, YM, RTY, CL, GC

4. Specify output file:
   - Enter a filename for your CSV output
   - Default: `market_data.csv`
   - Click "Browse" to select a different location

5. Click "START RECORDING"

### Stopping the Recorder

- Click "STOP RECORDING" button
- Or close the window (you'll be prompted to confirm)

## CSV Output Format

The recorder creates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| timestamp | ISO format timestamp of the data point |
| symbol | Ticker symbol (e.g., ES, NQ) |
| data_type | Type of data: 'quote', 'trade', or 'depth' |
| bid_price | Best bid price (for quotes) |
| bid_size | Best bid size (for quotes) |
| ask_price | Best ask price (for quotes) |
| ask_size | Best ask size (for quotes) |
| trade_price | Trade execution price (for trades) |
| trade_size | Trade size (for trades) |
| trade_side | Trade side: 'buy' or 'sell' (for trades) |
| depth_level | Order book level (for depth/DOM) |
| depth_side | 'bid' or 'ask' (for depth/DOM) |
| depth_price | Price at this depth level |
| depth_size | Size at this depth level |

### Example CSV Data

```csv
timestamp,symbol,data_type,bid_price,bid_size,ask_price,ask_size,trade_price,trade_size,trade_side,depth_level,depth_side,depth_price,depth_size
2025-12-06T14:30:15.123456,ES,quote,4500.25,10,4500.50,8,,,,,,
2025-12-06T14:30:15.234567,ES,trade,,,,,4500.50,2,buy,,,
2025-12-06T14:30:15.345678,NQ,quote,16200.00,15,16200.25,12,,,,,,
2025-12-06T14:30:15.456789,ES,depth,,,,,,,0,bid,4500.25,10
2025-12-06T14:30:15.567890,ES,depth,,,,,,,1,bid,4500.00,25
```

## Using Recorded Data for Backtesting

The CSV format is designed to be easily imported into your backtesting framework:

```python
import pandas as pd

# Load recorded data
df = pd.read_csv('market_data.csv')

# Filter by symbol
es_data = df[df['symbol'] == 'ES']

# Filter by data type
quotes = df[df['data_type'] == 'quote']
trades = df[df['data_type'] == 'trade']
depth = df[df['data_type'] == 'depth']

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Analyze or replay the data
```

## Tips

1. **Recording Duration**: The recorder can run indefinitely. For backtesting, you may want to record:
   - Full trading sessions (market open to close)
   - Specific market events
   - Multiple days for comprehensive data

2. **File Size**: Market data can be large. Monitor your disk space:
   - High-frequency data for multiple symbols can generate several GB per day
   - Consider recording during specific time periods of interest

3. **Data Quality**: 
   - Ensure stable internet connection during recording
   - The recorder will report statistics every 10 seconds
   - Check the status log for any connection issues

4. **Multiple Recording Sessions**:
   - Each recording session appends to the CSV if the file exists
   - To start fresh, specify a new filename or delete the old file

## Troubleshooting

### Cannot Connect to Broker
- Verify your API token is valid
- Check your internet connection
- Ensure your broker account is active

### No Data Being Recorded
- Check the status log for subscription errors
- Verify the selected symbols are available for trading
- Ensure market is open (or pre-market/after-hours for available symbols)

### CSV File is Empty
- Make sure you clicked "START RECORDING"
- Check that the recorder is connected (see status log)
- Allow some time for data to accumulate

## Configuration

The recorder saves your settings in `data_recorder_config.json`:
- Broker credentials (if you choose to save them)
- Last selected symbols
- Output file path

## Security Notes

- API tokens are stored in plain text in the config file
- Do not share your `data_recorder_config.json` file
- The config file is in `.gitignore` to prevent accidental commits
- Consider deleting credentials from the config when not in use

## Support

For issues or questions, please contact QuoTrading support.
