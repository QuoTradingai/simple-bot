"""
Clear all experiences from cloud PostgreSQL database
Removes all RLExperience, ExitExperience, and MLExperience records
"""

import os
import sys

# Add cloud-api to path for database imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cloud-api'))

from database import get_db, RLExperience, ExitExperience, MLExperience

def clear_all_experiences():
    """Delete all experience records from cloud database"""
    
    print("🗑️  Clearing all experiences from cloud database...")
    
    db = next(get_db())
    
    try:
        # Count before deletion
        rl_count = db.query(RLExperience).count()
        exit_count = db.query(ExitExperience).count()
        ml_count = db.query(MLExperience).count()
        
        print(f"\n📊 Current database counts:")
        print(f"   - RLExperience: {rl_count}")
        print(f"   - ExitExperience: {exit_count}")
        print(f"   - MLExperience: {ml_count}")
        print(f"   - TOTAL: {rl_count + exit_count + ml_count}")
        
        # Confirm deletion
        confirm = input("\n⚠️  Delete ALL experiences? Type 'DELETE' to confirm: ")
        
        if confirm != "DELETE":
            print("❌ Cancelled - no data deleted")
            return
        
        # Delete all records
        rl_deleted = db.query(RLExperience).delete()
        exit_deleted = db.query(ExitExperience).delete()
        ml_deleted = db.query(MLExperience).delete()
        
        db.commit()
        
        print(f"\n✅ Deleted:")
        print(f"   - RLExperience: {rl_deleted}")
        print(f"   - ExitExperience: {exit_deleted}")
        print(f"   - MLExperience: {ml_deleted}")
        print(f"   - TOTAL: {rl_deleted + exit_deleted + ml_deleted}")
        
        # Verify empty
        final_count = db.query(RLExperience).count() + db.query(ExitExperience).count() + db.query(MLExperience).count()
        
        if final_count == 0:
            print(f"\n✅ Cloud database is now empty")
        else:
            print(f"\n⚠️  Warning: {final_count} records remain")
            
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_experiences()
