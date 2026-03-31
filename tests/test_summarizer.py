"""
Tests for the TenderSummarizer utility.
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.summarizer import TenderSummarizer

# Load environment variables
load_dotenv()


def load_sample_tender():
    """Load a sample tender for testing."""
    tenders_file = Path(__file__).parent.parent / "sample_tenders.json"
    with open(tenders_file, 'r') as f:
        tenders = json.load(f)
    return tenders[0]  # Return first tender


def get_summarizer():
    """Create a TenderSummarizer instance."""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        return None
    return TenderSummarizer(api_key=api_key)


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
    """Test that summarizer initializes correctly."""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        print("⚠️  Skipping test_initialization: XAI_API_KEY not found")
        return True
    
    summarizer = TenderSummarizer(api_key=api_key)
    assert_true(summarizer.api_key == api_key, "API key should match")
    assert_true(summarizer.client is not None, "Client should be initialized")
    print("✅ test_initialization passed")
    return True


def test_initialization_without_key():
    """Test that initialization fails without API key."""
    original_key = os.environ.pop('XAI_API_KEY', None)
    
    try:
        assert_raises(ValueError, TenderSummarizer)
        print("✅ test_initialization_without_key passed")
        return True
    finally:
        # Restore the key
        if original_key:
            os.environ['XAI_API_KEY'] = original_key


def test_summarize_for_twitter():
    """Test Twitter summary generation."""
    summarizer = get_summarizer()
    if not summarizer:
        print("⚠️  Skipping test_summarize_for_twitter: XAI_API_KEY not found")
        return True
    
    sample_tender = load_sample_tender()
    summary = summarizer.summarize_for_twitter(sample_tender)
    
    # Check that summary is not empty
    assert_true(summary, "Twitter summary should not be empty")
    
    # Check length constraint (280 characters for Twitter)
    assert_true(len(summary) <= 280, f"Twitter summary too long: {len(summary)} chars")
    
    # Check that it contains some key information
    assert_true(len(summary) > 50, "Twitter summary seems too short")
    
    print(f"\nTwitter Summary ({len(summary)} chars):")
    print(summary)
    print("✅ test_summarize_for_twitter passed")
    return True


def test_summarize_for_linkedin():
    """Test LinkedIn summary generation."""
    summarizer = get_summarizer()
    if not summarizer:
        print("⚠️  Skipping test_summarize_for_linkedin: XAI_API_KEY not found")
        return True
    
    sample_tender = load_sample_tender()
    summary = summarizer.summarize_for_linkedin(sample_tender)
    
    # Check that summary is not empty
    assert_true(summary, "LinkedIn summary should not be empty")
    
    # LinkedIn posts can be longer
    assert_true(len(summary) <= 3000, f"LinkedIn summary too long: {len(summary)} chars")
    
    # Should be more detailed than Twitter
    assert_true(len(summary) > 100, "LinkedIn summary seems too short")
    
    print(f"\nLinkedIn Summary ({len(summary)} chars):")
    print(summary)
    print("✅ test_summarize_for_linkedin passed")
    return True


def test_create_hashtags():
    """Test hashtag generation."""
    summarizer = get_summarizer()
    if not summarizer:
        print("⚠️  Skipping test_create_hashtags: XAI_API_KEY not found")
        return True
    
    sample_tender = load_sample_tender()
    hashtags = summarizer.create_hashtags(sample_tender)
    
    # Check that hashtags are returned
    assert_true(isinstance(hashtags, list), "Hashtags should be a list")
    assert_true(len(hashtags) > 0, "Should generate at least one hashtag")
    
    # Check that all hashtags start with #
    for tag in hashtags:
        assert_true(tag.startswith('#'), f"Hashtag should start with #: {tag}")
    
    # Check for base hashtags
    assert_true('#PublicProcurement' in hashtags or '#Tenders' in hashtags, 
                "Should include base hashtags")
    
    print(f"\nGenerated Hashtags:")
    print(', '.join(hashtags))
    print("✅ test_create_hashtags passed")
    return True


def test_category_specific_hashtags():
    """Test that category-specific hashtags are generated correctly."""
    summarizer = get_summarizer()
    if not summarizer:
        print("⚠️  Skipping test_category_specific_hashtags: XAI_API_KEY not found")
        return True
    
    # Test IT category
    it_tender = {
        "title": "Software Development",
        "category": "IT & Software Development",
        "organization": "Test Org",
        "budget": "€100,000",
        "deadline": "2025-12-31",
        "description": "Test description"
    }
    
    hashtags = summarizer.create_hashtags(it_tender)
    assert_true(any('IT' in tag or 'Software' in tag for tag in hashtags),
                "Should include IT-related hashtags")
    
    # Test Construction category
    construction_tender = {
        "title": "Building Construction",
        "category": "Construction & Infrastructure",
        "organization": "Test Org",
        "budget": "€100,000",
        "deadline": "2025-12-31",
        "description": "Test description"
    }
    
    hashtags = summarizer.create_hashtags(construction_tender)
    assert_true(any('Construction' in tag or 'Infrastructure' in tag for tag in hashtags),
                "Should include construction-related hashtags")
    
    print("✅ test_category_specific_hashtags passed")
    return True


def test_all_sample_tenders():
    """Test summarization for all sample tenders."""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        print("⚠️  Skipping test_all_sample_tenders: XAI_API_KEY not found")
        return True
    
    summarizer = TenderSummarizer(api_key=api_key)
    
    # Load all sample tenders
    tenders_file = Path(__file__).parent.parent / "sample_tenders.json"
    with open(tenders_file, 'r') as f:
        tenders = json.load(f)
    
    results = []
    
    for tender in tenders:
        print(f"\n{'='*80}")
        print(f"Testing Tender: {tender['title']}")
        print(f"{'='*80}")
        
        # Generate Twitter summary
        twitter_summary = summarizer.summarize_for_twitter(tender)
        
        # Generate LinkedIn summary
        linkedin_summary = summarizer.summarize_for_linkedin(tender)
        
        # Generate hashtags
        hashtags = summarizer.create_hashtags(tender)
        
        result = {
            'tender_id': tender['id'],
            'tender_title': tender['title'],
            'twitter_summary': twitter_summary,
            'twitter_length': len(twitter_summary),
            'linkedin_summary': linkedin_summary,
            'linkedin_length': len(linkedin_summary),
            'hashtags': hashtags
        }
        
        results.append(result)
        
        print(f"\nTwitter ({len(twitter_summary)} chars):")
        print(twitter_summary)
        print(f"\nLinkedIn ({len(linkedin_summary)} chars):")
        print(linkedin_summary)
        print(f"\nHashtags: {', '.join(hashtags)}")
    
    # Save results to test-results directory
    output_dir = Path(__file__).parent.parent / "test-results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "summarizer_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")
    
    assert_true(len(results) == len(tenders), "Should process all tenders")
    print("✅ test_all_sample_tenders passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running TenderSummarizer Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_initialization,
        test_initialization_without_key,
        test_summarize_for_twitter,
        test_summarize_for_linkedin,
        test_create_hashtags,
        test_category_specific_hashtags,
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
