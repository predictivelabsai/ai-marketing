"""
Simple tests to verify connectivity for various .env keys.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_xai_api_key_connectivity():
    """Test XAI API key connectivity."""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        print("❌ XAI_API_KEY not found in environment")
        return False
    
    try:
        # Test connectivity by making a simple API call
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test request to check if API key is valid
        response = requests.get(
            "https://api.x.ai/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ XAI_API_KEY: Valid and connected")
            return True
        else:
            print(f"❌ XAI_API_KEY: API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ XAI_API_KEY: Connection failed - {str(e)}")
        return False


def test_arcade_api_key_connectivity():
    """Test Arcade API key connectivity."""
    api_key = os.getenv('ARCADE_API_KEY')
    if not api_key:
        print("❌ ARCADE_API_KEY not found in environment")
        return False
    
    try:
        # Test connectivity using the correct endpoint and auth method
        # Arcade API uses direct API key (no Bearer prefix) and api.arcade.dev
        headers = {
            "Authorization": api_key,  # Direct API key, no Bearer prefix
            "Content-Type": "application/json"
        }
        
        # Test request to list available tools
        response = requests.get(
            "https://api.arcade.dev/v1/tools",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ ARCADE_API_KEY: Valid and connected")
            return True
        elif response.status_code in [401, 403]:
            print("❌ ARCADE_API_KEY: Authentication failed (invalid key)")
            return False
        else:
            print(f"⚠️ ARCADE_API_KEY: API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ARCADE_API_KEY: Connection failed - {str(e)}")
        return False


def test_arcade_user_email():
    """Test that Arcade user email is set."""
    email = os.getenv('ARCADE_USER_EMAIL')
    if not email:
        print("❌ ARCADE_USER_EMAIL not found in environment")
        return False
    
    # Basic email format check
    if '@' in email and '.' in email.split('@')[1]:
        print(f"✅ ARCADE_USER_EMAIL: Set ({email[:3]}***@{email.split('@')[1]})")
        return True
    else:
        print("❌ ARCADE_USER_EMAIL: Invalid email format")
        return False


def test_arcade_user_password():
    """Test that Arcade user password is set."""
    password = os.getenv('ARCADE_USER_PASSWORD')
    if not password:
        print("❌ ARCADE_USER_PASSWORD not found in environment")
        return False
    
    if len(password) > 0:
        print(f"✅ ARCADE_USER_PASSWORD: Set (length: {len(password)})")
        return True
    else:
        print("❌ ARCADE_USER_PASSWORD: Empty")
        return False


def test_linkedin_page():
    """Test that LinkedIn page URL is set."""
    linkedin_page = os.getenv('LINKEDIN_PAGE')
    if not linkedin_page:
        print("❌ LINKEDIN_PAGE not found in environment")
        return False
    
    if linkedin_page.startswith('http'):
        print(f"✅ LINKEDIN_PAGE: Set ({linkedin_page})")
        return True
    else:
        print(f"⚠️ LINKEDIN_PAGE: May not be a valid URL ({linkedin_page})")
        return False


def test_twitter_email():
    """Test that Twitter email is set (if used)."""
    email = os.getenv('TWITTER_EMAIL')
    if not email:
        print("⚠️ TWITTER_EMAIL not found in environment (may not be required)")
        return None
    
    if '@' in email:
        print(f"✅ TWITTER_EMAIL: Set ({email[:3]}***@{email.split('@')[1]})")
        return True
    else:
        print("❌ TWITTER_EMAIL: Invalid email format")
        return False


def test_twitter_password():
    """Test that Twitter password is set (if used)."""
    password = os.getenv('TWITTER_PASSWORD')
    if not password:
        print("⚠️ TWITTER_PASSWORD not found in environment (may not be required)")
        return None
    
    if len(password) > 0:
        print(f"✅ TWITTER_PASSWORD: Set (length: {len(password)})")
        return True
    else:
        print("❌ TWITTER_PASSWORD: Empty")
        return False


def run_all_connectivity_tests():
    """Run all connectivity tests."""
    print("=" * 60)
    print("Environment Variable Connectivity Tests")
    print("=" * 60)
    print()
    
    results = []
    
    # Core API keys
    results.append(("XAI_API_KEY", test_xai_api_key_connectivity()))
    results.append(("ARCADE_API_KEY", test_arcade_api_key_connectivity()))
    
    print()
    
    # User credentials
    results.append(("ARCADE_USER_EMAIL", test_arcade_user_email()))
    results.append(("ARCADE_USER_PASSWORD", test_arcade_user_password()))
    
    print()
    
    # Configuration
    results.append(("LINKEDIN_PAGE", test_linkedin_page()))
    
    print()
    
    # Optional Twitter credentials
    twitter_email_result = test_twitter_email()
    twitter_password_result = test_twitter_password()
    if twitter_email_result is not None:
        results.append(("TWITTER_EMAIL", twitter_email_result))
    if twitter_password_result is not None:
        results.append(("TWITTER_PASSWORD", twitter_password_result))
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Skipped: {skipped}")
    print()
    
    return passed, failed, skipped


if __name__ == "__main__":
    run_all_connectivity_tests()

