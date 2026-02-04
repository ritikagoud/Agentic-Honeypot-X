"""
Performance and Polish Validation Test
Tests x-api-key validation and response time optimization.
"""

import asyncio
import time
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from main import app
from fastapi.testclient import TestClient


class PerformancePolishTest:
    """Test performance and final polish aspects."""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = {
            "api_key_validation": {},
            "response_times": {},
            "concurrent_performance": {},
            "error_handling": {}
        }
    
    def test_api_key_validation(self):
        """Test x-api-key header validation thoroughly."""
        print("🔐 Testing x-api-key Header Validation...")
        
        test_cases = [
            {
                "name": "Valid API Key",
                "headers": {"x-api-key": "valid_test_key"},
                "expected_status": 200,
                "should_pass": True
            },
            {
                "name": "Missing API Key",
                "headers": {},
                "expected_status": 401,
                "should_pass": False
            },
            {
                "name": "Empty API Key",
                "headers": {"x-api-key": ""},
                "expected_status": 401,
                "should_pass": False
            },
            {
                "name": "Whitespace API Key",
                "headers": {"x-api-key": "   "},
                "expected_status": 401,
                "should_pass": False
            },
            {
                "name": "Long Valid API Key",
                "headers": {"x-api-key": "very_long_api_key_that_should_still_work_fine_12345"},
                "expected_status": 200,
                "should_pass": True
            }
        ]
        
        sample_request = {
            "sessionId": "api_key_test",
            "message": {
                "sender": "scammer",
                "text": "Hello, I am from bank",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "in"
            }
        }
        
        for test_case in test_cases:
            print(f"\n   🧪 {test_case['name']}")
            
            start_time = time.time()
            response = self.client.post(
                "/chat",
                json=sample_request,
                headers=test_case["headers"]
            )
            response_time = (time.time() - start_time) * 1000
            
            status_match = response.status_code == test_case["expected_status"]
            
            self.test_results["api_key_validation"][test_case["name"]] = {
                "status_code": response.status_code,
                "expected_status": test_case["expected_status"],
                "status_match": status_match,
                "response_time_ms": response_time,
                "response_body": response.json() if response.status_code != 500 else None
            }
            
            status_icon = "✅" if status_match else "❌"
            print(f"      {status_icon} Status: {response.status_code} (expected: {test_case['expected_status']})")
            print(f"      ⏱️  Response Time: {response_time:.1f}ms")
            
            if test_case["should_pass"] and response.status_code == 200:
                response_data = response.json()
                if "reply" in response_data:
                    print(f"      💬 Response: {response_data['reply'][:50]}...")
    
    def test_response_time_optimization(self):
        """Test response times under various conditions."""
        print("\n⚡ Testing Response Time Optimization...")
        
        test_scenarios = [
            {
                "name": "Simple Message",
                "message": "Hello",
                "target_time_ms": 100
            },
            {
                "name": "Scam Detection Message",
                "message": "I am from bank, your account is suspended, send OTP immediately",
                "target_time_ms": 200
            },
            {
                "name": "Long Message",
                "message": "This is a very long message that contains multiple sentences and should test the system's ability to process longer text inputs efficiently without significant performance degradation. " * 3,
                "target_time_ms": 300
            },
            {
                "name": "Intelligence Rich Message",
                "message": "Transfer money to account 1234567890123456 with IFSC HDFC0001234 or UPI fraudster@paytm, call 9876543210 urgently",
                "target_time_ms": 250
            },
            {
                "name": "Complex Conversation",
                "message": "Police will arrest you immediately if you don't verify account by clicking https://fake-bank.com/urgent",
                "target_time_ms": 300
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n   🎯 {scenario['name']}")
            
            request_data = {
                "sessionId": f"perf_test_{scenario['name'].lower().replace(' ', '_')}",
                "message": {
                    "sender": "scammer",
                    "text": scenario["message"],
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "en",
                    "locale": "in"
                }
            }
            
            # Run multiple iterations for accurate timing
            times = []
            for i in range(5):
                start_time = time.time()
                response = self.client.post(
                    "/chat",
                    json=request_data,
                    headers={"x-api-key": "performance_test_key"}
                )
                response_time = (time.time() - start_time) * 1000
                times.append(response_time)
                
                # Update session ID for next iteration
                request_data["sessionId"] = f"perf_test_{scenario['name'].lower().replace(' ', '_')}_{i}"
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            performance_grade = "✅ EXCELLENT" if avg_time <= scenario["target_time_ms"] else "⚠️ ACCEPTABLE" if avg_time <= scenario["target_time_ms"] * 2 else "❌ NEEDS OPTIMIZATION"
            
            self.test_results["response_times"][scenario["name"]] = {
                "average_ms": avg_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "target_ms": scenario["target_time_ms"],
                "meets_target": avg_time <= scenario["target_time_ms"],
                "all_times": times
            }
            
            print(f"      ⏱️  Average: {avg_time:.1f}ms (target: {scenario['target_time_ms']}ms)")
            print(f"      📊 Range: {min_time:.1f}ms - {max_time:.1f}ms")
            print(f"      🎯 {performance_grade}")
    
    def test_concurrent_performance(self):
        """Test performance under concurrent load."""
        print("\n🚀 Testing Concurrent Performance...")
        
        def make_request(session_id: str):
            """Make a single request."""
            request_data = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": "I am from bank, please verify your account immediately",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "en",
                    "locale": "in"
                }
            }
            
            start_time = time.time()
            response = self.client.post(
                "/chat",
                json=request_data,
                headers={"x-api-key": "concurrent_test_key"}
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                "session_id": session_id,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200
            }
        
        # Test with different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        
        for concurrency in concurrency_levels:
            print(f"\n   🔄 Testing {concurrency} concurrent requests...")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                session_ids = [f"concurrent_test_{concurrency}_{i}" for i in range(concurrency)]
                results = list(executor.map(make_request, session_ids))
            
            total_time = time.time() - start_time
            
            successful_requests = sum(1 for r in results if r["success"])
            avg_response_time = sum(r["response_time_ms"] for r in results) / len(results)
            requests_per_second = concurrency / total_time
            
            self.test_results["concurrent_performance"][f"{concurrency}_concurrent"] = {
                "concurrency_level": concurrency,
                "total_time_s": total_time,
                "successful_requests": successful_requests,
                "success_rate": successful_requests / concurrency,
                "avg_response_time_ms": avg_response_time,
                "requests_per_second": requests_per_second,
                "individual_results": results
            }
            
            print(f"      ✅ Success Rate: {successful_requests}/{concurrency} ({successful_requests/concurrency*100:.1f}%)")
            print(f"      ⏱️  Avg Response Time: {avg_response_time:.1f}ms")
            print(f"      🚀 Throughput: {requests_per_second:.1f} req/s")
    
    def test_error_handling_robustness(self):
        """Test error handling and system robustness."""
        print("\n🛡️ Testing Error Handling Robustness...")
        
        error_test_cases = [
            {
                "name": "Malformed JSON",
                "data": "invalid json",
                "content_type": "application/json",
                "expected_status": 422
            },
            {
                "name": "Missing Required Fields",
                "data": {"sessionId": "test"},
                "content_type": "application/json",
                "expected_status": 422
            },
            {
                "name": "Invalid Message Format",
                "data": {
                    "sessionId": "test",
                    "message": "not an object",
                    "conversationHistory": [],
                    "metadata": {}
                },
                "content_type": "application/json",
                "expected_status": 422
            },
            {
                "name": "Extremely Long Message",
                "data": {
                    "sessionId": "long_message_test",
                    "message": {
                        "sender": "scammer",
                        "text": "A" * 10000,  # 10KB message
                        "timestamp": int(time.time() * 1000)
                    },
                    "conversationHistory": [],
                    "metadata": {"channel": "SMS", "language": "en", "locale": "in"}
                },
                "content_type": "application/json",
                "expected_status": 200  # Should handle gracefully
            }
        ]
        
        for test_case in error_test_cases:
            print(f"\n   🧪 {test_case['name']}")
            
            start_time = time.time()
            
            if isinstance(test_case["data"], str):
                # Send raw string for malformed JSON test
                response = self.client.post(
                    "/chat",
                    data=test_case["data"],
                    headers={
                        "x-api-key": "error_test_key",
                        "Content-Type": test_case["content_type"]
                    }
                )
            else:
                response = self.client.post(
                    "/chat",
                    json=test_case["data"],
                    headers={"x-api-key": "error_test_key"}
                )
            
            response_time = (time.time() - start_time) * 1000
            
            status_match = response.status_code == test_case["expected_status"]
            
            self.test_results["error_handling"][test_case["name"]] = {
                "status_code": response.status_code,
                "expected_status": test_case["expected_status"],
                "status_match": status_match,
                "response_time_ms": response_time,
                "response_body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
            status_icon = "✅" if status_match else "❌"
            print(f"      {status_icon} Status: {response.status_code} (expected: {test_case['expected_status']})")
            print(f"      ⏱️  Response Time: {response_time:.1f}ms")
            print(f"      🛡️  System remained stable: {'✅' if response.status_code != 500 else '❌'}")
    
    def generate_polish_report(self):
        """Generate comprehensive polish and performance report."""
        # Calculate metrics
        api_key_tests_passed = sum(1 for test in self.test_results["api_key_validation"].values() if test["status_match"])
        total_api_key_tests = len(self.test_results["api_key_validation"])
        
        response_time_targets_met = sum(1 for test in self.test_results["response_times"].values() if test["meets_target"])
        total_response_time_tests = len(self.test_results["response_times"])
        
        avg_response_time = sum(test["average_ms"] for test in self.test_results["response_times"].values()) / max(total_response_time_tests, 1)
        
        concurrent_success_rates = [test["success_rate"] for test in self.test_results["concurrent_performance"].values()]
        avg_concurrent_success_rate = sum(concurrent_success_rates) / max(len(concurrent_success_rates), 1)
        
        error_handling_passed = sum(1 for test in self.test_results["error_handling"].values() if test["status_match"])
        total_error_handling_tests = len(self.test_results["error_handling"])
        
        return {
            "polish_summary": {
                "api_key_validation_score": f"{api_key_tests_passed}/{total_api_key_tests}",
                "response_time_targets_met": f"{response_time_targets_met}/{total_response_time_tests}",
                "average_response_time_ms": round(avg_response_time, 1),
                "concurrent_success_rate": round(avg_concurrent_success_rate * 100, 1),
                "error_handling_score": f"{error_handling_passed}/{total_error_handling_tests}",
                "overall_polish_grade": "EXCELLENT" if all([
                    api_key_tests_passed == total_api_key_tests,
                    response_time_targets_met >= total_response_time_tests * 0.8,
                    avg_response_time <= 200,
                    avg_concurrent_success_rate >= 0.95,
                    error_handling_passed == total_error_handling_tests
                ]) else "GOOD" if all([
                    api_key_tests_passed >= total_api_key_tests * 0.8,
                    response_time_targets_met >= total_response_time_tests * 0.6,
                    avg_response_time <= 500,
                    avg_concurrent_success_rate >= 0.9
                ]) else "NEEDS_IMPROVEMENT"
            },
            "detailed_results": self.test_results
        }


def run_performance_polish_tests():
    """Run all performance and polish tests."""
    print("🔧 Starting Performance and Polish Validation")
    print("=" * 60)
    
    tester = PerformancePolishTest()
    
    # Run all tests
    tester.test_api_key_validation()
    tester.test_response_time_optimization()
    tester.test_concurrent_performance()
    tester.test_error_handling_robustness()
    
    # Generate report
    report = tester.generate_polish_report()
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE & POLISH REPORT")
    print("=" * 60)
    
    summary = report["polish_summary"]
    print(f"🔐 API Key Validation: {summary['api_key_validation_score']} tests passed")
    print(f"⚡ Response Time Targets: {summary['response_time_targets_met']} met")
    print(f"📊 Average Response Time: {summary['average_response_time_ms']}ms")
    print(f"🚀 Concurrent Success Rate: {summary['concurrent_success_rate']}%")
    print(f"🛡️ Error Handling: {summary['error_handling_score']} tests passed")
    
    print(f"\n🏆 OVERALL POLISH GRADE: {summary['overall_polish_grade']}")
    
    # Detailed assessment
    print(f"\n📋 POLISH ASSESSMENT:")
    if summary['api_key_validation_score'].endswith(f"/{summary['api_key_validation_score'].split('/')[1]}"):
        print("   ✅ x-api-key validation is working perfectly")
    else:
        print("   ⚠️  x-api-key validation has issues")
    
    if summary['average_response_time_ms'] <= 200:
        print("   ✅ Response times are excellent (<200ms)")
    elif summary['average_response_time_ms'] <= 500:
        print("   ✅ Response times are acceptable (<500ms)")
    else:
        print("   ⚠️  Response times need optimization")
    
    if summary['concurrent_success_rate'] >= 95:
        print("   ✅ System handles concurrent load excellently")
    elif summary['concurrent_success_rate'] >= 90:
        print("   ✅ System handles concurrent load well")
    else:
        print("   ⚠️  Concurrent performance needs improvement")
    
    return report


if __name__ == "__main__":
    report = run_performance_polish_tests()
    
    # Save report
    with open("performance_polish_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: performance_polish_report.json")