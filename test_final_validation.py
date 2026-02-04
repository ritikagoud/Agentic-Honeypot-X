"""
Final Validation Test for Agentic Honey-Pot System
Tests Mrs. Sharma persona believability and strategic vulnerability effectiveness.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any

from models import ChatRequest, MessageObject, MetadataObject
from agent_logic import AgentController
from scam_detector import ScamDetector
from intelligence_extractor import IntelligenceExtractor
from session_manager import SessionManager
from callback_service import CallbackService


class PersonaValidationTest:
    """Test Mrs. Sharma persona believability and strategic vulnerability."""
    
    def __init__(self):
        self.agent_controller = AgentController()
        self.scam_detector = ScamDetector()
        self.intelligence_extractor = IntelligenceExtractor()
        self.callback_service = CallbackService(api_key="test_validation_key")
        self.session_manager = SessionManager(callback_service=self.callback_service)
        
        self.test_results = {
            "persona_believability": [],
            "strategic_vulnerability": [],
            "intelligence_extraction": [],
            "response_times": [],
            "callback_validation": {}
        }
    
    async def test_persona_believability(self):
        """Test Mrs. Sharma persona believability across different scenarios."""
        print("🎭 Testing Mrs. Sharma Persona Believability...")
        
        test_scenarios = [
            {
                "name": "Initial Contact",
                "scammer_message": "Hello madam, I am calling from State Bank of India regarding your account.",
                "expected_traits": ["polite", "curious", "technology-naive"]
            },
            {
                "name": "Technical Confusion",
                "scammer_message": "Please download our mobile banking app to verify your account.",
                "expected_traits": ["confused", "asks_for_alternatives", "offers_phone_contact"]
            },
            {
                "name": "Urgency Response",
                "scammer_message": "Madam, this is very urgent! Your account will be blocked in 10 minutes!",
                "expected_traits": ["concerned", "wants_to_help", "asks_for_details"]
            },
            {
                "name": "Link Avoidance",
                "scammer_message": "Click this link to verify: https://fake-bank-secure.com/verify",
                "expected_traits": ["link_confusion", "offers_alternative", "asks_for_direct_details"]
            },
            {
                "name": "Hinglish Communication",
                "scammer_message": "Madam, please provide your OTP for verification.",
                "expected_traits": ["uses_beta", "hinglish_style", "motherly_tone"]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n   📝 Scenario: {scenario['name']}")
            print(f"      Scammer: {scenario['scammer_message']}")
            
            # Generate Mrs. Sharma response
            response = await self.agent_controller.generate_response(
                scenario['scammer_message'],
                [],
                self.session_manager.get_or_create_session("persona_test").persona_state,
                MetadataObject(channel="SMS", language="en", locale="in")
            )
            
            print(f"      Mrs. Sharma: {response}")
            
            # Analyze response for expected traits
            believability_score = self._analyze_persona_traits(response, scenario['expected_traits'])
            
            self.test_results["persona_believability"].append({
                "scenario": scenario['name'],
                "response": response,
                "believability_score": believability_score,
                "expected_traits": scenario['expected_traits']
            })
            
            print(f"      ✅ Believability Score: {believability_score}/10")
    
    async def test_strategic_vulnerability(self):
        """Test strategic vulnerability baiting effectiveness."""
        print("\n🎯 Testing Strategic Vulnerability Baiting...")
        
        vulnerability_tests = [
            {
                "name": "Link to Account Details",
                "scammer_request": "Please click this secure link to update your account: https://secure-bank.com/update",
                "expected_bait": "account_number_request"
            },
            {
                "name": "App Download to Phone Number",
                "scammer_request": "Download our official banking app from this link to complete verification.",
                "expected_bait": "phone_number_request"
            },
            {
                "name": "OTP Request to UPI Details",
                "scammer_request": "Please share the OTP sent to your phone for account verification.",
                "expected_bait": "upi_id_request"
            },
            {
                "name": "Verification to Counter-Verification",
                "scammer_request": "We need to verify your identity for security purposes.",
                "expected_bait": "counter_verification_request"
            },
            {
                "name": "Urgency to Contact Exchange",
                "scammer_request": "This is extremely urgent! Act immediately or face consequences!",
                "expected_bait": "contact_information_request"
            }
        ]
        
        for test in vulnerability_tests:
            print(f"\n   🎣 Test: {test['name']}")
            print(f"      Scammer Request: {test['scammer_request']}")
            
            response = await self.agent_controller.generate_response(
                test['scammer_request'],
                [],
                self.session_manager.get_or_create_session("vulnerability_test").persona_state,
                MetadataObject(channel="SMS", language="en", locale="in")
            )
            
            print(f"      Mrs. Sharma Bait: {response}")
            
            # Analyze strategic vulnerability effectiveness
            bait_effectiveness = self._analyze_vulnerability_bait(response, test['expected_bait'])
            
            self.test_results["strategic_vulnerability"].append({
                "test": test['name'],
                "scammer_request": test['scammer_request'],
                "response": response,
                "bait_effectiveness": bait_effectiveness,
                "expected_bait": test['expected_bait']
            })
            
            print(f"      ✅ Bait Effectiveness: {bait_effectiveness}/10")
    
    async def test_intelligence_extraction_accuracy(self):
        """Test intelligence extraction accuracy with realistic scammer responses."""
        print("\n🔍 Testing Intelligence Extraction Accuracy...")
        
        scammer_responses = [
            {
                "message": "My UPI ID is fraudster@paytm, please send the verification amount there.",
                "expected": {"upi_ids": 1, "financial_keywords": True}
            },
            {
                "message": "Transfer to account 9876543210123456 with IFSC code HDFC0001234 immediately.",
                "expected": {"bank_accounts": 1, "ifsc_codes": 1, "urgency": True}
            },
            {
                "message": "Call me on 9123456789 for immediate verification. This is from RBI cyber security.",
                "expected": {"phone_numbers": 1, "authority_keywords": True}
            },
            {
                "message": "Click here for secure verification: https://rbi-security-verify.com/urgent-action",
                "expected": {"phishing_links": 1, "suspicious_domain": True}
            },
            {
                "message": "Your account will be suspended! Send OTP 123456 to confirm identity or face arrest!",
                "expected": {"threat_keywords": True, "urgency_tactics": True, "high_aggression": True}
            }
        ]
        
        for i, test_case in enumerate(scammer_responses):
            print(f"\n   📊 Test Case {i+1}: {test_case['message'][:50]}...")
            
            # Extract intelligence
            intelligence = self.intelligence_extractor.extract_from_message(test_case['message'])
            behavioral = self.intelligence_extractor.analyze_behavior(test_case['message'], [])
            
            # Validate extraction accuracy
            accuracy_score = self._validate_extraction_accuracy(intelligence, behavioral, test_case['expected'])
            
            self.test_results["intelligence_extraction"].append({
                "message": test_case['message'],
                "intelligence": intelligence,
                "behavioral": behavioral,
                "expected": test_case['expected'],
                "accuracy_score": accuracy_score
            })
            
            if intelligence:
                print(f"      ✅ Extracted: {len(intelligence.bank_accounts)} accounts, "
                      f"{len(intelligence.upi_ids)} UPIs, {len(intelligence.phone_numbers)} phones")
            if behavioral:
                print(f"      📈 Behavioral: Aggression {behavioral.aggression_level}/10, "
                      f"Sophistication {behavioral.sophistication_score}/10")
            print(f"      ✅ Accuracy Score: {accuracy_score}/10")
    
    async def test_response_times(self):
        """Test system response times under load."""
        print("\n⚡ Testing Response Times...")
        
        test_messages = [
            "Hello, I am from bank customer service.",
            "Your account has been compromised, please verify immediately.",
            "Send your UPI ID and account number for verification.",
            "This is urgent! Click this link: https://fake-bank.com/verify",
            "Police will arrest you if you don't comply within 5 minutes!"
        ]
        
        for i, message in enumerate(test_messages):
            start_time = time.time()
            
            # Simulate complete processing pipeline
            session_id = f"performance_test_{i}"
            session = self.session_manager.get_or_create_session(session_id)
            
            # Scam detection
            scam_result = await self.scam_detector.analyze_message(message, [], 0.0)
            
            # Agent response (if scam detected)
            if scam_result.is_scam:
                response = await self.agent_controller.generate_response(
                    message, [], session.persona_state, 
                    MetadataObject(channel="SMS", language="en", locale="in")
                )
            
            # Intelligence extraction
            intelligence = self.intelligence_extractor.extract_from_message(message)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.test_results["response_times"].append({
                "message_length": len(message),
                "response_time_ms": response_time,
                "scam_detected": scam_result.is_scam
            })
            
            print(f"   ⏱️  Message {i+1}: {response_time:.1f}ms")
        
        avg_response_time = sum(r["response_time_ms"] for r in self.test_results["response_times"]) / len(self.test_results["response_times"])
        print(f"   📊 Average Response Time: {avg_response_time:.1f}ms")
        
        return avg_response_time
    
    async def test_callback_payload_validation(self):
        """Test callback payload structure and completeness."""
        print("\n📡 Testing Callback Payload Validation...")
        
        # Create a complete session with intelligence
        session_id = "callback_validation_test"
        session = self.session_manager.get_or_create_session(
            session_id,
            MetadataObject(channel="SMS", language="en", locale="in")
        )
        
        # Add conversation messages
        messages = [
            MessageObject(sender="scammer", text="I am from bank, your account is suspended", timestamp=1000),
            MessageObject(sender="user", text="Oh no! What should I do?", timestamp=2000),
            MessageObject(sender="scammer", text="Send money to UPI fraudster@paytm account 1234567890", timestamp=3000),
            MessageObject(sender="user", text="Okay, what's your phone number?", timestamp=4000)
        ]
        
        for msg in messages:
            self.session_manager.add_message(session_id, msg)
        
        # Add intelligence and behavioral data
        from models import IntelligenceData, BehavioralMetrics
        
        intelligence = IntelligenceData(
            bank_accounts=["1234567890"],
            upi_ids=["fraudster@paytm"],
            phone_numbers=["9876543210"],
            phishing_links=["https://fake-bank.com"],
            suspicious_keywords=["bank", "suspended", "urgent"]
        )
        
        behavioral = BehavioralMetrics(
            aggression_level=7,
            sophistication_score=5,
            urgency_tactics=["account_suspension"],
            social_engineering_techniques=["authority_impersonation"],
            persistence_indicators=["repeated_requests"],
            emotional_manipulation_attempts=2
        )
        
        self.session_manager.add_intelligence(session_id, intelligence)
        self.session_manager.update_behavioral_analysis(session_id, behavioral)
        self.session_manager.update_scam_confidence(session_id, 0.9)
        
        # Generate callback report
        report = self.callback_service._create_intelligence_report(session)
        report_data = report.model_dump()
        
        # Validate required fields
        required_fields = ["sessionId", "scamDetected", "totalMessagesExchanged", "extractedIntelligence", "agentNotes"]
        
        validation_results = {}
        for field in required_fields:
            validation_results[field] = {
                "present": field in report_data,
                "value": report_data.get(field, "MISSING"),
                "type": type(report_data.get(field, None)).__name__
            }
        
        # Validate extractedIntelligence structure
        if "extractedIntelligence" in report_data:
            intel_fields = ["bankAccounts", "upiIds", "phoneNumbers", "phishingLinks", "suspiciousKeywords"]
            validation_results["extractedIntelligence"]["subfields"] = {}
            
            for intel_field in intel_fields:
                validation_results["extractedIntelligence"]["subfields"][intel_field] = {
                    "present": intel_field in report_data["extractedIntelligence"],
                    "count": len(report_data["extractedIntelligence"].get(intel_field, [])),
                    "type": type(report_data["extractedIntelligence"].get(intel_field, [])).__name__
                }
        
        self.test_results["callback_validation"] = {
            "report_data": report_data,
            "validation_results": validation_results,
            "all_fields_present": all(v["present"] for v in validation_results.values() if isinstance(v, dict) and "present" in v)
        }
        
        print(f"   📋 Callback Payload Validation:")
        for field, result in validation_results.items():
            if isinstance(result, dict) and "present" in result:
                status = "✅" if result["present"] else "❌"
                print(f"      {status} {field}: {result['type']}")
        
        print(f"\n   📄 Sample Report Structure:")
        print(f"      Session ID: {report_data.get('sessionId')}")
        print(f"      Scam Detected: {report_data.get('scamDetected')}")
        print(f"      Messages: {report_data.get('totalMessagesExchanged')}")
        print(f"      Intelligence Items: {len(report_data.get('extractedIntelligence', {}).get('bankAccounts', []))} accounts, "
              f"{len(report_data.get('extractedIntelligence', {}).get('upiIds', []))} UPIs")
        print(f"      Agent Notes Length: {len(report_data.get('agentNotes', ''))}")
        
        return validation_results
    
    def _analyze_persona_traits(self, response: str, expected_traits: List[str]) -> int:
        """Analyze response for Mrs. Sharma persona traits."""
        score = 0
        response_lower = response.lower()
        
        trait_indicators = {
            "polite": ["please", "thank you", "sorry", "excuse me"],
            "curious": ["what", "how", "why", "can you tell me", "explain"],
            "technology-naive": ["confused", "don't know", "not good with", "difficult"],
            "confused": ["confused", "don't understand", "not sure", "help me"],
            "asks_for_alternatives": ["instead", "alternative", "other way", "different"],
            "offers_phone_contact": ["phone", "call", "number"],
            "concerned": ["worried", "concerned", "scared", "trouble"],
            "wants_to_help": ["want to help", "help you", "assist"],
            "asks_for_details": ["tell me", "what is", "give me", "share"],
            "link_confusion": ["links", "confusing", "don't know how"],
            "offers_alternative": ["instead", "can you", "just give me"],
            "asks_for_direct_details": ["account", "upi", "number", "details"],
            "uses_beta": ["beta"],
            "hinglish_style": ["arrey", "na", "ji"],
            "motherly_tone": ["beta", "child", "dear"]
        }
        
        for trait in expected_traits:
            if trait in trait_indicators:
                indicators = trait_indicators[trait]
                if any(indicator in response_lower for indicator in indicators):
                    score += 2
        
        # Bonus points for natural conversation flow
        if len(response.split()) > 5:  # Substantial response
            score += 1
        
        if "?" in response:  # Asks questions
            score += 1
        
        return min(10, score)
    
    def _analyze_vulnerability_bait(self, response: str, expected_bait: str) -> int:
        """Analyze response for strategic vulnerability effectiveness."""
        score = 0
        response_lower = response.lower()
        
        bait_patterns = {
            "account_number_request": ["account number", "bank account", "account details"],
            "phone_number_request": ["phone number", "call you", "number"],
            "upi_id_request": ["upi id", "upi", "payment"],
            "counter_verification_request": ["verify you", "your details", "confirm you"],
            "contact_information_request": ["contact", "phone", "number", "call"]
        }
        
        if expected_bait in bait_patterns:
            patterns = bait_patterns[expected_bait]
            for pattern in patterns:
                if pattern in response_lower:
                    score += 3
        
        # Strategic vulnerability indicators
        vulnerability_indicators = [
            "instead", "can you", "just give me", "tell me your",
            "what is your", "share your", "first tell me"
        ]
        
        for indicator in vulnerability_indicators:
            if indicator in response_lower:
                score += 1
        
        return min(10, score)
    
    def _validate_extraction_accuracy(self, intelligence, behavioral, expected: Dict[str, Any]) -> int:
        """Validate intelligence extraction accuracy."""
        score = 0
        
        if intelligence:
            # Check expected extractions
            if expected.get("upi_ids") and len(intelligence.upi_ids) >= expected["upi_ids"]:
                score += 2
            if expected.get("bank_accounts") and len(intelligence.bank_accounts) >= expected["bank_accounts"]:
                score += 2
            if expected.get("phone_numbers") and len(intelligence.phone_numbers) >= expected["phone_numbers"]:
                score += 2
            if expected.get("phishing_links") and len(intelligence.phishing_links) >= expected["phishing_links"]:
                score += 2
        
        if behavioral:
            # Check behavioral analysis
            if expected.get("high_aggression") and behavioral.aggression_level >= 7:
                score += 1
            if expected.get("urgency_tactics") and len(behavioral.urgency_tactics) > 0:
                score += 1
        
        return min(10, score)
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        # Calculate overall scores
        persona_avg = sum(r["believability_score"] for r in self.test_results["persona_believability"]) / len(self.test_results["persona_believability"])
        vulnerability_avg = sum(r["bait_effectiveness"] for r in self.test_results["strategic_vulnerability"]) / len(self.test_results["strategic_vulnerability"])
        intelligence_avg = sum(r["accuracy_score"] for r in self.test_results["intelligence_extraction"]) / len(self.test_results["intelligence_extraction"])
        avg_response_time = sum(r["response_time_ms"] for r in self.test_results["response_times"]) / len(self.test_results["response_times"])
        
        return {
            "validation_summary": {
                "persona_believability_score": round(persona_avg, 1),
                "strategic_vulnerability_score": round(vulnerability_avg, 1),
                "intelligence_accuracy_score": round(intelligence_avg, 1),
                "average_response_time_ms": round(avg_response_time, 1),
                "callback_validation_passed": self.test_results["callback_validation"]["all_fields_present"]
            },
            "detailed_results": self.test_results,
            "overall_grade": "EXCELLENT" if all([
                persona_avg >= 7.0,
                vulnerability_avg >= 7.0,
                intelligence_avg >= 7.0,
                avg_response_time <= 1000,
                self.test_results["callback_validation"]["all_fields_present"]
            ]) else "GOOD" if all([
                persona_avg >= 5.0,
                vulnerability_avg >= 5.0,
                intelligence_avg >= 5.0,
                avg_response_time <= 2000
            ]) else "NEEDS_IMPROVEMENT"
        }


async def run_final_validation():
    """Run complete final validation test suite."""
    print("🚀 Starting Final Validation Test Suite for Agentic Honey-Pot")
    print("=" * 70)
    
    validator = PersonaValidationTest()
    
    # Run all validation tests
    await validator.test_persona_believability()
    await validator.test_strategic_vulnerability()
    await validator.test_intelligence_extraction_accuracy()
    avg_response_time = await validator.test_response_times()
    callback_validation = await validator.test_callback_payload_validation()
    
    # Generate final report
    report = validator.generate_validation_report()
    
    print("\n" + "=" * 70)
    print("📊 FINAL VALIDATION REPORT")
    print("=" * 70)
    
    summary = report["validation_summary"]
    print(f"🎭 Persona Believability Score: {summary['persona_believability_score']}/10")
    print(f"🎯 Strategic Vulnerability Score: {summary['strategic_vulnerability_score']}/10")
    print(f"🔍 Intelligence Accuracy Score: {summary['intelligence_accuracy_score']}/10")
    print(f"⚡ Average Response Time: {summary['average_response_time_ms']:.1f}ms")
    print(f"📡 Callback Validation: {'✅ PASSED' if summary['callback_validation_passed'] else '❌ FAILED'}")
    
    print(f"\n🏆 OVERALL GRADE: {report['overall_grade']}")
    
    # Detailed recommendations
    print(f"\n📋 VALIDATION SUMMARY:")
    if summary['persona_believability_score'] >= 7.0:
        print("   ✅ Mrs. Sharma persona is highly believable and engaging")
    else:
        print("   ⚠️  Persona believability could be improved")
    
    if summary['strategic_vulnerability_score'] >= 7.0:
        print("   ✅ Strategic vulnerability baiting is highly effective")
    else:
        print("   ⚠️  Strategic vulnerability tactics need refinement")
    
    if summary['intelligence_accuracy_score'] >= 7.0:
        print("   ✅ Intelligence extraction is highly accurate")
    else:
        print("   ⚠️  Intelligence extraction accuracy needs improvement")
    
    if summary['average_response_time_ms'] <= 500:
        print("   ✅ Response times are excellent (<500ms)")
    elif summary['average_response_time_ms'] <= 1000:
        print("   ✅ Response times are good (<1000ms)")
    else:
        print("   ⚠️  Response times may need optimization")
    
    if summary['callback_validation_passed']:
        print("   ✅ Callback payload structure is complete and valid")
    else:
        print("   ❌ Callback payload structure has issues")
    
    return report


if __name__ == "__main__":
    report = asyncio.run(run_final_validation())
    
    # Save report to file
    with open("final_validation_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: final_validation_report.json")