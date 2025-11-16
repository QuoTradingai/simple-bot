"""
Direct PostgreSQL upload of local experiences to cloud ml_experiences table.
Bypasses the HTTP API and writes directly to the database.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import pytz
import sys

# Add cloud-api to path to import database models
sys.path.insert(0, str(Path(__file__).parent.parent / "cloud-api"))

from database import DatabaseManager, MLExperience

SIGNAL_PATH = Path("data/local_experiences/signal_experiences_v2.json")
EXIT_PATH = Path("data/local_experiences/exit_experiences_v2.json")


def load_experiences(path: Path) -> list:
    """Load experiences from JSON file"""
    if not path.exists():
        print(f"❌ File not found: {path}")
        return []
    
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    experiences = data.get("experiences", [])
    print(f"✅ Loaded {len(experiences):,} experiences from {path.name}")
    return experiences


def upload_signal_experiences(db_manager: DatabaseManager, experiences: list) -> int:
    """Upload signal experiences to ml_experiences table"""
    session = db_manager.get_session()
    uploaded = 0
    
    try:
        print(f"\n📤 Uploading {len(experiences):,} signal experiences...")
        
        for i, exp in enumerate(experiences, 1):
            try:
                # Parse timestamp
                timestamp_str = exp.get("timestamp", datetime.now(pytz.UTC).isoformat())
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now(pytz.UTC)
                
                # Create ML experience record
                ml_exp = MLExperience(
                    user_id="local_backtest",
                    symbol=exp.get("symbol", "ES"),
                    experience_type="signal",
                    rl_state=exp,  # Store entire experience as rl_state
                    outcome={
                        "pnl": exp.get("pnl", 0.0),
                        "outcome": exp.get("outcome", "UNKNOWN"),
                        "took_trade": exp.get("took_trade", False),
                        "confidence": exp.get("confidence", 0.5)
                    },
                    quality_score=float(exp.get("confidence", 0.5)),
                    timestamp=timestamp
                )
                
                session.add(ml_exp)
                uploaded += 1
                
                # Commit in batches of 100
                if uploaded % 100 == 0:
                    session.commit()
                    print(f"   ✓ {uploaded:,}/{len(experiences):,} signal experiences uploaded...")
                    
            except Exception as e:
                print(f"   ⚠️  Error uploading signal experience {i}: {e}")
                continue
        
        # Final commit
        session.commit()
        print(f"   ✅ Uploaded {uploaded:,} signal experiences total")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during signal upload: {e}")
    finally:
        session.close()
    
    return uploaded


def upload_exit_experiences(db_manager: DatabaseManager, experiences: list) -> int:
    """Upload exit experiences to ml_experiences table"""
    session = db_manager.get_session()
    uploaded = 0
    
    try:
        print(f"\n📤 Uploading {len(experiences):,} exit experiences...")
        
        for i, exp in enumerate(experiences, 1):
            try:
                # Parse timestamp
                timestamp_str = exp.get("timestamp", datetime.now(pytz.UTC).isoformat())
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now(pytz.UTC)
                
                # Extract outcome data
                outcome_data = exp.get("outcome", {})
                
                # Create ML experience record
                ml_exp = MLExperience(
                    user_id="local_backtest",
                    symbol=exp.get("symbol", "ES"),
                    experience_type="exit",
                    rl_state=exp,  # Store entire experience as rl_state
                    outcome=outcome_data,
                    quality_score=float(outcome_data.get("entry_confidence", 1.0)) if outcome_data else 1.0,
                    timestamp=timestamp
                )
                
                session.add(ml_exp)
                uploaded += 1
                
                # Commit in batches of 50 (exit experiences are larger)
                if uploaded % 50 == 0:
                    session.commit()
                    print(f"   ✓ {uploaded:,}/{len(experiences):,} exit experiences uploaded...")
                    
            except Exception as e:
                print(f"   ⚠️  Error uploading exit experience {i}: {e}")
                continue
        
        # Final commit
        session.commit()
        print(f"   ✅ Uploaded {uploaded:,} exit experiences total")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during exit upload: {e}")
    finally:
        session.close()
    
    return uploaded


def main():
    """Main upload function"""
    print("🚀 DIRECT DATABASE UPLOAD TO CLOUD POSTGRESQL")
    print("=" * 60)
    
    # Load experiences
    signal_experiences = load_experiences(SIGNAL_PATH)
    exit_experiences = load_experiences(EXIT_PATH)
    
    total_experiences = len(signal_experiences) + len(exit_experiences)
    print(f"\n📊 Total experiences to upload: {total_experiences:,}")
    print(f"   - Signal: {len(signal_experiences):,}")
    print(f"   - Exit: {len(exit_experiences):,}")
    
    # Initialize database connection
    db_manager = DatabaseManager()
    
    # Upload signal experiences
    signal_uploaded = upload_signal_experiences(db_manager, signal_experiences)
    
    # Upload exit experiences
    exit_uploaded = upload_exit_experiences(db_manager, exit_experiences)
    
    # Summary
    total_uploaded = signal_uploaded + exit_uploaded
    print("\n" + "=" * 60)
    print("UPLOAD COMPLETE!")
    print(f"Signal experiences: {signal_uploaded:,}/{len(signal_experiences):,}")
    print(f"Exit experiences:   {exit_uploaded:,}/{len(exit_experiences):,}")
    print(f"Total uploaded:     {total_uploaded:,}/{total_experiences:,}")
    
    if total_uploaded == total_experiences:
        print("\n✅ SUCCESS - All experiences uploaded to cloud!")
    elif total_uploaded > 0:
        print(f"\n⚠️  PARTIAL SUCCESS - {total_uploaded:,}/{total_experiences:,} uploaded")
    else:
        print("\n❌ FAILED - No experiences uploaded")


if __name__ == "__main__":
    main()
