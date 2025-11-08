"""
QuoTrading API - Admin CLI Tool
Manage users, subscriptions, and test API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "https://quotrading-api.onrender.com"  # Change to your deployed URL
# API_URL = "http://localhost:8000"  # For local testing

def print_response(response):
    """Pretty print API response"""
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print(response.text)

def register_user(email):
    """Register a new user"""
    print(f"\n📝 Registering user: {email}")
    response = requests.post(
        f"{API_URL}/api/v1/users/register",
        json={"email": email}
    )
    print(f"Status: {response.status_code}")
    print_response(response)
    return response

def validate_license(email, api_key):
    """Validate a user's license"""
    print(f"\n🔐 Validating license for: {email}")
    response = requests.post(
        f"{API_URL}/api/v1/license/validate",
        json={"email": email, "api_key": api_key}
    )
    print(f"Status: {response.status_code}")
    print_response(response)
    return response

def get_user_info(email):
    """Get user information"""
    print(f"\n👤 Getting info for: {email}")
    response = requests.get(f"{API_URL}/api/v1/users/{email}")
    print(f"Status: {response.status_code}")
    print_response(response)
    return response

def test_admin_key():
    """Test admin master key"""
    print("\n🔑 Testing admin master key")
    response = requests.post(
        f"{API_URL}/api/v1/license/validate",
        json={
            "email": "admin@quotrading.com",
            "api_key": "QUOTRADING_ADMIN_MASTER_2025"
        }
    )
    print(f"Status: {response.status_code}")
    print_response(response)
    return response

def health_check():
    """Check API health"""
    print("\n💚 Checking API health")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print_response(response)
    return response

def main_menu():
    """Interactive menu"""
    while True:
        print("\n" + "="*50)
        print("QuoTrading API - Admin Tool")
        print("="*50)
        print("1. Health Check")
        print("2. Test Admin Key")
        print("3. Register New User")
        print("4. Validate License")
        print("5. Get User Info")
        print("6. Run Full Test Suite")
        print("0. Exit")
        print("="*50)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            health_check()
        
        elif choice == "2":
            test_admin_key()
        
        elif choice == "3":
            email = input("Enter email: ").strip()
            register_user(email)
        
        elif choice == "4":
            email = input("Enter email: ").strip()
            api_key = input("Enter API key: ").strip()
            validate_license(email, api_key)
        
        elif choice == "5":
            email = input("Enter email: ").strip()
            get_user_info(email)
        
        elif choice == "6":
            run_test_suite()
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice!")

def run_test_suite():
    """Run comprehensive test suite"""
    print("\n" + "="*50)
    print("🧪 Running Test Suite")
    print("="*50)
    
    # Test 1: Health check
    print("\n[1/4] Health Check")
    health_check()
    
    # Test 2: Admin key
    print("\n[2/4] Admin Key Validation")
    test_admin_key()
    
    # Test 3: Register test user
    print("\n[3/4] User Registration")
    test_email = f"test_{datetime.now().timestamp()}@example.com"
    reg_response = register_user(test_email)
    
    if reg_response.status_code == 200:
        data = reg_response.json()
        test_api_key = data.get("api_key")
        
        # Test 4: Validate new user (should fail - no subscription)
        print("\n[4/4] License Validation (should fail - no subscription)")
        validate_license(test_email, test_api_key)
    
    print("\n" + "="*50)
    print("✅ Test Suite Complete!")
    print("="*50)

if __name__ == "__main__":
    print(f"\nAPI URL: {API_URL}")
    print("Note: Make sure your API is deployed and running!")
    
    # Quick test mode
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_test_suite()
        elif sys.argv[1] == "health":
            health_check()
        elif sys.argv[1] == "admin":
            test_admin_key()
    else:
        main_menu()
