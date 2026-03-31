"""
Individual post test to debug posting issues.
Takes a tender ID, loads summary from JSON, and posts to debug.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.social_poster import ArcadeSocialPoster

load_dotenv()


def load_summary(tender_id: str, platform: str):
    """Load summary from JSON file."""
    summaries_dir = Path(__file__).parent.parent / "summaries"
    filename = f"{platform}_summary_{tender_id}.json"
    filepath = summaries_dir / filename
    
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def test_post(tender_id: str, platform: str = None):
    """Test posting for a specific tender."""
    print("=" * 60)
    print(f"Testing Post for Tender ID: {tender_id}")
    print("=" * 60)
    print()
    
    # Load summaries
    x_summary = load_summary(tender_id, 'x')
    linkedin_summary = load_summary(tender_id, 'linkedin')
    
    if not x_summary and not linkedin_summary:
        print(f"❌ No summaries found for tender {tender_id}")
        print(f"   Looking for: summaries/x_summary_{tender_id}.json")
        print(f"   Looking for: summaries/linkedin_summary_{tender_id}.json")
        return
    
    # Initialize poster
    try:
        poster = ArcadeSocialPoster()
        print("✅ ArcadeSocialPoster initialized")
        print(f"   Base URL: {poster.base_url}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize poster: {e}")
        return
    
    # Test Twitter/X post
    if (platform is None or platform == 'twitter' or platform == 'x') and x_summary:
        print("🐦 Testing Twitter/X Post")
        print("-" * 60)
        content = x_summary.get('content', '')
        print(f"Content length: {len(content)} chars")
        print(f"Content preview: {content[:100]}...")
        print()
        
        try:
            result = poster.post_to_twitter(content)
            print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
            print(f"Platform: {result['platform']}")
            
            if result['success']:
                print("Response:")
                print(json.dumps(result.get('response', {}), indent=2))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                print()
                print("Full response:")
                print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Test LinkedIn post
    if (platform is None or platform == 'linkedin') and linkedin_summary:
        print("💼 Testing LinkedIn Post")
        print("-" * 60)
        content = linkedin_summary.get('content', '')
        print(f"Content length: {len(content)} chars")
        print(f"Content preview: {content[:100]}...")
        print()
        
        try:
            result = poster.post_to_linkedin(content)
            print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
            print(f"Platform: {result['platform']}")
            
            if result['success']:
                print("Response:")
                print(json.dumps(result.get('response', {}), indent=2))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                print()
                print("Full response:")
                print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
        
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tests/individual_post_test.py <tender_id> [platform]")
        print("Example: python tests/individual_post_test.py T002")
        print("Example: python tests/individual_post_test.py T002 twitter")
        sys.exit(1)
    
    tender_id = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else None
    
    test_post(tender_id, platform)

