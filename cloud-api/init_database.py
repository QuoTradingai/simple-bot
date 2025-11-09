"""
Database initialization script for QuoTrading Cloud API
Creates tables and seeds initial admin user
"""

import sys
import os
from database import DatabaseManager, create_user
from datetime import datetime, timedelta

def init_database(database_url=None, create_admin=True):
    """
    Initialize database with tables and optional admin user
    
    Args:
        database_url: Database connection string (optional)
        create_admin: Whether to create initial admin user
    """
    print("=" * 60)
    print("QuoTrading Database Initialization")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    print(f"\n📊 Database: {db_manager.database_url}")
    
    # Create tables
    print("\n🔨 Creating database tables...")
    db_manager.create_tables()
    
    # Create admin user if requested
    if create_admin:
        print("\n👤 Creating admin user...")
        db = db_manager.get_session()
        try:
            # Check if admin already exists
            from database import get_user_by_account_id
            existing_admin = get_user_by_account_id(db, "ADMIN")
            
            if existing_admin:
                print(f"⚠️  Admin user already exists:")
                print(f"   Account ID: {existing_admin.account_id}")
                print(f"   License Key: {existing_admin.license_key}")
                print(f"   Status: {existing_admin.license_status}")
            else:
                # Create new admin
                admin = create_user(
                    db_session=db,
                    account_id="ADMIN",
                    email="admin@quotrading.com",
                    license_type="ADMIN",
                    license_duration_days=None,  # Unlimited
                    is_admin=True,
                    notes="System administrator account"
                )
                
                print(f"✅ Admin user created successfully!")
                print(f"   Account ID: {admin.account_id}")
                print(f"   License Key: {admin.license_key}")
                print(f"   Email: {admin.email}")
                print(f"\n   🔑 Save this license key - you'll need it for admin API access!")
        
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.rollback()
        finally:
            db.close()
    
    # Show summary
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set DATABASE_URL environment variable in Azure")
    print("2. Set REDIS_URL environment variable in Azure (optional)")
    print("3. Deploy updated code to Azure Container Apps")
    print("4. Test API endpoints with admin license key")
    print("\n")
    
    db_manager.close()


def create_test_users(database_url=None, count=3):
    """Create test users for development"""
    print("=" * 60)
    print(f"Creating {count} Test Users")
    print("=" * 60)
    
    db_manager = DatabaseManager(database_url)
    db = db_manager.get_session()
    
    try:
        for i in range(1, count + 1):
            account_id = f"TEST{i:03d}"
            
            # Check if exists
            from database import get_user_by_account_id
            if get_user_by_account_id(db, account_id):
                print(f"⚠️  User {account_id} already exists, skipping...")
                continue
            
            # Create user
            user = create_user(
                db_session=db,
                account_id=account_id,
                email=f"test{i}@quotrading.com",
                license_type="BETA",
                license_duration_days=90,  # 90 day trial
                is_admin=False,
                notes=f"Test user {i} for beta testing"
            )
            
            print(f"✅ User {account_id} created")
            print(f"   License Key: {user.license_key}")
            print(f"   Expires: {user.license_expiration.strftime('%Y-%m-%d')}")
            print()
        
        print("✅ Test users created successfully!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
        db_manager.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize QuoTrading database")
    parser.add_argument(
        '--database-url',
        help='Database connection URL (default: from DATABASE_URL env var or SQLite)',
        default=None
    )
    parser.add_argument(
        '--no-admin',
        action='store_true',
        help='Skip creating admin user'
    )
    parser.add_argument(
        '--test-users',
        type=int,
        metavar='N',
        help='Create N test users for development'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    init_database(
        database_url=args.database_url,
        create_admin=not args.no_admin
    )
    
    # Create test users if requested
    if args.test_users:
        create_test_users(
            database_url=args.database_url,
            count=args.test_users
        )
