"""
Test different sample sizes to see if 10 is enough
"""
import psycopg2
import os
import sys
sys.path.insert(0, 'c:/Users/kevin/Downloads/simple-bot/cloud-api/flask-api')

from rl_decision_engine import CloudRLDecisionEngine

# Load experiences from PostgreSQL
print("Loading experiences from PostgreSQL...")
conn = psycopg2.connect(
    host="quotrading-db.postgres.database.azure.com",
    database="quotrading",
    user="quotradingadmin",
    password="QuoTrade2024!SecureDB",
    port=5432,
    sslmode='require'
)

cursor = conn.cursor()
cursor.execute("SELECT symbol, rsi, vwap_distance, atr, volume_ratio, hour, day_of_week, recent_pnl, streak, side, regime, took_trade, pnl, duration FROM rl_experiences WHERE symbol = 'ES'")
rows = cursor.fetchall()

# Convert to nested format for engine
experiences = []
for row in rows:
    exp = {
        'state': {
            'symbol': row[0],
            'rsi': float(row[1]),
            'vwap_distance': float(row[2]),
            'atr': float(row[3]),
            'volume_ratio': float(row[4]),
            'hour': int(row[5]),
            'day_of_week': int(row[6]),
            'recent_pnl': float(row[7]),
            'streak': int(row[8]),
            'side': row[9],
            'regime': row[10]
        },
        'action': {'took_trade': row[11]},
        'reward': float(row[12]),
        'duration': float(row[13])
    }
    experiences.append(exp)

cursor.close()
conn.close()

# Initialize engine
engine = CloudRLDecisionEngine(experiences)

print(f"\nTotal experiences loaded: {len(engine.experiences)}")

# Test a few conditions with different sample sizes
test_cases = [
    ("RSI 20 Long", {"rsi": 20, "vwap_distance": 0.90, "atr": 3.0, "volume_ratio": 1.5, "hour": 9, "day_of_week": 1, "recent_pnl": 100, "streak": 2, "side": "long", "regime": "NORMAL"}),
    ("RSI 35 Long", {"rsi": 35, "vwap_distance": 0.98, "atr": 2.0, "volume_ratio": 1.1, "hour": 11, "day_of_week": 2, "recent_pnl": 50, "streak": 1, "side": "long", "regime": "NORMAL"}),
    ("RSI 60 Short", {"rsi": 60, "vwap_distance": 1.05, "atr": 2.0, "volume_ratio": 1.1, "hour": 11, "day_of_week": 2, "recent_pnl": 50, "streak": 1, "side": "short", "regime": "NORMAL"}),
]

sample_sizes = [5, 10, 20, 30, 50]

for name, state in test_cases:
    print(f"\n{'='*100}")
    print(f"Test Case: {name}")
    print(f"{'='*100}")
    print(f"{'Size':>6} | {'Winners':>7} | {'Losers':>7} | {'Win Rate':>8} | {'Avg PNL':>10} | {'Decision':>8}")
    print(f"{'-'*100}")
    
    for size in sample_sizes:
        similar = engine.find_similar_states(state, max_results=size)
        
        if len(similar) < size:
            print(f"{size:>6} | Not enough data - only {len(similar)} experiences found")
            continue
            
        winners = sum(1 for exp in similar if exp.get('reward', 0) > 0)
        losers = len(similar) - winners
        win_rate = winners / len(similar)
        avg_pnl = sum(exp.get('reward', 0) for exp in similar) / len(similar)
        
        decision = "TAKE" if win_rate >= 0.5 and avg_pnl > 0 else "SKIP"
        
        print(f"{size:>6} | {winners:>7} | {losers:>7} | {win_rate:>7.1%} | ${avg_pnl:>9.2f} | {decision:>8}")

print(f"\n{'='*100}")
print("ANALYSIS:")
print("- Does win rate stabilize with more samples?")
print("- Does average PNL become more reliable?")
print("- Is 10 enough or should we use 20-30?")
print(f"{'='*100}\n")
