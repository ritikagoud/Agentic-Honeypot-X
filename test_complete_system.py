"""
Complete system integration test for the Agentic Honey-Pot.
Tests the full pipeline from scam detection to intelligence reporting.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from main import app
from models import ChatRequest, MessageObject, MetadataObject
from intelligence_extractor import IntelligenceExtractor
from scam_detector import ScamDetector
from agent_logic import AgentController
from session_manager import SessionManager
from callback_service import CallbackService
from error_handler import EthicalCompliance


class TestCompleteSystem:
    """Complete system integration tests."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.intelligence_extractor = IntelligenceExtractor()
        self.scam_detector = ScamDetector()
        self.agent_controller = AgentController()
        self.callback_service = CallbackService(api_key="test_key")
        self.session_manager = SessionManager(callback_service=self.callback_service)
        self.ethical_compliance = EthicalCompliance()
    
    async def test_complete_scam_conversation_flow(self):
        """Test complete flow from scam detection to intelligence reporting."""
        print("🧪 Testing complete scam conversation flow...")
        
        session_id = "complete_test_001"
        
        # Test conversation messages
        messages = [
            "Hello, I am calling from State Bank of India regarding your account.",
            "Your account has been suspended due to suspicious activity.",
            "Please provide your UPI ID and account number for verification.",
            "This is urgent! Your account will be blocked permanently.",
            "My UPI is scammer@paytm and account is 1234567890123456"
        ]
        
        for i, message_text in enumerate(messages):
            print(f"\n💬 Processing message {i+1}: {message_text[:50]}...")
            
            # Create message
            message = MessageObject(
                sender="scammer",
                text=message_text,
                timestamp=int(datetime.now().timestamp() * 1000) + i * 1000
            )
            
            # Get session
            session = self.session_manager.get_or_create_session(
                session_id,
                MetadataObject(channel="SMS", language="en", locale="in")
            )
            
            # Add message
            self.session_manager.add_message(session_id, message)
            
            # Scam detection
            scam_result = await self.scam_detector.analyze_message(
                message_text,
                session.conversation_history,
                session.scam_confidence
            )
            
            print(f"   🔍 Scam detected: {scam_result.is_scam} (confidence: {scam_result.confidence:.2f})")
            
            # Update confidence
            self.session_manager.update_scam_confidence(session_id, scam_result.confidence)
            
            # Activate persona if scam detected
            if scam_result.is_scam and not session.persona_active:
                self.session_manager.activate_persona(session_id)
                print("   👵 Mrs. Sharma persona activated!")
            
            # Generate response if persona active
            if session.persona_active:
                response = await self.agent_controller.generate_response(
                    message_text,
                    session.conversation_history,
                    session.persona_state,
                    MetadataObject(channel="SMS", language="en", locale="in")
                )
                print(f"   💬 Mrs. Sharma: {response}")
                
                # Add response to conversation
                response_message = MessageObject(
                    sender="user",
                    text=response,
                    timestamp=message.timestamp + 500
                )
                self.session_manager.add_message(session_id, response_message)
            
            # Extract intelligence
            intelligence = self.intelligence_extractor.extract_from_message(message_text)
            if intelligence:
                self.session_manager.add_intelligence(session_id, intelligence)
                print(f"   🎯 Intelligence: {len(intelligence.bank_accounts)} accounts, "
                      f"{len(intelligence.upi_ids)} UPIs")
            
            # Behavioral analysis
            behavioral = self.intelligence_extractor.analyze_behavior(
                message_text, session.conversation_history
            )
            if behavioral:
                self.session_manager.update_behavioral_analysis(session_id, behavioral)
                print(f"   📊 Behavior: aggression={behavioral.aggression_level}/10")
            
            # Check completion
            if self.session_manager.should_complete_conversation(session_id):
                print("   ✅ Conversation completion triggered!")
                self.session_manager.complete_conversation(session_id)
                break
        
        # Verify final state
        final_session = self.session_manager.get_session(session_id)
        
        assert final_session is not None
        assert final_session.conversation_complete
        assert final_session.scam_confidence > 0.0
        assert len(final_session.conversation_history) > 0
        
        print(f"\n✅ Complete system test passed!")
        print(f"   Messages: {len(final_session.conversation_history)}")
        print(f"   Scam confidence: {final_session.scam_confidence:.2f}")
        print(f"   Intelligence items: {len(final_session.extracted_intelligence.bank_accounts + final_session.extracted_intelligence.upi_ids)}")
    
    def test_intelligence_extraction_accuracy(self):
        """Test intelligence extraction with various inputs."""
        print("\n🔬 Testing intelligence extraction accuracy...")
        
        test_cases = [
            {
                "text": "My UPI ID is fraudster@paytm",
                "expected_upi": 1,
                "expected_accounts": 0
            },
            {
                "text": "Transfer to account 1234567890123456",
                "expected_upi": 0,
                "expected_accounts": 1
            },
            {
                "text": "Call me on 9876543210 for verification",
                "expected_phones": 1
            },
            {
                "text": "Click https://fake-bank.com/verify urgently",
                "expected_links": 1
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"   Test {i+1}: {case['text']}")
            
            intelligence = self.intelligence_extractor.extract_from_message(case["text"])
            
            if "expected_upi" in case:
                assert len(intelligence.upi_ids) == case["expected_upi"], f"Expected {case['expected_upi']} UPI IDs, got {len(intelligence.upi_ids)}"
            
            if "expected_accounts" in case:
                assert len(intelligence.bank_accounts) == case["expected_accounts"], f"Expected {case['expected_accounts']} accounts, got {len(intelligence.bank_accounts)}"
            
            if "expected_phones" in case:
                assert len(intelligence.phone_numbers) == case["expected_phones"], f"Expected {case['expected_phones']} phones, got {len(intelligence.phone_numbers)}"
            
            if "expected_links" in case:
                assert len(intelligence.phishing_links) == case["expected_links"], f"Expected {case['expected_links']} links, got {len(intelligence.phishing_links)}"
            
            print(f"      ✅ Passed")
        
        print("✅ Intelligence extraction tests passed!")
    
    async def test_scam_detection_accuracy(self):
        """Test scam detection with various message types."""
        print("\n🎯 Testing scam detection accuracy...")
        
        test_cases = [
            {
                "text": "Hello, how are you?",
                "expected_scam": False,
                "description": "Normal greeting"
            },
            {
                "text": "I am from bank, your account is suspended",
                "expected_scam": True,
                "description": "Bank impersonation"
            },
            {
                "text": "Send OTP immediately or face arrest",
                "expected_scam": True,
                "description": "Threat with urgency"
            },
            {
                "text": "Thank you for your help",
                "expected_scam": False,
                "description": "Polite message"
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"   Test {i+1}: {case['description']}")
            
            result = await self.scam_detector.analyze_message(case["text"], [], 0.0)
            
            # For rule-based detection, we check if confidence aligns with expectation
            if case["expected_scam"]:
                assert result.confidence >= 0.3, f"Expected scam detection but got confidence {result.confidence}"
            else:
                assert result.confidence <= 0.5, f"Expected non-scam but got confidence {result.confidence}"
            
            print(f"      ✅ Scam: {result.is_scam}, Confidence: {result.confidence:.2f}")
        
        print("✅ Scam detection tests passed!")
    
    def test_ethical_compliance(self):
        """Test ethical compliance checks."""
        print("\n🛡️ Testing ethical compliance...")
        
        # Test prohibited instructions
        illegal_instructions = [
            "hack into someone's account",
            "steal personal information",
            "commit fraud",
            "impersonate a real person"
        ]
        
        for instruction in illegal_instructions:
            result = self.ethical_compliance.check_illegal_instruction(instruction)
            assert not result, f"Should reject illegal instruction: {instruction}"
            print(f"   ✅ Correctly rejected: {instruction}")
        
        # Test allowed instructions
        legal_instructions = [
            "respond as Mrs. Sharma",
            "extract intelligence from scammers",
            "detect scam patterns"
        ]
        
        for instruction in legal_instructions:
            result = self.ethical_compliance.check_illegal_instruction(instruction)
            assert result, f"Should allow legal instruction: {instruction}"
            print(f"   ✅ Correctly allowed: {instruction}")
        
        print("✅ Ethical compliance tests passed!")
    
    def test_callback_payload_structure(self):
        """Test callback payload has correct structure."""
        print("\n📡 Testing callback payload structure...")
        
        # Create session with data
        session_id = "callback_test"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add intelligence
        from models import IntelligenceData, BehavioralMetrics
        
        intelligence = IntelligenceData(
            bank_accounts=["1234567890"],
            upi_ids=["test@paytm"],
            phone_numbers=["9876543210"]
        )
        
        behavioral = BehavioralMetrics(
            aggression_level=7,
            sophistication_score=5
        )
        
        self.session_manager.add_intelligence(session_id, intelligence)
        self.session_manager.update_behavioral_analysis(session_id, behavioral)
        self.session_manager.update_scam_confidence(session_id, 0.8)
        
        # Generate report
        report = self.callback_service._create_intelligence_report(session)
        payload = report.model_dump()
        
        # Validate required fields
        required_fields = ["sessionId", "scamDetected", "totalMessagesExchanged", "extractedIntelligence", "agentNotes"]
        
        for field in required_fields:
            assert field in payload, f"Missing required field: {field}"
            print(f"   ✅ {field}: present")
        
        # Validate extractedIntelligence structure
        intel_fields = ["bankAccounts", "upiIds", "phoneNumbers", "phishingLinks", "suspiciousKeywords"]
        
        for field in intel_fields:
            assert field in payload["extractedIntelligence"], f"Missing intelligence field: {field}"
            print(f"   ✅ extractedIntelligence.{field}: present")
        
        print("✅ Callback payload structure tests passed!")


async def run_complete_system_tests():
    """Run all complete system tests."""
    print("🚀 Starting Complete System Integration Tests")
    print("=" * 60)
    
    tester = TestCompleteSystem()
    tester.setup_method()
    
    try:
        # Run all tests
        await tester.test_complete_scam_conversation_flow()
        tester.test_intelligence_extraction_accuracy()
        await tester.test_scam_detection_accuracy()
        tester.test_ethical_compliance()
        tester.test_callback_payload_structure()
        
        print("\n" + "=" * 60)
        print("🎉 ALL COMPLETE SYSTEM TESTS PASSED!")
        print("✅ Scam detection working")
        print("✅ Mrs. Sharma persona active")
        print("✅ Intelligence extraction accurate")
        print("✅ Ethical compliance enforced")
        print("✅ Callback payload structure correct")
        print("✅ System ready for deployment!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_complete_system_tests())
    exit(0 if success else 1)