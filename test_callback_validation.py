"""
Callback Payload Validation Test
Validates the callback payload structure sent to hackathon endpoint.
"""

import json
from datetime import datetime
from models import IntelligenceReport, ExtractedIntelligence, SessionData, MessageObject, MetadataObject, IntelligenceData, BehavioralMetrics, PersonaState
from callback_service import CallbackService


def test_callback_payload_structure():
    """Test that callback payload includes all required fields."""
    print("📡 Testing Callback Payload Structure...")
    
    # Create a realistic session with complete data
    session = SessionData(
        session_id="hackathon_validation_test",
        conversation_history=[
            MessageObject(sender="scammer", text="I am from bank, your account is suspended", timestamp=1000),
            MessageObject(sender="user", text="Oh no! What should I do beta?", timestamp=2000),
            MessageObject(sender="scammer", text="Send money to UPI fraudster@paytm account 1234567890123456", timestamp=3000),
            MessageObject(sender="user", text="Okay, what's your phone number for verification?", timestamp=4000),
            MessageObject(sender="scammer", text="Call me on 9876543210 immediately", timestamp=5000),
            MessageObject(sender="user", text="Sure beta, I'll send money to your account", timestamp=6000)
        ],
        extracted_intelligence=IntelligenceData(
            bank_accounts=["1234567890123456"],
            ifsc_codes=["HDFC0001234"],
            upi_ids=["fraudster@paytm"],
            phone_numbers=["9876543210"],
            phishing_links=["https://fake-bank-verify.com"],
            suspicious_keywords=["bank", "suspended", "urgent", "immediately", "verify"]
        ),
        scam_confidence=0.95,
        persona_active=True,
        conversation_complete=True,
        behavioral_analysis=BehavioralMetrics(
            aggression_level=8,
            sophistication_score=6,
            urgency_tactics=["account_suspension", "immediate_action"],
            social_engineering_techniques=["authority_impersonation", "urgency_creation"],
            persistence_indicators=["repeated_requests", "escalating_threats"],
            emotional_manipulation_attempts=3
        ),
        persona_state=PersonaState(),
        start_time=datetime.now(),
        last_activity=datetime.now(),
        metadata=MetadataObject(channel="SMS", language="en", locale="in")
    )
    
    # Create callback service and generate report
    callback_service = CallbackService(api_key="hackathon_test_key")
    report = callback_service._create_intelligence_report(session)
    
    # Convert to the actual payload that would be sent
    payload = report.model_dump()
    
    print(f"\n📋 Generated Callback Payload:")
    print(json.dumps(payload, indent=2))
    
    # Validate required fields
    required_fields = {
        "sessionId": str,
        "scamDetected": bool,
        "totalMessagesExchanged": int,
        "extractedIntelligence": dict,
        "agentNotes": str
    }
    
    validation_results = {}
    all_fields_valid = True
    
    print(f"\n🔍 Field Validation:")
    
    for field_name, expected_type in required_fields.items():
        if field_name in payload:
            actual_value = payload[field_name]
            actual_type = type(actual_value)
            type_match = isinstance(actual_value, expected_type)
            
            validation_results[field_name] = {
                "present": True,
                "type_correct": type_match,
                "expected_type": expected_type.__name__,
                "actual_type": actual_type.__name__,
                "value": actual_value if field_name != "agentNotes" else f"[{len(str(actual_value))} chars]"
            }
            
            status = "✅" if type_match else "❌"
            print(f"   {status} {field_name}: {actual_type.__name__} (expected: {expected_type.__name__})")
            
            if not type_match:
                all_fields_valid = False
        else:
            validation_results[field_name] = {
                "present": False,
                "type_correct": False,
                "expected_type": expected_type.__name__,
                "actual_type": "MISSING",
                "value": None
            }
            print(f"   ❌ {field_name}: MISSING")
            all_fields_valid = False
    
    # Validate extractedIntelligence subfields
    if "extractedIntelligence" in payload:
        print(f"\n🔍 ExtractedIntelligence Subfields:")
        
        intel_fields = {
            "bankAccounts": list,
            "upiIds": list,
            "phoneNumbers": list,
            "phishingLinks": list,
            "suspiciousKeywords": list
        }
        
        intel_data = payload["extractedIntelligence"]
        
        for field_name, expected_type in intel_fields.items():
            if field_name in intel_data:
                actual_value = intel_data[field_name]
                actual_type = type(actual_value)
                type_match = isinstance(actual_value, expected_type)
                
                status = "✅" if type_match else "❌"
                count = len(actual_value) if isinstance(actual_value, list) else "N/A"
                print(f"   {status} {field_name}: {actual_type.__name__} with {count} items")
                
                if not type_match:
                    all_fields_valid = False
            else:
                print(f"   ❌ {field_name}: MISSING")
                all_fields_valid = False
    
    # Validate data content
    print(f"\n📊 Data Content Validation:")
    
    content_checks = [
        ("sessionId not empty", len(payload.get("sessionId", "")) > 0),
        ("scamDetected is boolean", isinstance(payload.get("scamDetected"), bool)),
        ("totalMessagesExchanged > 0", payload.get("totalMessagesExchanged", 0) > 0),
        ("agentNotes not empty", len(payload.get("agentNotes", "")) > 0),
        ("bankAccounts extracted", len(payload.get("extractedIntelligence", {}).get("bankAccounts", [])) > 0),
        ("upiIds extracted", len(payload.get("extractedIntelligence", {}).get("upiIds", [])) > 0),
        ("phoneNumbers extracted", len(payload.get("extractedIntelligence", {}).get("phoneNumbers", [])) > 0),
        ("agentNotes contains analysis", "aggression" in payload.get("agentNotes", "").lower())
    ]
    
    content_score = 0
    for check_name, check_result in content_checks:
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if check_result:
            content_score += 1
    
    # Generate final assessment
    print(f"\n📊 Validation Summary:")
    print(f"   🔧 Required Fields: {'✅ ALL PRESENT' if all_fields_valid else '❌ MISSING FIELDS'}")
    print(f"   📊 Content Quality: {content_score}/{len(content_checks)} checks passed")
    print(f"   📄 Payload Size: {len(json.dumps(payload))} bytes")
    
    # Sample of actual values
    print(f"\n📋 Sample Values:")
    print(f"   Session ID: {payload.get('sessionId')}")
    print(f"   Scam Detected: {payload.get('scamDetected')}")
    print(f"   Messages: {payload.get('totalMessagesExchanged')}")
    print(f"   Bank Accounts: {payload.get('extractedIntelligence', {}).get('bankAccounts', [])}")
    print(f"   UPI IDs: {payload.get('extractedIntelligence', {}).get('upiIds', [])}")
    print(f"   Phone Numbers: {payload.get('extractedIntelligence', {}).get('phoneNumbers', [])}")
    print(f"   Agent Notes Preview: {payload.get('agentNotes', '')[:100]}...")
    
    return {
        "all_fields_valid": all_fields_valid,
        "content_score": content_score,
        "total_content_checks": len(content_checks),
        "payload": payload,
        "validation_results": validation_results,
        "hackathon_ready": all_fields_valid and content_score >= len(content_checks) * 0.8
    }


