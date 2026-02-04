"""
Simple API Key Validation Test
Tests x-api-key validation without full application startup.
"""

import time
from fastapi import HTTPException
from main import verify_api_key


async def test_api_key_validation():
    """Test x-api-key validation function directly."""
    print("🔐 Testing x-api-key Header Validation...")
    
    test_cases = [
        {
            "name": "Valid API Key",
            "api_key": "valid_test_key",
            "should_pass": True
        },
        {
            "name": "Empty API Key",
            "api_key": "",
            "should_pass": False
        },
        {
            "name": "Whitespace API Key",
            "api_key": "   ",
            "should_pass": False
        },
        {
            "name": "None API Key",
            "api_key": None,
            "should_pass": False
        },
        {
            "name": "Long Valid API Key",
            "api_key": "very_long_api_key_that_should_still_work_fine_12345",
            "should_pass": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n   🧪 {test_case['name']}")
        
        try:
            start_time = time.time()
            result = await verify_api_key(test_case["api_key"])
            response_time = (time.time() - start_time) * 1000
            
            if test_case["should_pass"]:
                print(f"      ✅ PASSED: API key accepted")
                print(f"      ⏱️  Response Time: {response_time:.1f}ms")
                results.append({"test": test_case["name"], "passed": True, "time_ms": response_time})
            else:
                print(f"      ❌ FAILED: Should have been rejected but was accepted")
                results.append({"test": test_case["name"], "passed": False, "time_ms": response_time})
                
        except HTTPException as e:
            response_time = (time.time() - start_time) * 1000
            
            if not test_case["should_pass"]:
                print(f"      ✅ PASSED: Correctly rejected with status {e.status_code}")
                print(f"      📝 Error: {e.detail}")
                print(f"      ⏱️  Response Time: {response_time:.1f}ms")
                results.append({"test": test_case["name"], "passed": True, "time_ms": response_time})
            else:
                print(f"      ❌ FAILED: Should have been accepted but was rejected")
                print(f"      📝 Error: {e.detail}")
                results.append({"test": test_case["name"], "passed": False, "time_ms": response_time})
        
        except Exception as e:
            print(f"      ❌ UNEXPECTED ERROR: {e}")
            results.append({"test": test_case["name"], "passed": False, "time_ms": 0})
    
    # Summary
    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    avg_time = sum(r["time_ms"] for r in results) / len(results)
    
    print(f"\n📊 API Key Validation Summary:")
    print(f"   ✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"   ⏱️  Average Response Time: {avg_time:.1f}ms")
    print(f"   🎯 Validation Status: {'✅ EXCELLENT' if passed_tests == total_tests else '❌ NEEDS FIX'}")
    
    return {
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": passed_tests / total_tests,
        "average_time_ms": avg_time,
        "all_passed": passed_tests == total_tests
    }


if __name__ == "__main__":
    import asyncio
    
    print("🚀 Starting API Key Validation Test")
    print("=" * 50)
    
    result = asyncio.run(test_api_key_validation())
    
    if result["all_passed"]:
        print(f"\n🎉 ALL TESTS PASSED! x-api-key validation is working perfectly.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")
    
    print(f"\n📄 Final Score: {result['success_rate']*100:.1f}%")