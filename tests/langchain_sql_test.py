"""
Tests for LangChain SQL Agent utility.
Tests natural language to SQL queries using XAI API.
"""
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.langchain_sql import LangChainSQLAgent

# Load environment variables
load_dotenv()

# Test questions
TEST_QUESTIONS = [
    "how many tenders are there total",
    "show me the user count over time",
    "show me the tenders and cpv codes / sectors with highest value"
]


def run_test_question(agent: LangChainSQLAgent, question: str) -> dict:
    """
    Run a test question and return results.
    
    Args:
        agent: LangChainSQLAgent instance
        question: Natural language question
        
    Returns:
        Dictionary with test results including nested dataframe data
    """
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    try:
        result = agent.query_to_dataframe(question)
        
        # Check if we got a valid dataframe
        df = result.get("dataframe")
        sql_query = result.get("sql_query")
        error = result.get("error")
        
        success = bool(df is not None and not df.empty and error is None and sql_query)
        
        # Build nested JSON structure with dataframe data
        dataframe_data = None
        if df is not None:
            # Convert dataframe to dict, handling non-serializable types
            # Convert Timestamp and other datetime objects to strings
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_copy[col].dtype):
                    df_copy[col] = df_copy[col].astype(str)
                elif df_copy[col].dtype == 'object':
                    # Check if column contains datetime objects
                    try:
                        df_copy[col] = df_copy[col].apply(lambda x: str(x) if hasattr(x, 'isoformat') else x)
                    except:
                        pass
            
            dataframe_data = {
                "columns": list(df.columns),
                "rows": df_copy.to_dict('records'),  # List of dictionaries, one per row
                "row_count": len(df),
                "shape": list(df.shape)  # [rows, columns]
            }
        
        test_result = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "sql_query": sql_query,
            "error": error,
            "dataframe": dataframe_data  # Nested JSON structure with dataframe data
        }
        
        if test_result["success"]:
            print(f"✅ Success")
            print(f"SQL Query: {test_result['sql_query']}")
            print(f"Rows returned: {test_result['dataframe']['row_count']}")
            print(f"DataFrame columns: {test_result['dataframe']['columns']}")
            print(f"First few rows:")
            if df is not None:
                print(df.head().to_string())
        else:
            print(f"❌ Failed")
            print(f"Error: {test_result.get('error', 'Unknown error')}")
            if sql_query:
                print(f"SQL Query (generated but failed): {sql_query}")
            if df is not None:
                print(f"DataFrame (error): {df.to_string()}")
        
        return test_result
        
    except Exception as e:
        import traceback
        print(f"❌ Exception: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "sql_query": None,
            "error": str(e),
            "dataframe": None
        }


def test_total_tenders(agent: LangChainSQLAgent) -> dict:
    """Test: How many tenders are there total?"""
    return run_test_question(agent, "how many tenders are there total")


def test_user_count_over_time(agent: LangChainSQLAgent) -> dict:
    """Test: Show me the user count over time."""
    return run_test_question(agent, "show me the user count over time")


def test_tenders_with_highest_value(agent: LangChainSQLAgent) -> dict:
    """Test: Show me the tenders and cpv codes / sectors with highest value."""
    return run_test_question(
        agent,
        "show me the tenders and cpv codes / sectors with highest value"
    )


def run_all_tests():
    """Run all tests and save results."""
    print("="*60)
    print("LangChain SQL Agent Tests")
    print("="*60)
    print()
    
    # Check environment variables
    db_url = os.getenv('EE_DB_URL')
    api_key = os.getenv('XAI_API_KEY')
    
    if not db_url:
        print("❌ Error: EE_DB_URL not found in environment")
        return 1
    
    if not api_key:
        print("❌ Error: XAI_API_KEY not found in environment")
        return 1
    
    # Initialize agent
    print("🔌 Initializing SQL Agent...")
    try:
        agent = LangChainSQLAgent(verbose=False)
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return 1
    
    # Run tests
    results = []
    
    # Test 1: Total tenders
    print("\n" + "="*60)
    print("Test 1: Total Tenders Count")
    print("="*60)
    result1 = test_total_tenders(agent)
    results.append(result1)
    
    # Test 2: User count over time
    print("\n" + "="*60)
    print("Test 2: User Count Over Time")
    print("="*60)
    result2 = test_user_count_over_time(agent)
    results.append(result2)
    
    # Test 3: Tenders with highest value
    print("\n" + "="*60)
    print("Test 3: Tenders with Highest Value")
    print("="*60)
    result3 = test_tenders_with_highest_value(agent)
    results.append(result3)
    
    # Save results
    output_dir = Path(__file__).parent.parent / "test-results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"langchain_sql_test_results_{timestamp}.json"
    
    test_summary = {
        "test_run_timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total tests: {test_summary['total_tests']}")
    print(f"✅ Passed: {test_summary['passed']}")
    print(f"❌ Failed: {test_summary['failed']}")
    print(f"\nResults saved to: {output_file}")
    
    return 0 if test_summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

