"""
Scam Detector for the Agentic Honey-Pot system.
Implements AI-powered scam detection with fallback mechanisms.
"""

import logging
import re
from typing import List, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from models import MessageObject

logger = logging.getLogger(__name__)


class ScamResult:
    """Result of scam detection analysis."""
    
    def __init__(self, is_scam: bool, confidence: float, reasoning: str = ""):
        self.is_scam = is_scam
        self.confidence = confidence
        self.reasoning = reasoning


class ScamDetector:
    """
    AI-powered scam detection engine with fallback mechanisms.
    
    Uses Gemini AI for natural language analysis with rule-based fallback
    when AI service is unavailable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize scam detector.
        
        Args:
            api_key: Gemini API key for AI analysis
        """
        self.api_key = api_key
        self.ai_available = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.ai_available = True
                logger.info("Gemini AI initialized for scam detection")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini AI: {e}")
                self.ai_available = False
                self.model = None
        else:
            logger.warning("No Gemini API key provided - using rule-based detection only")
        
        # Rule-based patterns for fallback
        self.scam_patterns = {
            'urgency': [
                'immediate', 'urgent', 'asap', 'quickly', 'hurry', 'fast',
                'expire', 'deadline', 'limited time', 'act now'
            ],
            'financial': [
                'bank account', 'send money', 'transfer', 'payment', 'deposit',
                'otp', 'pin', 'cvv', 'card number', 'ifsc', 'upi'
            ],
            'authority': [
                'government', 'police', 'bank', 'officer', 'official',
                'rbi', 'income tax', 'customs', 'investigation'
            ],
            'threats': [
                'arrest', 'legal action', 'court', 'penalty', 'fine',
                'suspended', 'blocked', 'frozen', 'trouble'
            ],
            'verification': [
                'verify', 'confirm', 'validate', 'authenticate', 'update',
                'security', 'fraud', 'suspicious activity'
            ]
        }
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=2))
    async def analyze_message(
        self, 
        message_text: str, 
        conversation_history: List[MessageObject], 
        current_confidence: float = 0.0
    ) -> ScamResult:
        """
        Analyze message for scam indicators using AI and rule-based detection.
        
        Args:
            message_text: Text to analyze
            conversation_history: Previous conversation context
            current_confidence: Current scam confidence level
            
        Returns:
            ScamResult with detection outcome
        """
        if not message_text:
            return ScamResult(False, 0.0, "Empty message")
        
        # Try AI analysis first if available
        if self.ai_available:
            try:
                ai_result = await self._ai_analysis(message_text, conversation_history)
                if ai_result:
                    logger.debug(f"AI scam detection: {ai_result.is_scam} (confidence: {ai_result.confidence})")
                    return ai_result
            except Exception as e:
                logger.warning(f"AI analysis failed, falling back to rules: {e}")
        
        # Fallback to rule-based detection
        rule_result = self._rule_based_analysis(message_text, conversation_history, current_confidence)
        logger.debug(f"Rule-based scam detection: {rule_result.is_scam} (confidence: {rule_result.confidence})")
        
        return rule_result
    
    async def _ai_analysis(self, message_text: str, conversation_history: List[MessageObject]) -> Optional[ScamResult]:
        """
        Perform AI-based scam analysis using Gemini.
        
        Args:
            message_text: Text to analyze
            conversation_history: Conversation context
            
        Returns:
            ScamResult from AI analysis
        """
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages for context
                context = "Previous conversation:\n"
                for msg in recent_messages:
                    context += f"{msg.sender}: {msg.text}\n"
                context += "\n"
            
            prompt = f"""
            {context}Current message: "{message_text}"
            
            Analyze this message for scam indicators. Consider:
            1. Urgency tactics (immediate action required, deadlines)
            2. Authority impersonation (claiming to be from bank, government, police)
            3. Financial requests (asking for money, account details, OTP, PIN)
            4. Threat language (arrest, legal action, account suspension)
            5. Verification requests (confirm details, update information)
            6. Social engineering techniques
            
            Respond with:
            SCAM: YES/NO
            CONFIDENCE: 0.0-1.0
            REASONING: Brief explanation
            
            Be especially alert for Indian scam patterns involving:
            - Bank account verification scams
            - Government official impersonation
            - UPI/payment app fraud
            - Income tax/customs scams
            - Police/arrest threat scams
            """
            
            try:
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    return self._parse_ai_response(response.text)
            except Exception as e:
                logger.error(f"AI model generation error: {e}")
                # Don't re-raise, let it fall through to return None
                
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            raise
        
        return None
    
    def _parse_ai_response(self, response_text: str) -> ScamResult:
        """Parse AI response into ScamResult."""
        try:
            lines = response_text.strip().split('\n')
            
            is_scam = False
            confidence = 0.0
            reasoning = "AI analysis"
            
            for line in lines:
                line = line.strip().upper()
                if line.startswith('SCAM:'):
                    is_scam = 'YES' in line
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(re.search(r'[\d.]+', line).group())
                    except:
                        confidence = 0.5 if is_scam else 0.1
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
            
            return ScamResult(is_scam, confidence, reasoning)
            
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            # Return conservative result
            return ScamResult(True, 0.5, "AI parsing failed - conservative detection")
    
    def _rule_based_analysis(
        self, 
        message_text: str, 
        conversation_history: List[MessageObject], 
        current_confidence: float
    ) -> ScamResult:
        """
        Rule-based scam detection as fallback.
        
        Args:
            message_text: Text to analyze
            conversation_history: Conversation context
            current_confidence: Current confidence level
            
        Returns:
            ScamResult from rule-based analysis
        """
        text_lower = message_text.lower()
        score = 0
        matched_patterns = []
        
        # Check each pattern category
        for category, patterns in self.scam_patterns.items():
            category_matches = 0
            for pattern in patterns:
                if pattern in text_lower:
                    category_matches += 1
                    matched_patterns.append(f"{category}:{pattern}")
            
            # Weight different categories
            if category == 'financial' and category_matches > 0:
                score += category_matches * 3  # Financial requests are high priority
            elif category == 'threats' and category_matches > 0:
                score += category_matches * 2  # Threats are serious indicators
            elif category_matches > 0:
                score += category_matches
        
        # Additional scoring factors
        
        # Multiple exclamation marks or ALL CAPS (urgency indicators)
        if message_text.count('!') >= 2:
            score += 1
            matched_patterns.append("urgency:multiple_exclamations")
        
        caps_ratio = sum(1 for c in message_text if c.isupper()) / max(len(message_text), 1)
        if caps_ratio > 0.3:
            score += 1
            matched_patterns.append("urgency:excessive_caps")
        
        # Phone numbers or account numbers in message
        if re.search(r'\b\d{10,}\b', message_text):
            score += 2
            matched_patterns.append("financial:numeric_data")
        
        # Conversation context - escalation pattern
        if conversation_history:
            scammer_messages = [msg for msg in conversation_history if msg.sender == "scammer"]
            if len(scammer_messages) > 2:
                # Check for escalation in recent messages
                recent_texts = [msg.text.lower() for msg in scammer_messages[-3:]]
                threat_escalation = sum(1 for text in recent_texts 
                                     for threat in self.scam_patterns['threats'] 
                                     if threat in text)
                if threat_escalation > 0:
                    score += threat_escalation
                    matched_patterns.append("pattern:threat_escalation")
        
        # Convert score to confidence (0.0 to 1.0)
        confidence = min(1.0, score / 10.0)  # Normalize to 0-1 range
        
        # Boost confidence if we already have some confidence from previous messages
        if current_confidence > 0.3:
            confidence = min(1.0, confidence + (current_confidence * 0.2))
        
        # Determine if it's a scam based on confidence threshold
        is_scam = confidence >= 0.4  # 40% confidence threshold
        
        reasoning = f"Rule-based analysis: score={score}, patterns={len(matched_patterns)}"
        if matched_patterns:
            reasoning += f", matched={matched_patterns[:3]}"  # Show first 3 matches
        
        return ScamResult(is_scam, confidence, reasoning)
    
    def get_detection_stats(self) -> dict:
        """Get detection statistics."""
        return {
            "ai_available": self.ai_available,
            "detection_method": "AI + Rules" if self.ai_available else "Rules only",
            "patterns_loaded": sum(len(patterns) for patterns in self.scam_patterns.values())
        }
