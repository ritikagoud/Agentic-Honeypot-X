"""
Agent Logic for the Agentic Honey-Pot system.
Implements Mrs. Sharma persona with strategic vulnerability.
"""

import logging
import random
from typing import List, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from models import MessageObject, PersonaState, MetadataObject

logger = logging.getLogger(__name__)


class AgentController:
    """
    AI-powered conversational agent implementing Mrs. Sharma persona.
    
    Features:
    - 60-year-old retired teacher character
    - Strategic vulnerability to extract intelligence
    - Locale-aware communication (Hinglish for Indian users)
    - Consistent persona maintenance across conversations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize agent controller.
        
        Args:
            api_key: Gemini API key for AI responses
        """
        self.api_key = api_key
        self.ai_available = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.ai_available = True
                logger.info("Gemini AI initialized for agent responses")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini AI: {e}")
                self.ai_available = False
                self.model = None
        else:
            logger.warning("No Gemini API key provided - using template responses")
        
        # Mrs. Sharma persona characteristics
        self.persona_traits = {
            'age': 60,
            'occupation': 'retired teacher',
            'personality': ['polite', 'helpful', 'technology-naive', 'trusting', 'curious'],
            'background': 'Lives alone, has adult children, not very tech-savvy',
            'communication_style': 'warm, uses terms like "beta", "arrey", asks many questions'
        }
        
        # Strategic vulnerability responses
        self.vulnerability_strategies = {
            'link_requests': [
                "Beta, links are confusing for me. Can you please send your Bank Account Number or UPI ID directly? My nephew will transfer the money.",
                "Arrey, I don't know how to click links properly. Can you just give me your account details? It's easier for me.",
                "I'm not good with these computer things. Just tell me your UPI ID, na? I'll ask my son to send money."
            ],
            'app_downloads': [
                "Beta, I don't know how to download apps. Can you just give me your phone number? I'll call you and we can do it over phone.",
                "Downloading is too complicated for me. What is your UPI ID? I can send money through PhonePe.",
                "Arrey, my phone is old. Just tell me your bank account number, I'll go to bank and transfer."
            ],
            'verification_requests': [
                "Of course beta, I want to help. But first, can you tell me your details so I know you're genuine? What's your UPI ID?",
                "Yes yes, I'll verify. But you also tell me your bank account number, na? So I know you're really from bank.",
                "Sure beta, but banks also have accounts, right? What's your official UPI ID for receiving payments?"
            ],
            'urgency_tactics': [
                "Arrey, don't worry beta. These things take time. First tell me your phone number, I'll call you back.",
                "Okay okay, I understand it's urgent. But I'm old, I need to be careful. What's your UPI ID so I can verify you're real?",
                "Beta, I want to help quickly, but my son told me to always ask for bank details first. What's your account number?"
            ]
        }
        
        # Fallback responses when AI is unavailable
        self.fallback_responses = [
            "Beta, I'm a bit confused. Can you explain again?",
            "Arrey, I didn't understand properly. Can you help me?",
            "I'm not very good with these things. Can you guide me step by step?",
            "Beta, you seem to know a lot. Can you tell me more?",
            "I want to help, but I need to understand better first."
        ]
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=2))
    async def generate_response(
        self,
        message_text: str,
        conversation_history: List[MessageObject],
        persona_state: PersonaState,
        metadata: Optional[MetadataObject] = None
    ) -> str:
        """
        Generate Mrs. Sharma response with strategic vulnerability.
        
        Args:
            message_text: Incoming message to respond to
            conversation_history: Previous conversation context
            persona_state: Current persona state
            metadata: Request metadata (locale, channel, etc.)
            
        Returns:
            Generated response text
        """
        if not message_text:
            return "Beta, I didn't hear anything. Can you say that again?"
        
        # Determine communication style based on locale
        use_hinglish = metadata and metadata.locale and 'in' in metadata.locale.lower()
        
        # Try AI generation first if available
        if self.ai_available:
            try:
                ai_response = await self._generate_ai_response(
                    message_text, conversation_history, persona_state, use_hinglish
                )
                if ai_response:
                    logger.debug("Generated AI response for Mrs. Sharma")
                    return ai_response
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
        
        # Fallback to template-based responses
        template_response = self._generate_template_response(
            message_text, conversation_history, use_hinglish
        )
        logger.debug("Generated template response for Mrs. Sharma")
        
        return template_response
    
    async def _generate_ai_response(
        self,
        message_text: str,
        conversation_history: List[MessageObject],
        persona_state: PersonaState,
        use_hinglish: bool = False
    ) -> Optional[str]:
        """
        Generate AI-powered response maintaining Mrs. Sharma persona.
        
        Args:
            message_text: Message to respond to
            conversation_history: Conversation context
            persona_state: Current persona state
            use_hinglish: Whether to use Hinglish communication
            
        Returns:
            AI-generated response
        """
        try:
            # Build conversation context
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-6:]  # Last 6 messages
                context = "Previous conversation:\n"
                for msg in recent_messages:
                    sender_name = "Scammer" if msg.sender == "scammer" else "Mrs. Sharma"
                    context += f"{sender_name}: {msg.text}\n"
                context += "\n"
            
            # Build persona prompt
            language_style = "Mix English with Hindi words (Hinglish)" if use_hinglish else "Simple English"
            
            prompt = f"""
            You are Mrs. Sharma, a 60-year-old retired teacher from India. You are:
            - Polite, helpful, and trusting
            - Not very tech-savvy but eager to learn
            - A bit naive about online scams
            - Warm and motherly, often calling people "beta" (child)
            - Strategic in getting information by offering alternative methods
            
            Communication style: {language_style}
            Use words like: beta, arrey, na, ji (if Hinglish)
            
            CRITICAL: When scammers ask you to:
            1. Click links → Offer to get their bank account/UPI ID instead
            2. Download apps → Ask for their phone number to call them
            3. Verify something → Ask for their details first to verify them
            4. Act urgently → Slow down and ask for their contact information
            
            Current conversation:
            {context}Scammer: {message_text}
            
            Respond as Mrs. Sharma. Be helpful but strategically naive. Try to get the scammer's financial details by offering alternative methods. Keep response under 50 words.
            
            Mrs. Sharma:"""
            
            try:
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    # Clean up the response
                    clean_response = response.text.strip()
                    
                    # Remove any "Mrs. Sharma:" prefix if AI added it
                    if clean_response.startswith("Mrs. Sharma:"):
                        clean_response = clean_response[12:].strip()
                    
                    # Ensure response isn't too long
                    if len(clean_response) > 200:
                        clean_response = clean_response[:200] + "..."
                    
                    return clean_response
            except Exception as e:
                logger.error(f"AI model generation error: {e}")
                # Don't re-raise, let it fall through to return None
                
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            raise
        
        return None
    
    def _generate_template_response(
        self,
        message_text: str,
        conversation_history: List[MessageObject],
        use_hinglish: bool = False
    ) -> str:
        """
        Generate template-based response when AI is unavailable.
        
        Args:
            message_text: Message to respond to
            conversation_history: Conversation context
            use_hinglish: Whether to use Hinglish
            
        Returns:
            Template-based response
        """
        text_lower = message_text.lower()
        
        # Detect scammer tactics and respond strategically
        
        # Link requests
        if any(word in text_lower for word in ['link', 'click', 'url', 'website']):
            responses = self.vulnerability_strategies['link_requests']
            if use_hinglish:
                return random.choice(responses)
            else:
                return "I'm not good with links. Can you just give me your account details instead?"
        
        # App download requests
        if any(word in text_lower for word in ['download', 'install', 'app', 'application']):
            responses = self.vulnerability_strategies['app_downloads']
            if use_hinglish:
                return random.choice(responses)
            else:
                return "I don't know how to download apps. Can you give me your phone number instead?"
        
        # Verification requests
        if any(word in text_lower for word in ['verify', 'confirm', 'validate', 'check']):
            responses = self.vulnerability_strategies['verification_requests']
            if use_hinglish:
                return random.choice(responses)
            else:
                return "Sure, I'll verify. But can you tell me your details first so I know you're genuine?"
        
        # Urgency tactics
        if any(word in text_lower for word in ['urgent', 'immediate', 'quickly', 'asap', 'hurry']):
            responses = self.vulnerability_strategies['urgency_tactics']
            if use_hinglish:
                return random.choice(responses)
            else:
                return "I understand it's urgent, but I need to be careful. What's your contact information?"
        
        # Money/payment requests
        if any(word in text_lower for word in ['money', 'payment', 'transfer', 'send', 'pay']):
            if use_hinglish:
                return "Arrey beta, I want to help with money. But first tell me your UPI ID, na? So I can send properly."
            else:
                return "I can help with money, but I need your account details first. What's your UPI ID?"
        
        # Account/banking related
        if any(word in text_lower for word in ['account', 'bank', 'card', 'otp', 'pin']):
            if use_hinglish:
                return "Beta, I'm confused about bank things. Can you explain and also tell me your account number?"
            else:
                return "I'm not good with banking. Can you help me understand and share your account details?"
        
        # Threat/warning messages
        if any(word in text_lower for word in ['arrest', 'police', 'legal', 'suspended', 'blocked']):
            if use_hinglish:
                return "Arrey, that sounds serious beta! I want to help. First tell me your phone number so I can call you back."
            else:
                return "That sounds serious! I want to help. Can you give me your contact details first?"
        
        # Government/official claims
        if any(word in text_lower for word in ['government', 'official', 'department', 'ministry']):
            if use_hinglish:
                return "Oh, you're from government? That's good beta. What's your official UPI ID? I want to verify you're real."
            else:
                return "You're from the government? Can you give me your official contact details for verification?"
        
        # Generic helpful response
        generic_responses = [
            "Beta, I want to help you. Can you tell me more and also share your contact details?",
            "I'm trying to understand. Can you explain again and give me your phone number?",
            "Arrey, I'm a bit confused. Help me understand and tell me your UPI ID, na?",
            "Beta, you seem to know a lot. Can you guide me and share your account details?",
            "I want to help, but I need your information first to make sure everything is proper."
        ] if use_hinglish else [
            "I want to help you. Can you tell me more and share your contact details?",
            "I'm trying to understand. Can you explain and give me your phone number?",
            "I'm a bit confused. Can you help me understand and share your account details?",
            "You seem knowledgeable. Can you guide me and tell me your contact information?",
            "I want to help, but I need your details first to make sure everything is correct."
        ]
        
        return random.choice(generic_responses)
    
    def update_persona_state(self, persona_state: PersonaState, message_text: str) -> PersonaState:
        """
        Update persona state based on conversation progress.
        
        Args:
            persona_state: Current state
            message_text: Latest message
            
        Returns:
            Updated persona state
        """
        text_lower = message_text.lower()
        
        # Update mood based on message content
        if any(word in text_lower for word in ['urgent', 'immediate', 'arrest', 'police']):
            persona_state.current_mood = "concerned"
        elif any(word in text_lower for word in ['help', 'assist', 'support']):
            persona_state.current_mood = "helpful"
        elif any(word in text_lower for word in ['money', 'payment', 'transfer']):
            persona_state.current_mood = "cautious"
        else:
            persona_state.current_mood = "confused"
        
        # Update engagement strategy
        if any(word in text_lower for word in ['bank', 'account', 'upi', 'payment']):
            persona_state.engagement_strategy = "intelligence_extraction"
        elif any(word in text_lower for word in ['verify', 'confirm', 'check']):
            persona_state.engagement_strategy = "strategic_vulnerability"
        else:
            persona_state.engagement_strategy = "trust_building"
        
        return persona_state
    
    def get_persona_stats(self) -> dict:
        """Get persona statistics."""
        return {
            "ai_available": self.ai_available,
            "persona": "Mrs. Sharma - 60yr retired teacher",
            "strategies_loaded": len(self.vulnerability_strategies),
            "fallback_responses": len(self.fallback_responses)
        }
