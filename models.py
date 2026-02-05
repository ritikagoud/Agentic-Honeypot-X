"""
Bulletproof Pydantic V2 models for GUVI tester compatibility.
All fields are optional with proper aliases and validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class MessageObject(BaseModel):
    """Individual message in a conversation - all fields optional for flexibility."""
    model_config = ConfigDict(populate_by_name=True)
    
    sender: Optional[str] = Field(None, description="Message sender: 'scammer' or 'user'")
    text: Optional[str] = Field(None, description="Message content")
    timestamp: Optional[int] = Field(None, description="Epoch time in milliseconds")


class MetadataObject(BaseModel):
    """Conversation metadata - all fields optional with None defaults."""
    model_config = ConfigDict(populate_by_name=True)
    
    channel: Optional[str] = Field(None, description="Communication channel: SMS/WhatsApp/Email")
    language: Optional[str] = Field(None, description="Language used in conversation")
    locale: Optional[str] = Field(None, description="Country or region code")


class ChatRequest(BaseModel):
    """Main API request model with bulletproof GUVI compatibility."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    # Use aliases to accept both sessionId and session_id
    sessionId: str = Field(..., alias="sessionId", description="Unique session identifier")
    message: Union[str, MessageObject, Dict[str, Any], int, float] = Field(..., description="Message as string, object, dictionary, or number")
    conversationHistory: Optional[List[MessageObject]] = Field(
        default=[], 
        alias="conversationHistory", 
        description="Previous messages"
    )
    metadata: Optional[MetadataObject] = Field(None, description="Conversation metadata")


class ChatResponse(BaseModel):
    """Standard API response model."""
    model_config = ConfigDict(populate_by_name=True)
    
    status: str = Field(default="success", description="Response status")
    reply: str = Field(..., description="Agent response message")


class ErrorResponse(BaseModel):
    """Error response model."""
    model_config = ConfigDict(populate_by_name=True)
    
    status: str = Field(default="error", description="Error status")
    message: str = Field(..., description="Error description")
    code: Optional[str] = Field(None, description="Error code")


class IntelligenceData(BaseModel):
    """Extracted intelligence from conversations."""
    model_config = ConfigDict(populate_by_name=True)
    
    bank_accounts: List[str] = Field(default=[], description="Extracted bank account numbers")
    ifsc_codes: List[str] = Field(default=[], description="Extracted IFSC codes")
    upi_ids: List[str] = Field(default=[], description="Extracted UPI IDs")
    phone_numbers: List[str] = Field(default=[], description="Extracted phone numbers")
    phishing_links: List[str] = Field(default=[], description="Extracted malicious URLs")
    suspicious_keywords: List[str] = Field(default=[], description="Suspicious phrases")
    extraction_confidence: Dict[str, float] = Field(default={}, description="Confidence scores")


class BehavioralMetrics(BaseModel):
    """Scammer behavioral analysis metrics."""
    model_config = ConfigDict(populate_by_name=True)
    
    aggression_level: int = Field(default=1, ge=1, le=10, description="Aggression rating 1-10")
    sophistication_score: int = Field(default=1, ge=1, le=10, description="Sophistication rating 1-10")
    urgency_tactics: List[str] = Field(default=[], description="Urgency techniques used")
    social_engineering_techniques: List[str] = Field(default=[], description="SE techniques")
    persistence_indicators: List[str] = Field(default=[], description="Persistence patterns")
    emotional_manipulation_attempts: int = Field(default=0, description="Manipulation count")


class PersonaState(BaseModel):
    """Mrs. Sharma persona state tracking."""
    model_config = ConfigDict(populate_by_name=True)
    
    current_mood: str = Field(default="confused", description="Current emotional state")
    knowledge_level: str = Field(default="naive", description="Tech knowledge level")
    engagement_strategy: str = Field(default="information_gathering", description="Current strategy")
    conversation_phase: str = Field(default="introduction", description="Conversation phase")
    locale_adaptation: str = Field(default="english", description="Language adaptation")


class SessionData(BaseModel):
    """Complete session information."""
    model_config = ConfigDict(populate_by_name=True)
    
    session_id: str = Field(..., description="Unique session identifier")
    conversation_history: List[MessageObject] = Field(default=[], description="All messages")
    extracted_intelligence: IntelligenceData = Field(default_factory=IntelligenceData)
    scam_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Scam detection confidence")
    persona_active: bool = Field(default=False, description="Whether AI agent is active")
    conversation_complete: bool = Field(default=False, description="Conversation completion status")
    behavioral_analysis: BehavioralMetrics = Field(default_factory=BehavioralMetrics)
    persona_state: PersonaState = Field(default_factory=PersonaState)
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    metadata: Optional[MetadataObject] = Field(None, description="Session metadata")


class ExtractedIntelligence(BaseModel):
    """Intelligence report format for callback service."""
    model_config = ConfigDict(populate_by_name=True)
    
    bankAccounts: List[str] = Field(default=[], description="Bank account numbers")
    upiIds: List[str] = Field(default=[], description="UPI IDs")
    phishingLinks: List[str] = Field(default=[], description="Malicious URLs")
    phoneNumbers: List[str] = Field(default=[], description="Phone numbers")
    suspiciousKeywords: List[str] = Field(default=[], description="Suspicious keywords")


class IntelligenceReport(BaseModel):
    """Final intelligence report for hackathon callback."""
    model_config = ConfigDict(populate_by_name=True)
    
    sessionId: str = Field(..., description="Session identifier")
    scamDetected: bool = Field(..., description="Whether scam was detected")
    totalMessagesExchanged: int = Field(..., description="Total message count")
    extractedIntelligence: ExtractedIntelligence = Field(..., description="All extracted data")
    agentNotes: str = Field(..., description="Behavioral analysis summary")


class ConversationPhase(str, Enum):
    """Conversation phases for state management."""
    INTRODUCTION = "introduction"
    ENGAGEMENT = "engagement"
    EXTRACTION = "extraction"
    CONCLUSION = "conclusion"


class EngagementStrategy(str, Enum):
    """Agent engagement strategies."""
    INFORMATION_GATHERING = "information_gathering"
    TRUST_BUILDING = "trust_building"
    STRATEGIC_VULNERABILITY = "strategic_vulnerability"
    INTELLIGENCE_EXTRACTION = "intelligence_extraction"
