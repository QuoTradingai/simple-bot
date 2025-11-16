"""
Query cloud PostgreSQL database to verify saved experiences
"""

import os
import sys

# Add cloud-api to path for database imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cloud-api'))

from database import DatabaseManager, RLExperience, ExitExperience, MLExperience
import json

def query_cloud_experiences():
    """Query and display sample experiences from cloud database"""
    
    print("🔍 Querying cloud PostgreSQL database...")
    
    db_manager = DatabaseManager()
    db = db_manager.get_session()
    
    try:
        # Count all records
        rl_count = db.query(RLExperience).count()
        exit_count = db.query(ExitExperience).count()
        ml_count = db.query(MLExperience).count()
        
        print(f"\n📊 Database Record Counts:")
        print(f"   - RLExperience: {rl_count:,}")
        print(f"   - ExitExperience: {exit_count:,}")
        print(f"   - MLExperience: {ml_count:,}")
        print(f"   - TOTAL: {rl_count + exit_count + ml_count:,}")
        
        # Query MLExperience table (newest table with JSONB storage)
        if ml_count > 0:
            print(f"\n📋 MLExperience Table (first 3 records):")
            ml_experiences = db.query(MLExperience).order_by(MLExperience.timestamp.desc()).limit(3).all()
            
            for i, exp in enumerate(ml_experiences, 1):
                print(f"\n   Record {i}:")
                print(f"      ID: {exp.id}")
                print(f"      User: {exp.user_id}")
                print(f"      Symbol: {exp.symbol}")
                print(f"      Type: {exp.experience_type}")
                print(f"      Quality Score: {exp.quality_score}")
                print(f"      Timestamp: {exp.timestamp}")
                
                # Show sample of rl_state fields
                if exp.rl_state:
                    rl_keys = list(exp.rl_state.keys())
                    print(f"      RL State Keys ({len(rl_keys)} total): {rl_keys[:10]}...")
                    
                    # Show specific important fields
                    if 'signal' in exp.rl_state:
                        print(f"         signal: {exp.rl_state.get('signal')}")
                    if 'confidence' in exp.rl_state:
                        print(f"         confidence: {exp.rl_state.get('confidence')}")
                    if 'took_trade' in exp.rl_state:
                        print(f"         took_trade: {exp.rl_state.get('took_trade')}")
                
                # Show outcome
                if exp.outcome:
                    print(f"      Outcome: {exp.outcome}")
        
        # Query RLExperience table (legacy signal storage)
        if rl_count > 0:
            print(f"\n📋 RLExperience Table (first 3 records):")
            rl_experiences = db.query(RLExperience).order_by(RLExperience.timestamp.desc()).limit(3).all()
            
            for i, exp in enumerate(rl_experiences, 1):
                print(f"\n   Record {i}:")
                print(f"      ID: {exp.id}")
                print(f"      User: {exp.user_id}")
                print(f"      Symbol: {exp.symbol}")
                print(f"      Signal: {exp.signal}")
                print(f"      Confidence: {exp.confidence}")
                print(f"      Reward: {exp.reward}")
                print(f"      Took Trade: {exp.took_trade}")
                print(f"      Timestamp: {exp.timestamp}")
        
        # Query ExitExperience table
        if exit_count > 0:
            print(f"\n📋 ExitExperience Table (first 3 records):")
            exit_experiences = db.query(ExitExperience).order_by(ExitExperience.timestamp.desc()).limit(3).all()
            
            for i, exp in enumerate(exit_experiences, 1):
                print(f"\n   Record {i}:")
                print(f"      ID: {exp.id}")
                print(f"      User: {exp.user_id}")
                print(f"      Symbol: {exp.symbol}")
                print(f"      Regime: {exp.regime}")
                print(f"      Timestamp: {exp.timestamp}")
                if exp.outcome:
                    print(f"      Outcome: PnL={exp.outcome.get('pnl')}, Win={exp.outcome.get('win')}")
        
        print("\n✅ Query complete")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    query_cloud_experiences()
