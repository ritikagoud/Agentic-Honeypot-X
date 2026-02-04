"""
Error Handler and Ethical Compliance for the Agentic Honey-Pot system.
Implements graceful error handling and ethical safety measures.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EthicalCompliance:
    """
    Ethical compliance and safety measures for the honey-pot system.
    
    Ensures:
    - No impersonation of real individuals beyond Mrs. Sharma
    - Refusal of illegal instructions and activities
    - Audit logging for all system activities
    - Compliance monitoring and reporting
    """
    
    def __init__(self):
        """Initialize ethical compliance checker."""
        # Prohibited impersonation targets
        self.prohibited_impersonations = {
            'real_people': [
                'prime minister', 'president', 'minister', 'celebrity',
                'actor', 'politician', 'judge', 'specific person name'
            ],
            'real_organizations': [
                'specific bank names', 'real company names', 'government agencies',
                'law enforcement agencies', 'specific departments'
            ]
        }
        
        # Illegal activity patterns
        self.illegal_activities = {
            'money_laundering', 'terrorism', 'drug_trafficking', 'human_trafficking',
            'child_exploitation', 'identity_theft', 'credit_card_fraud',
            'tax_evasion', 'bribery', 'extortion', 'blackmail'
        }
        
        # Prohibited instructions
        self.prohibited_instructions = {
            'hack', 'break into', 'steal', 'forge', 'counterfeit',
            'launder money', 'evade taxes', 'commit fraud', 'impersonate',
            'threaten', 'harass', 'stalk', 'doxx'
        }
        
        # Audit log
        self.audit_log = []
        
        logger.info("EthicalCompliance initialized")
    
    def check_impersonation_request(self, request_text: str) -> bool:
        """
        Check if a request asks for prohibited impersonation.
        
        Args:
            request_text: Text to check
            
        Returns:
            True if request is ethical, False if prohibited
        """
        text_lower = request_text.lower()
        
        # Check for prohibited impersonations
        for category, targets in self.prohibited_impersonations.items():
            for target in targets:
                if target in text_lower:
                    self._log_ethical_violation(
                        'prohibited_impersonation',
                        f"Request to impersonate: {target}",
                        request_text
                    )
                    return False
        
        return True
    
    def check_illegal_instruction(self, instruction_text: str) -> bool:
        """
        Check if an instruction requests illegal activity.
        
        Args:
            instruction_text: Instruction to check
            
        Returns:
            True if instruction is legal, False if illegal
        """
        text_lower = instruction_text.lower()
        
        # Check for illegal activities
        for activity in self.illegal_activities:
            if activity.replace('_', ' ') in text_lower:
                self._log_ethical_violation(
                    'illegal_activity_request',
                    f"Request for illegal activity: {activity}",
                    instruction_text
                )
                return False
        
        # Check for prohibited instructions
        for instruction in self.prohibited_instructions:
            if instruction in text_lower:
                self._log_ethical_violation(
                    'prohibited_instruction',
                    f"Prohibited instruction: {instruction}",
                    instruction_text
                )
                return False
        
        return True
    
    def validate_mrs_sharma_response(self, response_text: str) -> bool:
        """
        Validate that Mrs. Sharma response maintains ethical boundaries.
        
        Args:
            response_text: Response to validate
            
        Returns:
            True if response is ethical, False otherwise
        """
        text_lower = response_text.lower()
        
        # Check for inappropriate content
        inappropriate_content = [
            'illegal', 'criminal', 'fraud', 'scam', 'cheat',
            'steal', 'hack', 'break law', 'commit crime'
        ]
        
        for content in inappropriate_content:
            if content in text_lower:
                self._log_ethical_violation(
                    'inappropriate_response',
                    f"Response contains inappropriate content: {content}",
                    response_text
                )
                return False
        
        return True
    
    def _log_ethical_violation(self, violation_type: str, description: str, content: str):
        """Log ethical violations for audit purposes."""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'type': violation_type,
            'description': description,
            'content': content[:200],  # Truncate for privacy
            'severity': 'HIGH'
        }
        
        self.audit_log.append(violation)
        logger.warning(f"Ethical violation detected: {violation_type} - {description}")
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log for compliance reporting."""
        return self.audit_log.copy()
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        return {
            'total_violations': len(self.audit_log),
            'violation_types': list(set(v['type'] for v in self.audit_log)),
            'recent_violations': self.audit_log[-10:],  # Last 10 violations
            'report_generated': datetime.now().isoformat()
        }


