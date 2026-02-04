"""
Session Manager for the Agentic Honey-Pot system.
Handles conversation tracking, state management, and session isolation.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Callable
from threading import Lock

from models import (
    SessionData, MessageObject, MetadataObject, IntelligenceData,
    BehavioralMetrics, PersonaState, ConversationPhase, EngagementStrategy
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions with isolation, state tracking, and completion detection.
    
    Provides:
    - SessionId-based conversation isolation
    - Conversation history storage and retrieval
    - Metadata storage for channel, language, locale information
    - Conversation state transitions and completion detection
    - Automatic intelligence reporting triggers
    """
    
    def __init__(self, session_timeout_minutes: int = 60, callback_service=None):
        """
        Initialize the session manager.
        
        Args:
            session_timeout_minutes: Minutes after which inactive sessions are considered stale
            callback_service: Optional callback service for intelligence reporting
        """
        self._sessions: Dict[str, SessionData] = {}
        self._session_lock = Lock()
        self._session_timeout = timedelta(minutes=session_timeout_minutes)
        self._callback_service = callback_service
        self._completion_callbacks: List[Callable[[SessionData], None]] = []
        
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")
    
    def get_or_create_session(
        self, 
        session_id: str, 
        metadata: Optional[MetadataObject] = None
    ) -> SessionData:
        """
        Get existing session or create new one with proper isolation.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional conversation metadata
            
        Returns:
            SessionData object for the session
        """
        with self._session_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                # Update last activity timestamp
                session.last_activity = datetime.now()
                
                # Update metadata if provided and different
                if metadata and session.metadata != metadata:
                    session.metadata = metadata
                    logger.info(f"Updated metadata for session {session_id}")
                
                logger.debug(f"Retrieved existing session: {session_id}")
                return session
            
            # Create new session
            session = SessionData(
                session_id=session_id,
                conversation_history=[],
                extracted_intelligence=IntelligenceData(),
                scam_confidence=0.0,
                persona_active=False,
                conversation_complete=False,
                behavioral_analysis=BehavioralMetrics(),
                persona_state=PersonaState(),
                start_time=datetime.now(),
                last_activity=datetime.now(),
                metadata=metadata
            )
            
            self._sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
            
            return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get existing session without creating new one.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if exists, None otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if session:
                session.last_activity = datetime.now()
                logger.debug(f"Retrieved session: {session_id}")
            return session
    
    def add_message(self, session_id: str, message: MessageObject) -> bool:
        """
        Add message to session conversation history.
        
        Args:
            session_id: Session identifier
            message: Message to add
            
        Returns:
            True if message added successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot add message to non-existent session: {session_id}")
                return False
            
            # Validate message object
            if not isinstance(message, MessageObject):
                # Convert dict to MessageObject if needed
                if isinstance(message, dict):
                    try:
                        message = MessageObject(**message)
                    except Exception as e:
                        logger.error(f"Invalid message format for session {session_id}: {e}")
                        return False
                else:
                    logger.error(f"Invalid message type for session {session_id}")
                    return False
            
            session.conversation_history.append(message)
            session.last_activity = datetime.now()
            
            logger.debug(f"Added message to session {session_id}: {message.sender}")
            return True
    
    def get_conversation_history(self, session_id: str) -> List[MessageObject]:
        """
        Get complete conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages in chronological order
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.warning(f"No conversation history for non-existent session: {session_id}")
                return []
            
            return session.conversation_history.copy()
    
    def update_scam_confidence(self, session_id: str, confidence: float) -> bool:
        """
        Update scam detection confidence for a session.
        
        Args:
            session_id: Session identifier
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            True if updated successfully, False otherwise
        """
        if not 0.0 <= confidence <= 1.0:
            logger.error(f"Invalid confidence score: {confidence}")
            return False
        
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot update confidence for non-existent session: {session_id}")
                return False
            
            session.scam_confidence = confidence
            session.last_activity = datetime.now()
            
            logger.debug(f"Updated scam confidence for session {session_id}: {confidence}")
            return True
    
    def activate_persona(self, session_id: str) -> bool:
        """
        Activate Mrs. Sharma persona for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if activated successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot activate persona for non-existent session: {session_id}")
                return False
            
            session.persona_active = True
            session.persona_state.conversation_phase = ConversationPhase.ENGAGEMENT.value
            session.persona_state.engagement_strategy = EngagementStrategy.TRUST_BUILDING.value
            session.last_activity = datetime.now()
            
            logger.info(f"Activated Mrs. Sharma persona for session: {session_id}")
            return True
    
    def deactivate_persona(self, session_id: str) -> bool:
        """
        Deactivate persona for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deactivated successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot deactivate persona for non-existent session: {session_id}")
                return False
            
            session.persona_active = False
            session.last_activity = datetime.now()
            
            logger.info(f"Deactivated persona for session: {session_id}")
            return True
    
    def update_persona_state(
        self, 
        session_id: str, 
        state_updates: Dict[str, Any]
    ) -> bool:
        """
        Update persona state for a session.
        
        Args:
            session_id: Session identifier
            state_updates: Dictionary of state fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot update persona state for non-existent session: {session_id}")
                return False
            
            # Update persona state fields
            for field, value in state_updates.items():
                if hasattr(session.persona_state, field):
                    setattr(session.persona_state, field, value)
                    logger.debug(f"Updated persona {field} for session {session_id}: {value}")
                else:
                    logger.warning(f"Unknown persona state field: {field}")
            
            session.last_activity = datetime.now()
            return True
    
    def add_intelligence(self, session_id: str, intelligence: IntelligenceData) -> bool:
        """
        Add extracted intelligence to a session.
        
        Args:
            session_id: Session identifier
            intelligence: Intelligence data to add
            
        Returns:
            True if added successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot add intelligence to non-existent session: {session_id}")
                return False
            
            # Merge intelligence data
            session.extracted_intelligence.bank_accounts.extend(intelligence.bank_accounts)
            session.extracted_intelligence.ifsc_codes.extend(intelligence.ifsc_codes)
            session.extracted_intelligence.upi_ids.extend(intelligence.upi_ids)
            session.extracted_intelligence.phone_numbers.extend(intelligence.phone_numbers)
            session.extracted_intelligence.phishing_links.extend(intelligence.phishing_links)
            session.extracted_intelligence.suspicious_keywords.extend(intelligence.suspicious_keywords)
            
            # Merge confidence scores
            session.extracted_intelligence.extraction_confidence.update(
                intelligence.extraction_confidence
            )
            
            # Remove duplicates
            session.extracted_intelligence.bank_accounts = list(set(
                session.extracted_intelligence.bank_accounts
            ))
            session.extracted_intelligence.ifsc_codes = list(set(
                session.extracted_intelligence.ifsc_codes
            ))
            session.extracted_intelligence.upi_ids = list(set(
                session.extracted_intelligence.upi_ids
            ))
            session.extracted_intelligence.phone_numbers = list(set(
                session.extracted_intelligence.phone_numbers
            ))
            session.extracted_intelligence.phishing_links = list(set(
                session.extracted_intelligence.phishing_links
            ))
            session.extracted_intelligence.suspicious_keywords = list(set(
                session.extracted_intelligence.suspicious_keywords
            ))
            
            session.last_activity = datetime.now()
            
            logger.debug(f"Added intelligence to session {session_id}")
            return True
    
    def update_behavioral_analysis(
        self, 
        session_id: str, 
        behavioral_update: BehavioralMetrics
    ) -> bool:
        """
        Update behavioral analysis for a session.
        
        Args:
            session_id: Session identifier
            behavioral_update: Behavioral metrics to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot update behavioral analysis for non-existent session: {session_id}")
                return False
            
            # Update behavioral metrics
            session.behavioral_analysis.aggression_level = max(
                session.behavioral_analysis.aggression_level,
                behavioral_update.aggression_level
            )
            session.behavioral_analysis.sophistication_score = max(
                session.behavioral_analysis.sophistication_score,
                behavioral_update.sophistication_score
            )
            
            # Merge lists
            session.behavioral_analysis.urgency_tactics.extend(behavioral_update.urgency_tactics)
            session.behavioral_analysis.social_engineering_techniques.extend(
                behavioral_update.social_engineering_techniques
            )
            session.behavioral_analysis.persistence_indicators.extend(
                behavioral_update.persistence_indicators
            )
            
            # Remove duplicates
            session.behavioral_analysis.urgency_tactics = list(set(
                session.behavioral_analysis.urgency_tactics
            ))
            session.behavioral_analysis.social_engineering_techniques = list(set(
                session.behavioral_analysis.social_engineering_techniques
            ))
            session.behavioral_analysis.persistence_indicators = list(set(
                session.behavioral_analysis.persistence_indicators
            ))
            
            # Update manipulation attempts count
            session.behavioral_analysis.emotional_manipulation_attempts += (
                behavioral_update.emotional_manipulation_attempts
            )
            
            session.last_activity = datetime.now()
            
            logger.debug(f"Updated behavioral analysis for session {session_id}")
            return True
    
    def should_complete_conversation(self, session_id: str) -> bool:
        """
        Determine if a conversation should be marked as complete.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if conversation should complete, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                return False
            
            # Don't complete if already complete
            if session.conversation_complete:
                return False
            
            # Complete if significant intelligence has been extracted
            intelligence = session.extracted_intelligence
            has_significant_intelligence = (
                len(intelligence.bank_accounts) > 0 or
                len(intelligence.upi_ids) > 0 or
                len(intelligence.phone_numbers) > 0 or
                len(intelligence.phishing_links) > 0
            )
            
            # Complete if conversation has been going for a while with intelligence
            message_count = len(session.conversation_history)
            has_enough_messages = message_count >= 10
            
            # Complete if scammer seems to be disengaging
            if message_count >= 5:
                recent_messages = session.conversation_history[-3:]
                scammer_messages = [msg for msg in recent_messages if msg.sender == "scammer"]
                if len(scammer_messages) == 0:
                    logger.info(f"Scammer disengagement detected for session {session_id}")
                    return True
            
            # Complete if we have significant intelligence and enough interaction
            if has_significant_intelligence and message_count >= 6:
                logger.info(f"Sufficient intelligence gathered for session {session_id}")
                return True
            
            # Complete if conversation is very long (potential endless loop)
            if message_count >= 20:
                logger.info(f"Maximum message limit reached for session {session_id}")
                return True
            
            # Complete if session has been inactive for extended period
            inactive_duration = datetime.now() - session.last_activity
            if inactive_duration > timedelta(minutes=30) and message_count >= 3:
                logger.info(f"Session inactive for {inactive_duration.total_seconds()/60:.1f} minutes: {session_id}")
                return True
            
            # Complete if scammer provided key intelligence and conversation is winding down
            if (intelligence.bank_accounts or intelligence.upi_ids) and message_count >= 4:
                # Check if last few messages indicate conversation ending
                if message_count >= 2:
                    last_messages = session.conversation_history[-2:]
                    last_texts = [msg.text.lower() for msg in last_messages]
                    ending_indicators = ['bye', 'goodbye', 'thank you', 'thanks', 'done', 'complete', 'finished']
                    if any(indicator in text for text in last_texts for indicator in ending_indicators):
                        logger.info(f"Conversation ending detected with intelligence for session {session_id}")
                        return True
            
            return False
    
    def complete_conversation(self, session_id: str) -> bool:
        """
        Mark a conversation as complete and trigger intelligence reporting.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if marked complete successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot complete non-existent session: {session_id}")
                return False
            
            # Don't complete if already complete
            if session.conversation_complete:
                logger.warning(f"Session already complete: {session_id}")
                return True
            
            session.conversation_complete = True
            session.persona_state.conversation_phase = ConversationPhase.CONCLUSION.value
            session.last_activity = datetime.now()
            
            logger.info(f"Marked conversation complete for session: {session_id}")
            
            # Trigger intelligence reporting
            self._trigger_intelligence_reporting(session)
            
            # Call completion callbacks
            for callback in self._completion_callbacks:
                try:
                    callback(session)
                except Exception as e:
                    logger.error(f"Completion callback failed for session {session_id}: {e}")
            
            return True
    
    def get_session_metadata(self, session_id: str) -> Optional[MetadataObject]:
        """
        Get metadata for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            MetadataObject if session exists, None otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            return session.metadata if session else None
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active (non-complete) session IDs.
        
        Returns:
            List of active session IDs
        """
        with self._session_lock:
            return [
                session_id for session_id, session in self._sessions.items()
                if not session.conversation_complete
            ]
    
    def cleanup_stale_sessions(self) -> int:
        """
        Remove sessions that have been inactive for too long.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.now()
        stale_sessions = []
        
        with self._session_lock:
            for session_id, session in self._sessions.items():
                if current_time - session.last_activity > self._session_timeout:
                    stale_sessions.append(session_id)
            
            for session_id in stale_sessions:
                del self._sessions[session_id]
                logger.info(f"Cleaned up stale session: {session_id}")
        
        return len(stale_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current sessions.
        
        Returns:
            Dictionary with session statistics
        """
        with self._session_lock:
            total_sessions = len(self._sessions)
            active_sessions = len([s for s in self._sessions.values() if not s.conversation_complete])
            completed_sessions = total_sessions - active_sessions
            persona_active_sessions = len([s for s in self._sessions.values() if s.persona_active])
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "persona_active_sessions": persona_active_sessions,
                "average_messages_per_session": (
                    sum(len(s.conversation_history) for s in self._sessions.values()) / total_sessions
                    if total_sessions > 0 else 0
                )
            }
    
    def set_callback_service(self, callback_service) -> None:
        """
        Set the callback service for intelligence reporting.
        
        Args:
            callback_service: Callback service instance
        """
        self._callback_service = callback_service
        logger.info("Callback service configured for intelligence reporting")
    
    def add_completion_callback(self, callback: Callable[[SessionData], None]) -> None:
        """
        Add a callback function to be called when conversations complete.
        
        Args:
            callback: Function to call with completed session data
        """
        self._completion_callbacks.append(callback)
        callback_name = getattr(callback, '__name__', str(callback))
        logger.info(f"Added completion callback: {callback_name}")
    
    def _trigger_intelligence_reporting(self, session: SessionData) -> None:
        """
        Trigger intelligence reporting for a completed session.
        
        Args:
            session: Completed session data
        """
        if not self._callback_service:
            logger.warning(f"No callback service configured for session {session.session_id}")
            return
        
        # Only report if scam was detected and we have some intelligence
        if session.scam_confidence <= 0.5:
            logger.info(f"Skipping report for non-scam session: {session.session_id}")
            return
        
        intelligence = session.extracted_intelligence
        has_intelligence = (
            intelligence.bank_accounts or
            intelligence.upi_ids or
            intelligence.phone_numbers or
            intelligence.phishing_links or
            intelligence.suspicious_keywords
        )
        
        if not has_intelligence:
            logger.info(f"Skipping report for session with no intelligence: {session.session_id}")
            return
        
        try:
            # Send intelligence report asynchronously
            logger.info(f"Triggering intelligence report for session: {session.session_id}")
            
            # Use thread pool to avoid blocking
            import threading
            def send_report():
                try:
                    success = self._callback_service.send_intelligence_report_sync(session)
                    if success:
                        logger.info(f"Intelligence report sent successfully for session: {session.session_id}")
                    else:
                        logger.error(f"Failed to send intelligence report for session: {session.session_id}")
                except Exception as e:
                    logger.error(f"Exception sending intelligence report for session {session.session_id}: {e}")
            
            thread = threading.Thread(target=send_report, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to trigger intelligence reporting for session {session.session_id}: {e}")
    
    def check_and_complete_conversations(self) -> List[str]:
        """
        Check all active sessions and complete those that should be completed.
        
        Returns:
            List of session IDs that were completed
        """
        completed_sessions = []
        
        # Get list of active sessions to check
        active_session_ids = []
        with self._session_lock:
            active_session_ids = [
                session_id for session_id, session in self._sessions.items()
                if not session.conversation_complete
            ]
        
        # Check each active session for completion
        for session_id in active_session_ids:
            if self.should_complete_conversation(session_id):
                if self.complete_conversation(session_id):
                    completed_sessions.append(session_id)
        
        if completed_sessions:
            logger.info(f"Auto-completed {len(completed_sessions)} conversations: {completed_sessions}")
        
        return completed_sessions
    
    def archive_completed_sessions(self, max_completed_sessions: int = 100) -> int:
        """
        Archive old completed sessions to prevent memory buildup.
        
        Args:
            max_completed_sessions: Maximum number of completed sessions to keep
            
        Returns:
            Number of sessions archived
        """
        archived_count = 0
        
        with self._session_lock:
            # Get completed sessions sorted by last activity (oldest first)
            completed_sessions = [
                (session_id, session) for session_id, session in self._sessions.items()
                if session.conversation_complete
            ]
            
            if len(completed_sessions) <= max_completed_sessions:
                return 0
            
            # Sort by last activity (oldest first)
            completed_sessions.sort(key=lambda x: x[1].last_activity)
            
            # Archive oldest sessions
            sessions_to_archive = completed_sessions[:-max_completed_sessions]
            
            for session_id, session in sessions_to_archive:
                # Log session summary before archiving
                intelligence = session.extracted_intelligence
                intel_summary = {
                    'bank_accounts': len(intelligence.bank_accounts),
                    'upi_ids': len(intelligence.upi_ids),
                    'phone_numbers': len(intelligence.phone_numbers),
                    'phishing_links': len(intelligence.phishing_links),
                    'messages': len(session.conversation_history),
                    'scam_confidence': session.scam_confidence
                }
                
                logger.info(f"Archiving session {session_id}: {intel_summary}")
                
                # Remove from active sessions
                del self._sessions[session_id]
                archived_count += 1
        
        if archived_count > 0:
            logger.info(f"Archived {archived_count} completed sessions")
        
        return archived_count
    
    def get_completed_sessions(self) -> List[SessionData]:
        """
        Get all completed sessions.
        
        Returns:
            List of completed session data
        """
        with self._session_lock:
            return [
                session for session in self._sessions.values()
                if session.conversation_complete
            ]
    
    def force_complete_session(self, session_id: str, reason: str = "Manual completion") -> bool:
        """
        Force complete a session regardless of automatic completion criteria.
        
        Args:
            session_id: Session identifier
            reason: Reason for forced completion
            
        Returns:
            True if completed successfully, False otherwise
        """
        with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.error(f"Cannot force complete non-existent session: {session_id}")
                return False
            
            if session.conversation_complete:
                logger.warning(f"Session already complete: {session_id}")
                return True
            
            logger.info(f"Force completing session {session_id}: {reason}")
            
            # Mark as complete and trigger reporting
            session.conversation_complete = True
            session.persona_state.conversation_phase = ConversationPhase.CONCLUSION.value
            session.last_activity = datetime.now()
            
            # Trigger intelligence reporting
            self._trigger_intelligence_reporting(session)
            
            # Call completion callbacks
            for callback in self._completion_callbacks:
                try:
                    callback(session)
                except Exception as e:
                    logger.error(f"Completion callback failed for session {session_id}: {e}")
            
            return True