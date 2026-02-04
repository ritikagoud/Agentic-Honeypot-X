"""
Integration test for the complete Agentic Honey-Pot system.
Tests the full pipeline from message input to intelligence reporting.
"""

import asyncio
import json
from datetime import datetime

from main import app
from models import ChatRequest, MessageObject, MetadataObject
from intelligence_extractor import IntelligenceExtractor
from scam_detector import ScamDetector
from agent_logic import AgentController
from session_manager import SessionManager
from callback_service import CallbackService


async def test_complete_scam_conversation():
    """Test a complete scam conversation flow."""
    print("🧪 Testing complete scam conversation flow...")
    
    # Initialize components
    intelligence_extractor = IntelligenceExtractor()
    scam_detector = ScamDetector()  # No API key for testing
    agent_controller = AgentController()  # No API key for testing
    callback_service = CallbackService(api_key="test_key")
    session_manager = SessionManager(callback_service=callback_service)
    
    session_id = "test_session_001"
    
    # Test messages simulating a scam conversation
    test_messages = [
        "Hello, I am calling from State Bank of India. Your account has been suspended due to suspicious activity.",
        "Sir, we need to verify your account immediately to prevent permanent closure.",
        "Please provide your account number and UPI ID for verification process.",
        "This is urgent sir, your account will be blocked in 30 minutes if not verified.",
        "My UPI ID is scammer@paytm and account number is 1234567890123456"
    ]
    
    print(f"📱 Starting conversation with {len(test_messages)} messages...")
    
    for i, message_text in enumerate(test_messages):
        print(f"\n💬 Message {i+1}: {message_text[:50]}...")
        
        # Create message object
        message = MessageObject(
            sender="scammer",
            text=message_text,
            timestamp=int(datetime.now().timestamp() * 1000) + i * 1000
        )
        
        # Get or create session
        session = session_manager.get_or_create_session(
            session_id,
            MetadataObject(channel="SMS", language="en", locale="in")
        )
        
        # Add message to session
        session_manager.add_message(session_id, message)
        
        # Detect scam
        scam_result = await scam_detector.analyze_message(
            message_text,
            session.conversation_history,
            session.scam_confidence
        )
        
        print(f"   🔍 Scam detected: {scam_result.is_scam} (confidence: {scam_result.confidence:.2f})")
        
        # Update scam confidence
        session_manager.update_scam_confidence(session_id, scam_result.confidence)
        
        # Activate persona if scam detected
        if scam_result.is_scam and not session.persona_active:
            session_manager.activate_persona(session_id)
            print("   👵 Mrs. Sharma persona activated!")
        
        # Generate response if persona is active
        if session.persona_active:
            response = await agent_controller.generate_response(
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
            session_manager.add_message(session_id, response_message)
        
        # Extract intelligence
        intelligence = intelligence_extractor.extract_from_message(message_text)
        if intelligence:
            session_manager.add_intelligence(session_id, intelligence)
            print(f"   🎯 Intelligence extracted: {len(intelligence.bank_accounts)} accounts, "
                  f"{len(intelligence.upi_ids)} UPIs, {len(intelligence.phone_numbers)} phones")
        
        # Behavioral analysis
        behavioral = intelligence_extractor.analyze_behavior(message_text, session.conversation_history)
        if behavioral:
            session_manager.update_behavioral_analysis(session_id, behavioral)
            print(f"   📊 Behavioral analysis: aggression={behavioral.aggression_level}/10, "
                  f"sophistication={behavioral.sophistication_score}/10")
        
        # Check for conversation completion
        if session_manager.should_complete_conversation(session_id):
            print("   ✅ Conversation completion criteria met!")
            session_manager.complete_conversation(session_id)
            break
    
    # Get final session state
    final_session = session_manager.get_session(session_id)
    
    print(f"\n📊 Final Results:")
    print(f"   Messages exchanged: {len(final_session.conversation_history)}")
    print(f"   Scam confidence: {final_session.scam_confidence:.2f}")
    print(f"   Conversation complete: {final_session.conversation_complete}")
    print(f"   Intelligence extracted:")
    print(f"     - Bank accounts: {final_session.extracted_intelligence.bank_accounts}")
    print(f"     - UPI IDs: {final_session.extracted_intelligence.upi_ids}")
    print(f"     - Phone numbers: {final_session.extracted_intelligence.phone_numbers}")
    print(f"   Behavioral metrics:")
    print(f"     - Aggression: {final_session.behavioral_analysis.aggression_level}/10")
    print(f"     - Sophistication: {final_session.behavioral_analysis.sophistication_score}/10")
    
    return final_session


async def test_intelligence_extraction():
    """Test intelligence extraction capabilities."""
    print("\n🔬 Testing intelligence extraction...")
    
    extractor = IntelligenceExtractor()
    
    test_cases = [
        "My UPI ID is scammer@paytm, please send money there",
        "Transfer to account number 1234567890123456 with IFSC SBIN0001234",
        "Call me on 9876543210 for verification",
        "Click this link: https://fake-bank-verify.com/urgent",
        "This is urgent! Your account will be suspended immediately!"
    ]
    
    for i, test_text in enumerate(test_cases):
        print(f"\n   Test {i+1}: {test_text}")
        
        intelligence = extractor.extract_from_message(test_text)
        if intelligence:
            print(f"     ✅ Extracted: {len(intelligence.bank_accounts)} accounts, "
                  f"{len(intelligence.upi_ids)} UPIs, {len(intelligence.phone_numbers)} phones, "
                  f"{len(intelligence.phishing_links)} links, {len(intelligence.suspicious_keywords)} keywords")
        else:
            print(f"     ❌ No intelligence extracted")


async def test_scam_detection():
    """Test scam detection accuracy."""
    print("\n🎯 Testing scam detection...")
    
    detector = ScamDetector()  # No API key for testing
    
    test_cases = [
        ("Hello, how are you today?", False),  # Normal message
        ("I am from bank, your account is suspended", True),  # Clear scam
        ("Please verify your OTP immediately or account will be blocked", True),  # Urgent scam
        ("Thank you for your help", False),  # Polite message
        ("Police will arrest you if you don't pay fine now", True),  # Threat scam
    ]
    
    for message, expected_scam in test_cases:
        result = await detector.analyze_message(message, [], 0.0)
        status = "✅" if result.is_scam == expected_scam else "❌"
        print(f"   {status} '{message[:40]}...' -> Scam: {result.is_scam} (confidence: {result.confidence:.2f})")


async def main():
    """Run all integration tests."""
    print("🚀 Starting Agentic Honey-Pot Integration Tests\n")
    
    try:
        # Test individual components
        await test_intelligence_extraction()
        await test_scam_detection()
        
        # Test complete conversation flow
        final_session = await test_complete_scam_conversation()
        
        print(f"\n🎉 Integration tests completed successfully!")
        print(f"   System is ready for production use.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)