def test_callback_url_format():
    """Test that callback URL is correctly formatted."""
    print(f"\n🌐 Testing Callback URL Configuration...")
    
    callback_service = CallbackService(api_key="test")
    expected_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    url_correct = callback_service.callback_url == expected_url
    
    print(f"   🎯 Expected URL: {expected_url}")
    print(f"   🔧 Configured URL: {callback_service.callback_url}")
    print(f"   ✅ URL Match: {'✅ CORRECT' if url_correct else '❌ INCORRECT'}")
    
    # Test timeout configuration
    timeout_correct = callback_service.timeout.total == 10
    print(f"   ⏱️  Timeout: {callback_service.timeout.total}s {'✅ CORRECT' if timeout_correct else '❌ INCORRECT'}")
    
    return {
        "url_correct": url_correct,
        "timeout_correct": timeout_correct,
        "configured_url": callback_service.callback_url
    }


if __name__ == "__main__":
    print("🚀 Starting Callback Payload Validation")
    print("=" * 60)
    
    # Test payload structure
    payload_result = test_callback_payload_structure()
    
    # Test URL configuration
    url_result = test_callback_url_format()
    
    print("\n" + "=" * 60)
    print("📊 FINAL CALLBACK VALIDATION REPORT")
    print("=" * 60)
    
    print(f"🔧 Payload Structure: {'✅ VALID' if payload_result['all_fields_valid'] else '❌ INVALID'}")
    print(f"📊 Content Quality: {payload_result['content_score']}/{payload_result['total_content_checks']} ({'✅ EXCELLENT' if payload_result['content_score'] >= payload_result['total_content_checks'] * 0.8 else '⚠️ NEEDS IMPROVEMENT'})")
    print(f"🌐 URL Configuration: {'✅ CORRECT' if url_result['url_correct'] else '❌ INCORRECT'}")
    print(f"⏱️  Timeout Settings: {'✅ CORRECT' if url_result['timeout_correct'] else '❌ INCORRECT'}")
    
    hackathon_ready = (
        payload_result['all_fields_valid'] and 
        payload_result['content_score'] >= payload_result['total_content_checks'] * 0.8 and
        url_result['url_correct'] and 
        url_result['timeout_correct']
    )
    
    print(f"\n🏆 HACKATHON READINESS: {'✅ READY FOR DEPLOYMENT' if hackathon_ready else '❌ NEEDS FIXES'}")
    
    if hackathon_ready:
        print(f"\n🎉 All callback validation tests passed!")
        print(f"   📡 Payload format is correct")
        print(f"   🎯 All required fields present")
        print(f"   📊 Intelligence extraction working")
        print(f"   🌐 Callback URL properly configured")
        print(f"   ⚡ System ready for hackathon evaluation!")
    else:
        print(f"\n⚠️  Some validation checks failed. Please review:")
        if not payload_result['all_fields_valid']:
            print(f"   - Fix missing or incorrect payload fields")
        if payload_result['content_score'] < payload_result['total_content_checks'] * 0.8:
            print(f"   - Improve intelligence extraction quality")
        if not url_result['url_correct']:
            print(f"   - Fix callback URL configuration")
        if not url_result['timeout_correct']:
            print(f"   - Fix timeout settings")
    
    # Save detailed report
    final_report = {
        "payload_validation": payload_result,
        "url_validation": url_result,
        "hackathon_ready": hackathon_ready,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("callback_validation_report.json", "w") as f:
        json.dump(final_report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: callback_validation_report.json")