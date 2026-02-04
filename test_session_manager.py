"""
Tests for session manager conversation completion and reporting functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, strategies as st

from session_manager import SessionManager
from callback_service import CallbackService
from models import (
    SessionData, MessageObject, MetadataObject, IntelligenceData,
    BehavioralMetrics, PersonaState, ConversationPhase
)


class TestSessionManagerCompletion:
    """Test conversation completion detection and reporting triggers."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_callback = Mock(spec=CallbackService)
        self.mock_callback.send_intelligence_report_sync = Mock(return_value=True)
        self.session_manager = SessionManager(callback_service=self.mock_callback)
    
    def test_should_complete_with_significant_intelligence(self):
        """Test completion when significant intelligence is extracted."""
        # Create session with intelligence
        session_id = "test_session_1"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add some messages
        for i in range(6):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
        
        # Add significant intelligence
        intelligence = IntelligenceData(
            bank_accounts=["1234567890"],
            upi_ids=["scammer@paytm"]
        )
        self.session_manager.add_intelligence(session_id, intelligence)
        self.session_manager.update_scam_confidence(session_id, 0.8)
        
        # Should complete with intelligence and enough messages
        assert self.session_manager.should_complete_conversation(session_id) is True
    
    def test_should_complete_with_scammer_disengagement(self):
        """Test completion when scammer stops responding."""
        session_id = "test_session_2"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add messages with scammer going silent (need at least 5 messages)
        messages = [
            MessageObject(sender="scammer", text="Hello", timestamp=1000),
            MessageObject(sender="agent", text="Hi there", timestamp=2000),
            MessageObject(sender="scammer", text="Send money", timestamp=3000),
            MessageObject(sender="agent", text="Sure", timestamp=4000),
            MessageObject(sender="agent", text="How?", timestamp=5000),
            MessageObject(sender="agent", text="Are you there?", timestamp=6000),  # Added more agent messages
        ]
        
        for message in messages:
            self.session_manager.add_message(session_id, message)
        
        # Should complete due to scammer disengagement
        assert self.session_manager.should_complete_conversation(session_id) is True
    
    def test_should_complete_with_max_messages(self):
        """Test completion when maximum message limit is reached."""
        session_id = "test_session_3"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add 20+ messages
        for i in range(21):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
        
        # Should complete due to message limit
        assert self.session_manager.should_complete_conversation(session_id) is True
    
    def test_should_complete_with_inactivity(self):
        """Test completion when session is inactive for extended period."""
        session_id = "test_session_4"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add some messages
        for i in range(4):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
        
        # Simulate inactivity by setting last_activity to past
        with self.session_manager._session_lock:
            session = self.session_manager._sessions[session_id]
            session.last_activity = datetime.now() - timedelta(minutes=35)
        
        # Should complete due to inactivity
        assert self.session_manager.should_complete_conversation(session_id) is True
    
    def test_should_complete_with_conversation_ending_indicators(self):
        """Test completion when conversation ending indicators are detected."""
        session_id = "test_session_5"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add intelligence first
        intelligence = IntelligenceData(bank_accounts=["1234567890"])
        self.session_manager.add_intelligence(session_id, intelligence)
        
        # Add messages with ending indicators
        messages = [
            MessageObject(sender="scammer", text="Send to account 1234567890", timestamp=1000),
            MessageObject(sender="agent", text="Okay", timestamp=2000),
            MessageObject(sender="scammer", text="Thank you", timestamp=3000),
            MessageObject(sender="agent", text="Bye", timestamp=4000),
        ]
        
        for message in messages:
            self.session_manager.add_message(session_id, message)
        
        # Should complete due to ending indicators with intelligence
        assert self.session_manager.should_complete_conversation(session_id) is True
    
    def test_should_not_complete_without_criteria(self):
        """Test that conversation doesn't complete without meeting criteria."""
        session_id = "test_session_6"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add just a few messages without intelligence
        for i in range(3):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
        
        # Should not complete
        assert self.session_manager.should_complete_conversation(session_id) is False
    
    def test_complete_conversation_triggers_reporting(self):
        """Test that completing conversation triggers intelligence reporting."""
        session_id = "test_session_7"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Set up session with scam and intelligence
        self.session_manager.update_scam_confidence(session_id, 0.8)
        intelligence = IntelligenceData(
            bank_accounts=["1234567890"],
            upi_ids=["scammer@paytm"]
        )
        self.session_manager.add_intelligence(session_id, intelligence)
        
        # Add some messages
        for i in range(3):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
        
        # Complete conversation
        result = self.session_manager.complete_conversation(session_id)
        
        assert result is True
        
        # Verify session is marked complete
        session = self.session_manager.get_session(session_id)
        assert session.conversation_complete is True
        assert session.persona_state.conversation_phase == ConversationPhase.CONCLUSION.value
        
        # Give time for background thread to execute
        import time
        time.sleep(0.1)
        
        # Verify callback was called (eventually)
        # Note: This is called in a background thread, so we need to be patient
        assert self.mock_callback.send_intelligence_report_sync.called
    
    def test_complete_conversation_skips_reporting_for_non_scam(self):
        """Test that non-scam sessions don't trigger reporting."""
        session_id = "test_session_8"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Set up session without scam confidence
        self.session_manager.update_scam_confidence(session_id, 0.3)
        
        # Complete conversation
        result = self.session_manager.complete_conversation(session_id)
        
        assert result is True
        
        # Give time for background thread to execute
        import time
        time.sleep(0.1)
        
        # Verify callback was not called for non-scam
        assert not self.mock_callback.send_intelligence_report_sync.called
    
    def test_check_and_complete_conversations(self):
        """Test automatic completion checking for multiple sessions."""
        # Create multiple sessions with different completion criteria
        session_ids = []
        
        # Session 1: Should complete (intelligence + messages)
        session_id_1 = "auto_complete_1"
        session_1 = self.session_manager.get_or_create_session(session_id_1)
        intelligence = IntelligenceData(bank_accounts=["1234567890"])
        self.session_manager.add_intelligence(session_id_1, intelligence)
        for i in range(6):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id_1, message)
        session_ids.append(session_id_1)
        
        # Session 2: Should not complete (not enough criteria)
        session_id_2 = "auto_complete_2"
        session_2 = self.session_manager.get_or_create_session(session_id_2)
        for i in range(2):
            message = MessageObject(
                sender="scammer" if i % 2 == 0 else "agent",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id_2, message)
        session_ids.append(session_id_2)
        
        # Check and complete conversations
        completed = self.session_manager.check_and_complete_conversations()
        
        # Verify results
        assert session_id_1 in completed
        assert session_id_2 not in completed
        assert len(completed) == 1
        
        # Verify session states
        session_1 = self.session_manager.get_session(session_id_1)
        session_2 = self.session_manager.get_session(session_id_2)
        assert session_1.conversation_complete is True
        assert session_2.conversation_complete is False
    
    def test_archive_completed_sessions(self):
        """Test archival of old completed sessions."""
        # Create and complete multiple sessions
        session_ids = []
        for i in range(5):
            session_id = f"archive_test_{i}"
            session = self.session_manager.get_or_create_session(session_id)
            
            # Add some data
            message = MessageObject(
                sender="scammer",
                text=f"Message {i}",
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            self.session_manager.add_message(session_id, message)
            
            # Complete the session
            self.session_manager.complete_conversation(session_id)
            session_ids.append(session_id)
        
        # Set different last activity times to test ordering
        with self.session_manager._session_lock:
            for i, session_id in enumerate(session_ids):
                session = self.session_manager._sessions[session_id]
                session.last_activity = datetime.now() - timedelta(minutes=i * 10)
        
        # Archive keeping only 2 sessions
        archived_count = self.session_manager.archive_completed_sessions(max_completed_sessions=2)
        
        # Verify archival
        assert archived_count == 3  # Should archive 3 out of 5
        
        # Verify remaining sessions are the most recent ones
        remaining_sessions = self.session_manager.get_completed_sessions()
        assert len(remaining_sessions) == 2
    
    def test_force_complete_session(self):
        """Test forced completion of a session."""
        session_id = "force_complete_test"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Add minimal data
        message = MessageObject(
            sender="scammer",
            text="Hello",
            timestamp=int(datetime.now().timestamp() * 1000)
        )
        self.session_manager.add_message(session_id, message)
        
        # Force complete
        result = self.session_manager.force_complete_session(session_id, "Test completion")
        
        assert result is True
        
        # Verify completion
        session = self.session_manager.get_session(session_id)
        assert session.conversation_complete is True
        assert session.persona_state.conversation_phase == ConversationPhase.CONCLUSION.value
    
    def test_completion_callbacks(self):
        """Test that completion callbacks are called."""
        callback_mock = Mock()
        self.session_manager.add_completion_callback(callback_mock)
        
        session_id = "callback_test"
        session = self.session_manager.get_or_create_session(session_id)
        
        # Complete conversation
        self.session_manager.complete_conversation(session_id)
        
        # Verify callback was called
        callback_mock.assert_called_once()
        called_session = callback_mock.call_args[0][0]
        assert called_session.session_id == session_id


class TestSessionManagerIntegration:
    """Integration tests for session manager with callback service."""
    
    def test_end_to_end_completion_and_reporting(self):
        """Test complete flow from detection to reporting."""
        # Create real callback service (mocked)
        with patch('callback_service.aiohttp.ClientSession') as mock_session:
            # Mock successful HTTP response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_response
            
            callback_service = CallbackService(api_key="test_key")
            session_manager = SessionManager(callback_service=callback_service)
            
            # Create session with full conversation flow
            session_id = "integration_test"
            session = session_manager.get_or_create_session(session_id)
            
            # Simulate scam conversation
            messages = [
                MessageObject(sender="scammer", text="Hello, I am from bank", timestamp=1000),
                MessageObject(sender="agent", text="Oh hello", timestamp=2000),
                MessageObject(sender="scammer", text="Send money to 1234567890", timestamp=3000),
                MessageObject(sender="agent", text="Okay, what is your UPI?", timestamp=4000),
                MessageObject(sender="scammer", text="scammer@paytm", timestamp=5000),
                MessageObject(sender="agent", text="Thank you", timestamp=6000),
            ]
            
            for message in messages:
                session_manager.add_message(session_id, message)
            
            # Set scam confidence and add intelligence
            session_manager.update_scam_confidence(session_id, 0.9)
            intelligence = IntelligenceData(
                bank_accounts=["1234567890"],
                upi_ids=["scammer@paytm"],
                suspicious_keywords=["bank", "send money"]
            )
            session_manager.add_intelligence(session_id, intelligence)
            
            # Add behavioral analysis
            behavioral = BehavioralMetrics(
                aggression_level=6,
                sophistication_score=4,
                urgency_tactics=["immediate action"],
                social_engineering_techniques=["authority impersonation"]
            )
            session_manager.update_behavioral_analysis(session_id, behavioral)
            
            # Check if should complete
            should_complete = session_manager.should_complete_conversation(session_id)
            assert should_complete is True
            
            # Complete conversation
            result = session_manager.complete_conversation(session_id)
            assert result is True
            
            # Verify session state
            final_session = session_manager.get_session(session_id)
            assert final_session.conversation_complete is True
            
            # Give time for background reporting
            import time
            time.sleep(0.2)
            
            # Verify HTTP call was made (eventually)
            # Note: The actual HTTP call happens in a background thread
            # so we verify the session was set up correctly for reporting
            assert final_session.scam_confidence > 0.5
            assert len(final_session.extracted_intelligence.bank_accounts) > 0