"""
Callback Service for the Agentic Honey-Pot system.
Handles automatic intelligence reporting to external services.
"""

import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime

from models import IntelligenceReport, ExtractedIntelligence, SessionData, BehavioralMetrics

logger = logging.getLogger(__name__)


class CallbackService:
    """
    Handles automatic intelligence reporting to external callback endpoints.
    
    Provides:
    - Automatic POST to hackathon evaluation endpoint
    - Proper authentication headers including x-api-key
    - Exponential backoff retry logic with tenacity
    - Comprehensive error logging without crashing the application
    """
    
    def __init__(self, api_key: str, callback_url: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"):
        """
        Initialize the callback service.
        
        Args:
            api_key: API key for authentication
            callback_url: External callback endpoint URL
        """
        self.api_key = api_key
        self.callback_url = callback_url
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10-second timeout
        
        logger.info(f"CallbackService initialized with endpoint: {callback_url}")
    
    def _generate_agent_notes(self, session: SessionData) -> str:
        """
        Generate comprehensive agent notes with behavioral analysis.
        
        Args:
            session: Session data to analyze
            
        Returns:
            Formatted agent notes string
        """
        behavioral = session.behavioral_analysis
        intelligence = session.extracted_intelligence
        
        # Basic conversation metrics
        message_count = len(session.conversation_history)
        scammer_messages = [msg for msg in session.conversation_history if msg.sender == "scammer"]
        agent_messages = [msg for msg in session.conversation_history if msg.sender != "scammer"]
        
        # Intelligence summary
        intel_summary = []
        if intelligence.bank_accounts:
            intel_summary.append(f"{len(intelligence.bank_accounts)} bank accounts")
        if intelligence.upi_ids:
            intel_summary.append(f"{len(intelligence.upi_ids)} UPI IDs")
        if intelligence.phone_numbers:
            intel_summary.append(f"{len(intelligence.phone_numbers)} phone numbers")
        if intelligence.phishing_links:
            intel_summary.append(f"{len(intelligence.phishing_links)} phishing links")
        
        intel_text = ", ".join(intel_summary) if intel_summary else "No significant intelligence"
        
        # Behavioral analysis
        aggression_desc = "Low" if behavioral.aggression_level <= 3 else "Medium" if behavioral.aggression_level <= 7 else "High"
        sophistication_desc = "Low" if behavioral.sophistication_score <= 3 else "Medium" if behavioral.sophistication_score <= 7 else "High"
        
        # Threat assessment
        threat_level = "Low"
        if behavioral.aggression_level >= 7 or behavioral.sophistication_score >= 7:
            threat_level = "High"
        elif behavioral.aggression_level >= 4 or behavioral.sophistication_score >= 4:
            threat_level = "Medium"
        
        # Generate comprehensive notes
        notes = f"""SCAMMER BEHAVIORAL ANALYSIS:
Aggression Level: {behavioral.aggression_level}/10 ({aggression_desc})
Sophistication Score: {behavioral.sophistication_score}/10 ({sophistication_desc})
Threat Assessment: {threat_level}

CONVERSATION METRICS:
Total Messages: {message_count}
Scammer Messages: {len(scammer_messages)}
Agent Responses: {len(agent_messages)}
Conversation Duration: {(session.last_activity - session.start_time).total_seconds():.0f} seconds

INTELLIGENCE EXTRACTED:
{intel_text}

BEHAVIORAL PATTERNS:
"""
        
        if behavioral.urgency_tactics:
            notes += f"Urgency Tactics: {', '.join(behavioral.urgency_tactics[:3])}\n"
        
        if behavioral.social_engineering_techniques:
            notes += f"Social Engineering: {', '.join(behavioral.social_engineering_techniques[:3])}\n"
        
        if behavioral.persistence_indicators:
            notes += f"Persistence Indicators: {', '.join(behavioral.persistence_indicators[:3])}\n"
        
        if behavioral.emotional_manipulation_attempts > 0:
            notes += f"Emotional Manipulation Attempts: {behavioral.emotional_manipulation_attempts}\n"
        
        # Operational assessment
        notes += f"\nOPERATIONAL ASSESSMENT:\n"
        
        if intelligence.bank_accounts or intelligence.upi_ids:
            notes += "HIGH VALUE: Financial credentials extracted - immediate threat to victims\n"
        
        if intelligence.phishing_links:
            notes += "INFRASTRUCTURE: Malicious links identified - potential for wider campaign\n"
        
        if behavioral.sophistication_score >= 7:
            notes += "ADVANCED THREAT: Sophisticated operation - likely organized group\n"
        elif behavioral.sophistication_score <= 3:
            notes += "BASIC THREAT: Low sophistication - likely individual operator\n"
        
        # Recommendations
        notes += f"\nRECOMMENDATIONS:\n"
        
        if intelligence.phone_numbers:
            notes += "- Block identified phone numbers across platforms\n"
        
        if intelligence.bank_accounts:
            notes += "- Report bank accounts to financial institutions\n"
        
        if intelligence.phishing_links:
            notes += "- Submit URLs to threat intelligence feeds\n"
        
        if behavioral.aggression_level >= 7:
            notes += "- High-priority case for law enforcement referral\n"
        
        return notes.strip()
    
    def _create_intelligence_report(self, session: SessionData) -> IntelligenceReport:
        """
        Create intelligence report from session data.
        
        Args:
            session: Session data to report
            
        Returns:
            Formatted intelligence report
        """
        intelligence = session.extracted_intelligence
        
        # Create extracted intelligence object
        extracted = ExtractedIntelligence(
            bankAccounts=intelligence.bank_accounts,
            upiIds=intelligence.upi_ids,
            phishingLinks=intelligence.phishing_links,
            phoneNumbers=intelligence.phone_numbers,
            suspiciousKeywords=intelligence.suspicious_keywords
        )
        
        # Generate agent notes
        agent_notes = self._generate_agent_notes(session)
        
        # Create report
        report = IntelligenceReport(
            sessionId=session.session_id,
            scamDetected=session.scam_confidence > 0.5,
            totalMessagesExchanged=len(session.conversation_history),
            extractedIntelligence=extracted,
            agentNotes=agent_notes
        )
        
        return report
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _send_report_with_retry(self, report_data: Dict[str, Any]) -> bool:
        """
        Send report with exponential backoff retry logic (1s, 2s, 4s).
        
        Args:
            report_data: Report data to send
            
        Returns:
            True if successful, False otherwise
        """
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "User-Agent": "Agentic-HoneyPot/1.0",
            "Accept": "application/json"
        }
        
        logger.info(f"Attempting to send report to {self.callback_url}")
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                self.callback_url,
                json=report_data,
                headers=headers
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    logger.info(f"Successfully sent intelligence report for session {report_data.get('sessionId')}")
                    logger.debug(f"Response: {response_text}")
                    return True
                else:
                    logger.error(f"Callback failed with status {response.status}: {response_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"HTTP {response.status}: {response_text}"
                    )
    
    async def send_intelligence_report(self, session: SessionData) -> bool:
        """
        Send intelligence report for a completed session.
        
        Args:
            session: Completed session data
            
        Returns:
            True if report sent successfully, False otherwise
        """
        try:
            # Create intelligence report
            report = self._create_intelligence_report(session)
            
            # Convert to dict for JSON serialization
            report_data = report.model_dump()
            
            logger.info(f"Sending intelligence report for session {session.session_id}")
            logger.debug(f"Report data: {report_data}")
            
            # Send with retry logic
            success = await self._send_report_with_retry(report_data)
            
            if success:
                logger.info(f"Intelligence report sent successfully for session {session.session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send intelligence report for session {session.session_id}: {e}")
            return False
    
    def send_intelligence_report_sync(self, session: SessionData) -> bool:
        """
        Synchronous wrapper for sending intelligence report.
        
        Args:
            session: Completed session data
            
        Returns:
            True if report sent successfully, False otherwise
        """
        try:
            # Create new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function
            return loop.run_until_complete(self.send_intelligence_report(session))
            
        except Exception as e:
            logger.error(f"Failed to send intelligence report synchronously for session {session.session_id}: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test connection to callback endpoint.
        
        Returns:
            True if endpoint is reachable, False otherwise
        """
        try:
            headers = {
                "x-api-key": self.api_key,
                "User-Agent": "Agentic-HoneyPot/1.0"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.callback_url, headers=headers) as response:
                    logger.info(f"Callback endpoint test: {response.status}")
                    return response.status in [200, 404, 405]  # Accept method not allowed as valid
                    
        except Exception as e:
            logger.error(f"Callback endpoint test failed: {e}")
            return False