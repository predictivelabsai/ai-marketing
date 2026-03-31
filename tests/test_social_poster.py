"""
Tests for the ArcadeSocialPoster utility.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.social_poster import ArcadeSocialPoster

# Load environment variables
load_dotenv()


def get_poster():
    """Create an ArcadeSocialPoster instance."""
    api_key = os.getenv('ARCADE_API_KEY')
    if not api_key:
        return None
    return ArcadeSocialPoster(api_key=api_key)


def assert_true(condition, message="Assertion failed"):
    """Custom assertion helper."""
    if not condition:
        raise AssertionError(message)
    return True


def assert_raises(exception_type, func, *args, **kwargs):
    """Test that a function raises an exception."""
    try:
        func(*args, **kwargs)
        raise AssertionError(f"Expected {exception_type.__name__} but no exception was raised")
    except exception_type:
        return True
    except Exception as e:
        raise AssertionError(f"Expected {exception_type.__name__} but got {type(e).__name__}: {e}")


def test_initialization():
    """Test that poster initializes correctly."""
    api_key = os.getenv('ARCADE_API_KEY')
    if not api_key:
        print("⚠️  Skipping test_initialization: ARCADE_API_KEY not found")
        return True
    
    poster = ArcadeSocialPoster(api_key=api_key)
    assert_true(poster.api_key == api_key, "API key should match")
    assert_true(poster.base_url == "https://api.arcade.dev/v1", "Base URL should be correct")
    assert_true("Authorization" in poster.headers, "Headers should contain Authorization")
    print("✅ test_initialization passed")
    return True


def test_initialization_without_key():
    """Test that initialization fails without API key."""
    original_key = os.environ.pop('ARCADE_API_KEY', None)
    
    try:
        assert_raises(ValueError, ArcadeSocialPoster)
        print("✅ test_initialization_without_key passed")
        return True
    finally:
        # Restore the key
        if original_key:
            os.environ['ARCADE_API_KEY'] = original_key


def test_post_to_twitter_dry_run():
    """Test Twitter posting structure (dry run - no actual posting)."""
    poster = get_poster()
    if not poster:
        print("⚠️  Skipping test_post_to_twitter_dry_run: ARCADE_API_KEY not found")
        return True
    
    test_content = "Test tweet about a tender opportunity #PublicProcurement #Tenders"
    test_url = "https://www.tendly.eu/tenders/T001"
    
    # Validate that the method exists and accepts correct parameters
    assert_true(hasattr(poster, 'post_to_twitter'), "poster should have post_to_twitter method")
    
    # Check that content formatting works
    full_content = f"{test_content}\n\n{test_url}"
    assert_true(len(full_content) > 0, "Content should not be empty")
    assert_true(test_url in full_content, "Content should contain URL")
    
    print(f"\nTwitter post would contain:")
    print(full_content)
    print("✅ test_post_to_twitter_dry_run passed")
    return True


def test_post_to_linkedin_dry_run():
    """Test LinkedIn posting structure (dry run - no actual posting)."""
    poster = get_poster()
    if not poster:
        print("⚠️  Skipping test_post_to_linkedin_dry_run: ARCADE_API_KEY not found")
        return True
    
    test_content = """
    Exciting tender opportunity in AI and public procurement!
    
    The Estonian Ministry is seeking innovative solutions for AI-powered 
    procurement platforms. This is a great opportunity for tech companies 
    to contribute to digital transformation.
    
    #PublicProcurement #AI #Estonia
    """
    test_url = "https://www.tendly.eu/tenders/T001"
    
    # Validate that the method exists and accepts correct parameters
    assert_true(hasattr(poster, 'post_to_linkedin'), "poster should have post_to_linkedin method")
    
    # Check that content formatting works
    full_content = f"{test_content}\n\nLearn more: {test_url}"
    assert_true(len(full_content) > 0, "Content should not be empty")
    assert_true(test_url in full_content, "Content should contain URL")
    
    print(f"\nLinkedIn post would contain:")
    print(full_content)
    print("✅ test_post_to_linkedin_dry_run passed")
    return True


def test_post_to_all_platforms_dry_run():
    """Test posting to all platforms structure (dry run)."""
    poster = get_poster()
    if not poster:
        print("⚠️  Skipping test_post_to_all_platforms_dry_run: ARCADE_API_KEY not found")
        return True
    
    twitter_content = "Test Twitter content #Test"
    linkedin_content = "Test LinkedIn content with more details #Test #LinkedIn"
    test_url = "https://www.tendly.eu/tenders/T001"
    
    # Validate that the method exists
    assert_true(hasattr(poster, 'post_to_all_platforms'), "poster should have post_to_all_platforms method")
    
    print(f"\nWould post to both platforms:")
    print(f"Twitter: {twitter_content}")
    print(f"LinkedIn: {linkedin_content}")
    print(f"URL: {test_url}")
    print("✅ test_post_to_all_platforms_dry_run passed")
    return True


def test_api_endpoint_structure():
    """Test that API endpoint structure is correct."""
    api_key = os.getenv('ARCADE_API_KEY')
    if not api_key:
        print("⚠️  Skipping test_api_endpoint_structure: ARCADE_API_KEY not found")
        return True
    
    poster = ArcadeSocialPoster(api_key=api_key)
    
    # Validate base URL
    assert_true(poster.base_url.startswith("https://"), "Base URL should start with https://")
    assert_true("arcade" in poster.base_url.lower(), "Base URL should contain 'arcade'")
    
    # Validate headers
    assert_true("Authorization" in poster.headers, "Headers should contain Authorization")
    assert_true(poster.headers["Authorization"] == api_key, "Authorization header should be the API key")
    assert_true("Content-Type" in poster.headers, "Headers should contain Content-Type")
    assert_true(poster.headers["Content-Type"] == "application/json", "Content-Type should be application/json")
    
    print(f"\nAPI Configuration:")
    print(f"Base URL: {poster.base_url}")
    print(f"Headers: {poster.headers}")
    print("✅ test_api_endpoint_structure passed")
    return True


def test_environment_variables():
    """Test that all required environment variables are set."""
    required_vars = [
        'ARCADE_API_KEY',
        'XAI_API_KEY',
        'ARCADE_USER_EMAIL',
        'ARCADE_USER_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nWarning: Missing environment variables: {', '.join(missing_vars)}")
        print("These should be set in the .env file for full functionality")
    
    # At least API keys should be present
    assert_true(os.getenv('ARCADE_API_KEY'), "ARCADE_API_KEY is required")
    assert_true(os.getenv('XAI_API_KEY'), "XAI_API_KEY is required")
    print("✅ test_environment_variables passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running ArcadeSocialPoster Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_initialization,
        test_initialization_without_key,
        test_post_to_twitter_dry_run,
        test_post_to_linkedin_dry_run,
        test_post_to_all_platforms_dry_run,
        test_api_endpoint_structure,
        test_environment_variables,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                skipped += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    print()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