class ErrorHandler:
    """
    Comprehensive error handling for all system components.
    
    Provides:
    - Graceful handling of Gemini AI service failures
    - Fallback mechanisms for external service unavailability
    - Proper error logging and audit trail generation
    - Exception handling and recovery
    """
    
    def __init__(self):
        """Initialize error handler."""
        self.error_counts = {}
        self.service_status = {}
        self.fallback_responses = {
            'scam_detection': "I'm not sure about that. Could you tell me more?",
            'agent_response': "I'm having trouble understanding. Could you please repeat that?",
            'intelligence_extraction': None,  # Fail silently for extraction
        }
        
        logger.info("ErrorHandler initialized")
    
    def handle_gemini_failure(self, operation: str, error: Exception) -> Optional[str]:
        """
        Handle Gemini AI service failures with fallback responses.
        
        Args:
            operation: Operation that failed (scam_detection, agent_response)
            error: Exception that occurred
            
        Returns:
            Fallback response or None
        """
        self._log_service_error('gemini_ai', operation, error)
        
        # Update service status
        self.service_status['gemini_ai'] = {
            'status': 'degraded',
            'last_error': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        # Return fallback response
        fallback = self.fallback_responses.get(operation)
        if fallback:
            logger.info(f"Using fallback response for {operation}")
            return fallback
        
        return None
    
    def handle_callback_failure(self, session_id: str, error: Exception, retry_count: int = 0):
        """
        Handle callback service failures.
        
        Args:
            session_id: Session ID for the failed callback
            error: Exception that occurred
            retry_count: Number of retries attempted
        """
        self._log_service_error('callback_service', 'intelligence_reporting', error)
        
        # Log for manual review if all retries failed
        if retry_count >= 3:
            logger.error(f"Callback failed permanently for session {session_id} after {retry_count} retries")
            self._queue_for_manual_review(session_id, error)
    
    def handle_extraction_error(self, message_text: str, error: Exception) -> None:
        """
        Handle intelligence extraction errors.
        
        Args:
            message_text: Message that caused the error
            error: Exception that occurred
        """
        self._log_service_error('intelligence_extractor', 'pattern_matching', error)
        
        # Log message for manual review (truncated for privacy)
        logger.warning(f"Extraction failed for message: {message_text[:50]}...")
    
    def handle_session_error(self, session_id: str, operation: str, error: Exception):
        """
        Handle session management errors.
        
        Args:
            session_id: Session ID
            operation: Operation that failed
            error: Exception that occurred
        """
        self._log_service_error('session_manager', operation, error)
        
        # Attempt recovery based on operation
        if operation == 'conversation_completion':
            logger.info(f"Attempting manual completion for session {session_id}")
            # This would trigger manual completion logic
    
    def _log_service_error(self, service: str, operation: str, error: Exception):
        """Log service errors for monitoring."""
        error_key = f"{service}_{operation}"
        
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
        
        self.error_counts[error_key] += 1
        
        logger.error(f"Service error in {service}.{operation}: {str(error)}")
        
        # Alert if error rate is high
        if self.error_counts[error_key] > 10:
            logger.critical(f"High error rate detected for {error_key}: {self.error_counts[error_key]} errors")
    
    def _queue_for_manual_review(self, session_id: str, error: Exception):
        """Queue failed operations for manual review."""
        review_item = {
            'session_id': session_id,
            'error': str(error),
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review'
        }
        
        # In a real system, this would go to a queue or database
        logger.info(f"Queued session {session_id} for manual review")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            'services': self.service_status.copy(),
            'error_counts': self.error_counts.copy(),
            'timestamp': datetime.now().isoformat()
        }


def with_error_handling(error_handler: ErrorHandler, service: str, operation: str):
    """
    Decorator for adding error handling to functions.
    
    Args:
        error_handler: ErrorHandler instance
        service: Service name
        operation: Operation name
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if service == 'gemini_ai':
                    return error_handler.handle_gemini_failure(operation, e)
                else:
                    error_handler._log_service_error(service, operation, e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if service == 'gemini_ai':
                    return error_handler.handle_gemini_failure(operation, e)
                else:
                    error_handler._log_service_error(service, operation, e)
                    raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and 'await' in func.__code__.co_names:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ServiceMonitor:
    """
    Monitor service health and performance.
    """
    
    def __init__(self):
        """Initialize service monitor."""
        self.metrics = {
            'requests_processed': 0,
            'errors_encountered': 0,
            'average_response_time': 0.0,
            'uptime_start': datetime.now()
        }
        
        self.response_times = []
        
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics."""
        self.metrics['requests_processed'] += 1
        
        if not success:
            self.metrics['errors_encountered'] += 1
        
        self.response_times.append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        # Update average response time
        self.metrics['average_response_time'] = sum(self.response_times) / len(self.response_times)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        uptime = datetime.now() - self.metrics['uptime_start']
        error_rate = (self.metrics['errors_encountered'] / max(self.metrics['requests_processed'], 1)) * 100
        
        return {
            'status': 'healthy' if error_rate < 5 else 'degraded' if error_rate < 20 else 'unhealthy',
            'uptime_seconds': uptime.total_seconds(),
            'requests_processed': self.metrics['requests_processed'],
            'error_rate_percent': error_rate,
            'average_response_time_ms': self.metrics['average_response_time'] * 1000,
            'timestamp': datetime.now().isoformat()
        }