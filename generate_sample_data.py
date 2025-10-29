"""
Generate sample historical data for backtesting
"""

import csv
from datetime import datetime, timedelta
import random
import os


def generate_sample_tick_data(symbol, start_date, end_date, output_dir):
    """Generate sample tick data for testing"""
    filepath = os.path.join(output_dir, f"{symbol}_ticks.csv")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'price', 'volume'])
        
        current_time = start_date
        base_price = 4500.0  # MES base price
        
        while current_time <= end_date:
            # Skip weekends
            if current_time.weekday() < 5:  # Monday-Friday
                # Trading hours: 9 AM - 4 PM
                if 9 <= current_time.hour < 16:
                    # Generate tick every 10 seconds during trading hours
                    price = base_price + random.uniform(-5, 5)
                    volume = random.randint(1, 10)
                    
                    writer.writerow([
                        current_time.isoformat(),
                        f"{price:.2f}",
                        volume
                    ])
                    
                    current_time += timedelta(seconds=10)
                else:
                    # Jump to next day 9 AM
                    current_time = current_time.replace(hour=9, minute=0, second=0)
                    current_time += timedelta(days=1)
            else:
                # Jump to Monday
                days_until_monday = (7 - current_time.weekday()) % 7
                current_time += timedelta(days=days_until_monday if days_until_monday > 0 else 1)
                current_time = current_time.replace(hour=9, minute=0, second=0)
                
            # Slight price drift
            base_price += random.uniform(-0.5, 0.5)
    
    print(f"Generated tick data: {filepath}")


def generate_sample_bar_data(symbol, timeframe, start_date, end_date, output_dir):
    """Generate sample bar data for testing"""
    filepath = os.path.join(output_dir, f"{symbol}_{timeframe}.csv")
    
    # Determine bar duration
    if timeframe == "1min":
        bar_duration = timedelta(minutes=1)
    elif timeframe == "15min":
        bar_duration = timedelta(minutes=15)
    else:
        bar_duration = timedelta(minutes=1)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        current_time = start_date.replace(minute=0, second=0, microsecond=0)
        base_price = 4500.0
        
        while current_time <= end_date:
            # Skip weekends
            if current_time.weekday() < 5:  # Monday-Friday
                # Trading hours: 9 AM - 4 PM
                if 9 <= current_time.hour < 16:
                    # Generate bar
                    open_price = base_price + random.uniform(-2, 2)
                    close_price = open_price + random.uniform(-1, 1)
                    high_price = max(open_price, close_price) + random.uniform(0, 0.5)
                    low_price = min(open_price, close_price) - random.uniform(0, 0.5)
                    volume = random.randint(10, 100)
                    
                    writer.writerow([
                        current_time.isoformat(),
                        f"{open_price:.2f}",
                        f"{high_price:.2f}",
                        f"{low_price:.2f}",
                        f"{close_price:.2f}",
                        volume
                    ])
                    
                    current_time += bar_duration
                    base_price = close_price
                else:
                    # Jump to next day 9 AM
                    current_time = current_time.replace(hour=9, minute=0, second=0)
                    current_time += timedelta(days=1)
            else:
                # Jump to Monday
                days_until_monday = (7 - current_time.weekday()) % 7
                current_time += timedelta(days=days_until_monday if days_until_monday > 0 else 1)
                current_time = current_time.replace(hour=9, minute=0, second=0)
    
    print(f"Generated bar data: {filepath}")


def main():
    """Generate sample data"""
    output_dir = './historical_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate data for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"Generating sample data from {start_date.date()} to {end_date.date()}")
    
    # Generate for MES
    symbol = "MES"
    
    # Generate tick data
    generate_sample_tick_data(symbol, start_date, end_date, output_dir)
    
    # Generate 1-minute bars
    generate_sample_bar_data(symbol, "1min", start_date, end_date, output_dir)
    
    # Generate 15-minute bars
    generate_sample_bar_data(symbol, "15min", start_date, end_date, output_dir)
    
    print("\nSample data generation complete!")
    print(f"Data saved to: {output_dir}")


if __name__ == '__main__':
    main()
