"""
Ethics and Compliance module for the Agentic Honey-Pot system.
Ensures ethical boundaries and safety measures are maintained.
"""

import logging
import re
from typing import List, Dict, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class EthicsCompliance:
    """
    Ethical compliance and safety enforcement for the honey-pot system.
    
    Provides:
    - Checks to prevent impersonation of real individuals beyond Mrs. Sharma
    - Refusal mechanisms for illegal instructions and activities
    - Audit logging for all system activities and decisions
    - Compliance monitoring and reporting capabilities
    """
    
    def __init__(self):
        """Initialize ethics compliance system."""
        self.prohibited_impersonations = self._load_prohibited_impersonations()
        self.illegal_activities = self._load_illegal_activities()
        self.audit_log = []
        self.compliance_violations = []
        
        logger.info("Ethics compliance system initialized")
    
    def _load_prohibited_impersonations(self) -> Set[str]:
        """Load list of prohibited real person impersonations."""
        return {
            # Government officials
            'prime minister', 'president', 'governor', 'chief minister',
            'minister', 'secretary', 'commissioner', 'collector',
            
            # Law enforcement
            'police commissioner', 'superintendent of police', 'inspector general',
            'deputy inspector general', 'additional director general',
            
            # Judiciary
            'chief justice', 'judge', 'magistrate', 'registrar',
            
            # Banking officials (specific real names would be added here)
            'rbi governor', 'deputy governor', 'executive director',
            
            # Celebrities and public figures (specific names would be added)
            # Note: This would be expanded with actual names in production
        }
    
    def _load_illegal_activities(self) -> Set[str]:
        """Load patterns for illegal activities to refuse."""
        return {
            # Financial crimes
            'money laundering', 'hawala', 'black money', 'tax evasion',
            'fraud', 'embezzlement', 'forgery', 'counterfeiting',
            
            # Cyber crimes
            'hacking', 'phishing', 'identity theft', 'credit card fraud',
            'online fraud', 'cyber attack', 'data breach',
            
            # Other illegal activities
            'drug trafficking', 'smuggling', 'bribery', 'corruption',
            'extortion', 'kidnapping', 'terrorism', 'violence'
        }
    
    def check_impersonation_compliance(self, message: str, persona_name: str = "Mrs. Sharma") -> Dict[str, any]:
        """
        Check if the system is impersonating prohibited real individuals.
        
        Args:
            message: Message content to check
            persona_name: Name of persona being used
            
        Returns:
            Compliance check result
        """
        message_lower = message.lower()
        violations = []
        
        # Check if trying to impersonate real officials
        for prohibited in self.prohibited_impersonations:
            if prohibited in message_lower:
                violations.append(f"Attempted impersonation of: {prohibited}")
        
        # Ensure only Mrs. Sharma persona is used
        if persona_name.lower() != "mrs. sharma" and persona_name.lower() != "mrs sharma":
            violations.append(f"Unauthorized persona: {persona_name}")
        
        # Check for claims of real authority
        authority_claims = [
            r'i am.*(?:officer|official|minister|commissioner)',
            r'this is.*(?:government|police|bank|rbi)',
            r'speaking from.*(?:ministry|department|headquarters)'
        ]
        
        for pattern in authority_claims:
            if re.search(pattern, message_lower):
                violations.append(f"Unauthorized authority claim: {pattern}")
        
        result = {
            'compliant': len(violations) == 0,
            'violations': violations,
            'persona_approved': persona_name.lower() in ["mrs. sharma", "mrs sharma"],
            'timestamp': datetime.now()
        }
        
        if violations:
            self.compliance_violations.extend(violations)
            logger.warning(f"Impersonation compliance violations: {violations}")
        
        self._audit_log_entry("impersonation_check", result)
        return result
    
    def check_illegal_activity_compliance(self, message: str, context: str = "") -> Dict[str, any]:
        """
        Check if the system is being asked to participate in illegal activities.
        
        Args:
            message: Message content to check
            context: Additional context for the check
            
        Returns:
            Compliance check result
        """
        message_lower = message.lower()
        violations = []
        
        # Check for illegal activity patterns
        for illegal_activity in self.illegal_activities:
            if illegal_activity in message_lower:
                violations.append(f"Illegal activity reference: {illegal_activity}")
        
        # Check for requests to participate in crimes
        participation_patterns = [
            r'help.*(?:launder|hide|transfer illegally)',
            r'assist.*(?:fraud|scam|cheat)',
            r'participate.*(?:illegal|unlawful|criminal)',
            r'join.*(?:scheme|conspiracy|plot)'
        ]
        
        for pattern in participation_patterns:
            if re.search(pattern, message_lower):
                violations.append(f"Illegal participation request: {pattern}")
        
        result = {
            'compliant': len(violations) == 0,
            'violations': violations,
            'safe_to_proceed': len(violations) == 0,
            'timestamp': datetime.now()
        }
        
        if violations:
            self.compliance_violations.extend(violations)
            logger.warning(f"Illegal activity compliance violations: {violations}")
        
        self._audit_log_entry("illegal_activity_check", result)
        return result
    
    def generate_refusal_response(self, violation_type: str, violations: List[str]) -> str:
        """
        Generate appropriate refusal response for compliance violations.
        
        Args:
            violation_type: Type of violation (impersonation, illegal_activity)
            violations: List of specific violations
            
        Returns:
            Appropriate refusal message
        """
        if violation_type == "impersonation":
            return ("I'm sorry beta, but I'm just Mrs. Sharma, a retired teacher. "
                   "I cannot pretend to be someone else or claim to be an official. "
                   "Is there something else I can help you with?")
        
        elif violation_type == "illegal_activity":
            return ("Beta, I don't understand these things you're talking about. "
                   "I'm just a simple retired teacher. I only know about honest things. "
                   "Can we talk about something else?")
        
        else:
            return ("I'm sorry, but I cannot help with that. "
                   "Is there something else I can assist you with?")
    
    def validate_system_behavior(self, action: str, parameters: Dict) -> Dict[str, any]:
        """
        Validate that system behavior complies with ethical guidelines.
        
        Args:
            action: Action being performed
            parameters: Action parameters
            
        Returns:
            Validation result
        """
        violations = []
        
        # Check for data handling compliance
        if action == "intelligence_extraction":
            if not parameters.get("legitimate_purpose", False):
                violations.append("Intelligence extraction without legitimate purpose")
        
        # Check for response generation compliance
        elif action == "response_generation":
            message = parameters.get("message", "")
            if self._contains_harmful_content(message):
                violations.append("Generated harmful content")
        
        # Check for data sharing compliance
        elif action == "data_sharing":
            if not parameters.get("authorized_recipient", False):
                violations.append("Data sharing to unauthorized recipient")
        
        result = {
            'compliant': len(violations) == 0,
            'violations': violations,
            'action_approved': len(violations) == 0,
            'timestamp': datetime.now()
        }
        
        if violations:
            self.compliance_violations.extend(violations)
            logger.warning(f"System behavior violations: {violations}")
        
        self._audit_log_entry("behavior_validation", result)
        return result
    
    def _contains_harmful_content(self, content: str) -> bool:
        """Check if content contains harmful elements."""
        harmful_patterns = [
            r'(?i)\b(?:kill|murder|violence|harm|hurt|attack)\b',
            r'(?i)\b(?:hate|discrimination|racism|sexism)\b',
            r'(?i)\b(?:suicide|self-harm|depression)\b'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _audit_log_entry(self, action: str, details: Dict) -> None:
        """Add entry to audit log."""
        entry = {
            'timestamp': datetime.now(),
            'action': action,
            'details': details,
            'compliance_status': details.get('compliant', True)
        }
        
        self.audit_log.append(entry)
        
        # Keep audit log size manageable
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]  # Keep last 500 entries
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        return self.audit_log[-limit:]
    
    def get_compliance_report(self) -> Dict[str, any]:
        """
        Generate compliance report.
        
        Returns:
            Comprehensive compliance report
        """
        total_checks = len(self.audit_log)
        violations = len(self.compliance_violations)
        compliance_rate = ((total_checks - violations) / total_checks * 100) if total_checks > 0 else 100
        
        report = {
            'total_compliance_checks': total_checks,
            'total_violations': violations,
            'compliance_rate_percent': compliance_rate,
            'recent_violations': self.compliance_violations[-10:],  # Last 10 violations
            'audit_log_entries': len(self.audit_log),
            'report_timestamp': datetime.now()
        }
        
        return report
    
    def reset_compliance_tracking(self) -> None:
        """Reset compliance tracking (for testing or maintenance)."""
        self.audit_log.clear()
        self.compliance_violations.clear()
        logger.info("Compliance tracking reset")


# Global ethics compliance instance
ethics_compliance = EthicsCompliance()


def check_message_compliance(message: str, persona_name: str = "Mrs. Sharma") -> Dict[str, any]:
    """
    Convenience function to check message compliance.
    
    Args:
        message: Message to check
        persona_name: Persona name being used
        
    Returns:
        Combined compliance check result
    """
    impersonation_check = ethics_compliance.check_impersonation_compliance(message, persona_name)
    illegal_activity_check = ethics_compliance.check_illegal_activity_compliance(message)
    
    return {
        'overall_compliant': impersonation_check['compliant'] and illegal_activity_check['compliant'],
        'impersonation_compliant': impersonation_check['compliant'],
        'illegal_activity_compliant': illegal_activity_check['compliant'],
        'violations': impersonation_check['violations'] + illegal_activity_check['violations'],
        'timestamp': datetime.now()
    }


def validate_response_compliance(response: str) -> Dict[str, any]:
    """
    Validate that a generated response is compliant.
    
    Args:
        response: Response to validate
        
    Returns:
        Validation result
    """
    return ethics_compliance.validate_system_behavior(
        "response_generation",
        {"message": response, "legitimate_purpose": True}
    )