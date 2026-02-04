"""
Intelligence Extractor for the Agentic Honey-Pot system.
Implements comprehensive pattern matching and behavioral analysis.
"""

import re
import logging
from typing import Optional, List, Dict, Set
from urllib.parse import urlparse

from models import IntelligenceData, BehavioralMetrics, MessageObject

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """
    Comprehensive intelligence extraction engine for scam detection.
    
    Provides:
    - Regex pattern matching for Indian bank accounts, IFSC codes, UPI IDs
    - Phone number extraction for 10-digit Indian mobile numbers
    - URL and phishing link detection
    - Suspicious keyword identification
    - Behavioral analysis and aggression scoring (1-10 scale)
    - Social engineering technique identification
    """
    
    def __init__(self):
        """Initialize the intelligence extractor with regex patterns."""
        # Financial data patterns
        self.bank_account_pattern = re.compile(r'\b\d{9,18}\b')
        self.ifsc_pattern = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', re.IGNORECASE)
        
        # Broad UPI pattern as specified
        self.upi_pattern = re.compile(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}')
        
        # Phone number pattern for 10-digit Indian mobile numbers
        self.phone_pattern = re.compile(r'\b[6-9]\d{9}\b')
        
        # URL patterns
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Suspicious keywords for different categories
        self.urgency_keywords = {
            'immediate', 'urgent', 'quickly', 'fast', 'hurry', 'asap', 'now', 'today',
            'expire', 'expires', 'deadline', 'limited time', 'act now', 'don\'t wait',
            'emergency', 'critical', 'important', 'final notice', 'last chance'
        }
        
        self.financial_keywords = {
            'bank account', 'account number', 'routing number', 'ifsc', 'upi', 'paytm',
            'gpay', 'phonepe', 'transfer money', 'send money', 'payment', 'deposit',
            'withdraw', 'atm', 'pin', 'otp', 'cvv', 'card number', 'debit card',
            'credit card', 'net banking', 'mobile banking'
        }
        
        self.verification_keywords = {
            'verify', 'confirm', 'validate', 'authenticate', 'check', 'update',
            'suspended', 'blocked', 'frozen', 'locked', 'compromised', 'security',
            'fraud', 'unauthorized', 'suspicious activity'
        }
        
        self.authority_keywords = {
            'bank', 'government', 'police', 'officer', 'official', 'department',
            'ministry', 'rbi', 'reserve bank', 'income tax', 'customs', 'cbi',
            'cyber crime', 'investigation', 'legal action', 'court', 'arrest'
        }
        
        # Social engineering techniques
        self.social_engineering_patterns = {
            'authority_impersonation': [
                'i am calling from', 'this is', 'speaking from', 'bank representative',
                'government official', 'police officer', 'tax department'
            ],
            'urgency_creation': [
                'immediate action required', 'account will be closed', 'legal action',
                'arrest warrant', 'penalty', 'fine', 'suspension'
            ],
            'fear_tactics': [
                'fraud detected', 'suspicious activity', 'unauthorized access',
                'security breach', 'account compromised', 'illegal activity'
            ],
            'trust_building': [
                'for your security', 'to protect you', 'verification process',
                'security update', 'safety measure', 'precautionary'
            ],
            'information_gathering': [
                'confirm your', 'verify your', 'provide your', 'share your',
                'tell me your', 'what is your', 'send me your'
            ]
        }
        
        logger.info("IntelligenceExtractor initialized with comprehensive patterns")
    
    def extract_from_message(self, message_text: str) -> Optional[IntelligenceData]:
        """
        Extract intelligence from a single message.
        
        Args:
            message_text: Text content to analyze
            
        Returns:
            IntelligenceData object with extracted information
        """
        if not message_text or not isinstance(message_text, str):
            return None
        
        text_lower = message_text.lower()
        
        # Extract financial data
        bank_accounts = self._extract_bank_accounts(message_text)
        ifsc_codes = self._extract_ifsc_codes(message_text)
        upi_ids = self._extract_upi_ids(message_text)
        phone_numbers = self._extract_phone_numbers(message_text)
        phishing_links = self._extract_urls(message_text)
        suspicious_keywords = self._extract_suspicious_keywords(text_lower)
        
        # Calculate extraction confidence
        confidence = self._calculate_extraction_confidence(
            bank_accounts, ifsc_codes, upi_ids, phone_numbers, phishing_links, suspicious_keywords
        )
        
        # Only return if we found something significant
        if any([bank_accounts, ifsc_codes, upi_ids, phone_numbers, phishing_links, suspicious_keywords]):
            intelligence = IntelligenceData(
                bank_accounts=bank_accounts,
                ifsc_codes=ifsc_codes,
                upi_ids=upi_ids,
                phone_numbers=phone_numbers,
                phishing_links=phishing_links,
                suspicious_keywords=suspicious_keywords,
                extraction_confidence=confidence
            )
            
            logger.info(f"Extracted intelligence: {len(bank_accounts)} accounts, {len(upi_ids)} UPIs, "
                       f"{len(phone_numbers)} phones, {len(phishing_links)} links, "
                       f"{len(suspicious_keywords)} keywords")
            
            return intelligence
        
        return None
    
    def analyze_behavior(self, message_text: str, conversation_history: List[MessageObject]) -> Optional[BehavioralMetrics]:
        """
        Analyze behavioral patterns and generate metrics.
        
        Args:
            message_text: Latest message text
            conversation_history: Full conversation history
            
        Returns:
            BehavioralMetrics object with analysis results
        """
        if not message_text:
            return None
        
        text_lower = message_text.lower()
        
        # Analyze aggression level (1-10 scale)
        aggression_level = self._calculate_aggression_level(message_text, conversation_history)
        
        # Analyze sophistication (1-10 scale)
        sophistication_score = self._calculate_sophistication_score(message_text, conversation_history)
        
        # Identify tactics and techniques
        urgency_tactics = self._identify_urgency_tactics(text_lower)
        social_engineering_techniques = self._identify_social_engineering(text_lower)
        persistence_indicators = self._identify_persistence_patterns(conversation_history)
        
        # Count emotional manipulation attempts
        manipulation_attempts = self._count_manipulation_attempts(text_lower)
        
        behavioral = BehavioralMetrics(
            aggression_level=aggression_level,
            sophistication_score=sophistication_score,
            urgency_tactics=urgency_tactics,
            social_engineering_techniques=social_engineering_techniques,
            persistence_indicators=persistence_indicators,
            emotional_manipulation_attempts=manipulation_attempts
        )
        
        logger.debug(f"Behavioral analysis: aggression={aggression_level}, "
                    f"sophistication={sophistication_score}, "
                    f"techniques={len(social_engineering_techniques)}")
        
        return behavioral
    
    def _extract_bank_accounts(self, text: str) -> List[str]:
        """Extract Indian bank account numbers."""
        matches = self.bank_account_pattern.findall(text)
        # Filter out common false positives (phone numbers, dates, etc.)
        valid_accounts = []
        for match in matches:
            # Bank accounts are typically 9-18 digits
            if 9 <= len(match) <= 18:
                # Avoid phone numbers (10 digits starting with 6-9)
                if not (len(match) == 10 and match[0] in '6789'):
                    valid_accounts.append(match)
        
        return list(set(valid_accounts))  # Remove duplicates
    
    def _extract_ifsc_codes(self, text: str) -> List[str]:
        """Extract IFSC codes."""
        matches = self.ifsc_pattern.findall(text)
        return list(set([match.upper() for match in matches]))
    
    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs using broad regex pattern."""
        matches = self.upi_pattern.findall(text)
        # Filter out email addresses that might match the pattern
        upi_ids = []
        for match in matches:
            # Common UPI domains
            domain = match.split('@')[1].lower()
            if domain in ['paytm', 'okicici', 'apl', 'ybl', 'ibl', 'axl', 'fbl', 'pnb', 'sbi', 'upi']:
                upi_ids.append(match)
            elif len(domain) <= 10:  # Short domains are likely UPI
                upi_ids.append(match)
        
        return list(set(upi_ids))
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract 10-digit Indian mobile phone numbers."""
        matches = self.phone_pattern.findall(text)
        return list(set(matches))
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs and identify potential phishing links."""
        matches = self.url_pattern.findall(text)
        phishing_links = []
        
        for url in matches:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Check for suspicious domains
                suspicious_indicators = [
                    'bit.ly', 'tinyurl', 'short', 'redirect', 'click',
                    'secure-bank', 'verify-account', 'update-info',
                    'banking-security', 'account-verify'
                ]
                
                if any(indicator in domain for indicator in suspicious_indicators):
                    phishing_links.append(url)
                elif len(domain.split('.')) > 3:  # Suspicious subdomain structure
                    phishing_links.append(url)
                else:
                    phishing_links.append(url)  # Include all URLs for analysis
                    
            except Exception:
                phishing_links.append(url)  # Include malformed URLs
        
        return list(set(phishing_links))
    
    def _extract_suspicious_keywords(self, text_lower: str) -> List[str]:
        """Extract suspicious keywords from different categories."""
        found_keywords = []
        
        # Check all keyword categories
        all_keywords = (
            self.urgency_keywords | self.financial_keywords | 
            self.verification_keywords | self.authority_keywords
        )
        
        for keyword in all_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_extraction_confidence(self, bank_accounts, ifsc_codes, upi_ids, 
                                       phone_numbers, phishing_links, keywords) -> Dict[str, float]:
        """Calculate confidence scores for extracted data."""
        confidence = {}
        
        # Bank accounts confidence
        if bank_accounts:
            confidence['bank_accounts'] = min(0.9, 0.6 + len(bank_accounts) * 0.1)
        
        # IFSC codes confidence
        if ifsc_codes:
            confidence['ifsc_codes'] = 0.95  # IFSC pattern is very specific
        
        # UPI IDs confidence
        if upi_ids:
            confidence['upi_ids'] = min(0.9, 0.7 + len(upi_ids) * 0.1)
        
        # Phone numbers confidence
        if phone_numbers:
            confidence['phone_numbers'] = min(0.85, 0.6 + len(phone_numbers) * 0.1)
        
        # URLs confidence
        if phishing_links:
            confidence['phishing_links'] = 0.8
        
        # Keywords confidence
        if keywords:
            confidence['suspicious_keywords'] = min(0.7, 0.4 + len(keywords) * 0.05)
        
        return confidence
    
    def _calculate_aggression_level(self, message_text: str, conversation_history: List[MessageObject]) -> int:
        """Calculate aggression level on 1-10 scale."""
        text_lower = message_text.lower()
        aggression_score = 1
        
        # Check for aggressive language patterns
        aggressive_indicators = [
            'must', 'have to', 'need to', 'required', 'mandatory', 'immediately',
            'now', 'urgent', 'critical', 'important', 'serious', 'warning',
            'penalty', 'fine', 'arrest', 'legal action', 'court', 'police'
        ]
        
        # Threatening language
        threats = [
            'arrest', 'jail', 'prison', 'legal action', 'court case', 'penalty',
            'fine', 'punishment', 'consequences', 'trouble', 'problem'
        ]
        
        # Demanding language
        demands = [
            'send immediately', 'transfer now', 'provide details', 'give me',
            'tell me', 'share your', 'confirm your'
        ]
        
        # Score based on indicators
        for indicator in aggressive_indicators:
            if indicator in text_lower:
                aggression_score += 1
        
        for threat in threats:
            if threat in text_lower:
                aggression_score += 2
        
        for demand in demands:
            if demand in text_lower:
                aggression_score += 1
        
        # Check for ALL CAPS (aggressive tone)
        caps_ratio = sum(1 for c in message_text if c.isupper()) / max(len(message_text), 1)
        if caps_ratio > 0.3:
            aggression_score += 2
        
        # Check for multiple exclamation marks
        if message_text.count('!') >= 2:
            aggression_score += 1
        
        # Persistence across conversation
        if len(conversation_history) > 5:
            scammer_messages = [msg for msg in conversation_history if msg.sender == "scammer"]
            if len(scammer_messages) > 3:
                aggression_score += 1
        
        return min(10, aggression_score)
    
    def _calculate_sophistication_score(self, message_text: str, conversation_history: List[MessageObject]) -> int:
        """Calculate sophistication level on 1-10 scale."""
        text_lower = message_text.lower()
        sophistication_score = 1
        
        # Technical terminology
        technical_terms = [
            'verification', 'authentication', 'security protocol', 'encryption',
            'digital signature', 'otp', 'two-factor', 'biometric', 'kyc'
        ]
        
        # Professional language
        professional_terms = [
            'procedure', 'protocol', 'compliance', 'regulation', 'policy',
            'guidelines', 'standard', 'process', 'documentation'
        ]
        
        # Authority impersonation sophistication
        authority_terms = [
            'reserve bank of india', 'rbi', 'income tax department', 'cbdt',
            'enforcement directorate', 'cyber crime cell', 'investigation'
        ]
        
        # Score based on sophistication indicators
        for term in technical_terms:
            if term in text_lower:
                sophistication_score += 2
        
        for term in professional_terms:
            if term in text_lower:
                sophistication_score += 1
        
        for term in authority_terms:
            if term in text_lower:
                sophistication_score += 2
        
        # Grammar and spelling quality (basic check)
        words = message_text.split()
        if len(words) > 10:
            # Longer, well-structured messages indicate higher sophistication
            sophistication_score += 1
        
        # Use of specific details (account numbers, reference numbers, etc.)
        if re.search(r'\b[A-Z0-9]{6,}\b', message_text):  # Reference numbers
            sophistication_score += 1
        
        # Conversation flow sophistication
        if len(conversation_history) > 3:
            sophistication_score += 1
        
        return min(10, sophistication_score)
    
    def _identify_urgency_tactics(self, text_lower: str) -> List[str]:
        """Identify urgency tactics used."""
        tactics = []
        
        urgency_patterns = {
            'time_pressure': ['immediately', 'now', 'urgent', 'asap', 'quickly'],
            'deadline_threat': ['expire', 'deadline', 'limited time', 'last chance'],
            'consequence_threat': ['penalty', 'fine', 'arrest', 'legal action'],
            'account_threat': ['suspended', 'blocked', 'closed', 'frozen']
        }
        
        for tactic, keywords in urgency_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                tactics.append(tactic)
        
        return tactics
    
    def _identify_social_engineering(self, text_lower: str) -> List[str]:
        """Identify social engineering techniques."""
        techniques = []
        
        for technique, patterns in self.social_engineering_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                techniques.append(technique)
        
        return techniques
    
    def _identify_persistence_patterns(self, conversation_history: List[MessageObject]) -> List[str]:
        """Identify persistence patterns in conversation."""
        patterns = []
        
        if len(conversation_history) < 3:
            return patterns
        
        scammer_messages = [msg for msg in conversation_history if msg.sender == "scammer"]
        
        if len(scammer_messages) > 5:
            patterns.append('high_message_frequency')
        
        # Check for repeated requests
        scammer_texts = [msg.text.lower() for msg in scammer_messages]
        repeated_requests = 0
        for i in range(1, len(scammer_texts)):
            if any(keyword in scammer_texts[i] and keyword in scammer_texts[i-1] 
                   for keyword in ['send', 'provide', 'confirm', 'verify']):
                repeated_requests += 1
        
        if repeated_requests > 2:
            patterns.append('repeated_information_requests')
        
        # Check for escalation
        if len(scammer_messages) > 3:
            recent_messages = scammer_texts[-3:]
            threat_keywords = ['arrest', 'legal', 'police', 'court', 'penalty']
            if any(keyword in ' '.join(recent_messages) for keyword in threat_keywords):
                patterns.append('escalating_threats')
        
        return patterns
    
    def _count_manipulation_attempts(self, text_lower: str) -> int:
        """Count emotional manipulation attempts."""
        manipulation_patterns = [
            'for your safety', 'to protect you', 'help you', 'save you',
            'trust me', 'believe me', 'i understand', 'don\'t worry',
            'fear', 'scared', 'worried', 'concerned', 'urgent'
        ]
        
        count = 0
        for pattern in manipulation_patterns:
            if pattern in text_lower:
                count += 1
        
        return count