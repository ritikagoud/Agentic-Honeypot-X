"""
Main FastAPI application for the Agentic Honey-Pot system.
Handles API routing, authentication, and request processing with comprehensive error handling.
"""

import os
import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional

from models import ChatRequest, ChatResponse, ErrorResponse, MessageObject
from scam_detector import ScamDetector
from agent_logic import AgentController
from session_manager import SessionManager
from intelligence_extractor import IntelligenceExtractor
from callback_service import CallbackService
from error_handler import ErrorHandler, EthicalCompliance, ServiceMonitor, with_error_handling

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global components
scam_detector = None
agent_controller = None
session_manager = None
intelligence_extractor = None
callback_service = None
error_handler = None
ethical_compliance = None
service_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive initialization."""
    global scam_detector, agent_controller, session_manager, intelligence_extractor
    global callback_service, error_handler, ethical_compliance, service_monitor
    
    logger.info("Initializing Agentic Honey-Pot system...")
    
    try:
        # Initialize error handling and compliance first
        error_handler = ErrorHandler()
        ethical_compliance = EthicalCompliance()
        service_monitor = ServiceMonitor()
        
        # Get configuration from environment
        api_key = os.getenv("API_KEY", "default_hackathon_key")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not set. AI features may be limited.")
        
        # Initialize core components with error handling
        logger.info("Initializing scam detector...")
        scam_detector = ScamDetector(api_key=gemini_api_key)
        
        logger.info("Initializing agent controller...")
        agent_controller = AgentController(api_key=gemini_api_key)
        
        logger.info("Initializing intelligence extractor...")
        intelligence_extractor = IntelligenceExtractor()
        
        logger.info("Initializing callback service...")
        callback_service = CallbackService(api_key=api_key)
        
        logger.info("Initializing session manager...")
        session_manager = SessionManager(callback_service=callback_service)
        
        # Test callback service connection
        try:
            connection_ok = await callback_service.test_connection()
            if connection_ok:
                logger.info("Callback service connection test successful")
            else:
                logger.warning("Callback service connection test failed - reports may not be delivered")
        except Exception as e:
            logger.warning(f"Callback service test failed: {e}")
        
        logger.info("System initialization complete - All components ready")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise
    finally:
        logger.info("Shutting down Agentic Honey-Pot system...")


# Create FastAPI application
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key authentication with comprehensive validation."""
    if not x_api_key:
        logger.warning("Request received without API key")
        raise HTTPException(
            status_code=401,
            detail="Missing x-api-key header"
        )
    
    # In production, validate against secure key storage
    # For hackathon, accept any non-empty key
    if not x_api_key.strip():
        logger.warning("Request received with empty API key")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.debug(f"Request authenticated with API key: {x_api_key[:8]}...")
    return x_api_key


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with comprehensive error logging."""
    logger.error(f"Unhandled exception in {request.url.path}: {str(exc)}", exc_info=True)
    
    # Record error in service monitor
    if service_monitor:
        service_monitor.record_request(0.0, success=False)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error - please try again later",
            code="INTERNAL_ERROR"
        ).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler with detailed logging."""
    logger.warning(f"HTTP exception in {request.url.path}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            code=f"HTTP_{exc.status_code}"
        ).model_dump()
    )


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "service": "agentic-honey-pot",
        "timestamp": time.time()
    }
    
    if service_monitor:
        health_status.update(service_monitor.get_health_status())
    
    if error_handler:
        health_status["service_status"] = error_handler.get_service_status()
    
    return health_status


@app.get("/metrics")
async def get_metrics():
    """Get system metrics and statistics."""
    metrics = {}
    
    if service_monitor:
        metrics["performance"] = service_monitor.get_health_status()
    
    if session_manager:
        metrics["sessions"] = session_manager.get_session_stats()
    
    if error_handler:
        metrics["errors"] = error_handler.get_service_status()
    
    if ethical_compliance:
        metrics["compliance"] = ethical_compliance.generate_compliance_report()
    
    return metrics


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Main chat endpoint with comprehensive request processing pipeline.
    
    This endpoint implements the complete flow:
    1. Request validation and authentication
    2. Ethical compliance checking
    3. Session management and conversation tracking
    4. Scam detection using AI and pattern matching
    5. AI agent activation and response generation
    6. Intelligence extraction and behavioral analysis
    7. Conversation completion detection
    8. Automatic intelligence reporting
    9. Comprehensive error handling and logging
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing chat request for session: {request.sessionId}")
        
        # Handle missing or None values with defaults
        conversation_history = request.conversationHistory or []
        metadata = request.metadata if request.metadata else None
        message_text = request.message
        
        # Ensure metadata is properly handled - create safe defaults if needed
        safe_metadata = None
        if metadata and (metadata.channel or metadata.language or metadata.locale):
            safe_metadata = metadata
        
        # Ethical compliance check
        if not ethical_compliance.check_illegal_instruction(message_text):
            logger.warning(f"Illegal instruction detected in session {request.sessionId}")
            raise HTTPException(
                status_code=400,
                detail="Request contains prohibited content"
            )
        
        # Get or create session with error handling
        try:
            session = session_manager.get_or_create_session(
                request.sessionId,
                safe_metadata
            )
        except Exception as e:
            error_handler.handle_session_error(request.sessionId, 'session_creation', e)
            raise HTTPException(status_code=500, detail="Failed to manage session")
        
        # Create MessageObject for the incoming message
        import time as time_module
        current_timestamp = int(time_module.time() * 1000)  # Current time in milliseconds
        
        message_obj = MessageObject(
            sender="scammer",
            text=message_text,
            timestamp=current_timestamp
        )
        
        # Add new message to session
        session_manager.add_message(request.sessionId, message_obj)
        
        # Detect scam intent with fallback handling
        scam_result = None
        try:
            scam_result = await scam_detector.analyze_message(
                message_text,
                conversation_history,
                session.scam_confidence
            )
        except Exception as e:
            logger.warning(f"Scam detection failed for session {request.sessionId}: {e}")
            # Use fallback scam detection
            scam_result = _fallback_scam_detection(message_text)
        
        # Update session with scam detection results
        if scam_result:
            session_manager.update_scam_confidence(
                request.sessionId,
                scam_result.confidence
            )
        
        # Generate response with comprehensive error handling
        response_text = None
        try:
            if scam_result and scam_result.is_scam and not session.persona_active:
                # Activate AI agent for scam engagement
                logger.info(f"Scam detected in session {request.sessionId}, activating Mrs. Sharma persona")
                session_manager.activate_persona(request.sessionId)
                
                response_text = await agent_controller.generate_response(
                    message_text,
                    conversation_history,
                    session.persona_state,
                    safe_metadata
                )
            elif session.persona_active:
                # Continue agent conversation
                response_text = await agent_controller.generate_response(
                    message_text,
                    conversation_history,
                    session.persona_state,
                    safe_metadata
                )
            else:
                # Neutral response for non-scam messages
                response_text = "I'm not sure I understand. Could you please clarify what you need help with?"
        
        except Exception as e:
            logger.warning(f"Agent response generation failed for session {request.sessionId}: {e}")
            response_text = error_handler.handle_gemini_failure('agent_response', e)
            if not response_text:
                response_text = "I'm having some technical difficulties. Could you please try again?"
        
        # Ethical compliance check for response
        if response_text and not ethical_compliance.validate_mrs_sharma_response(response_text):
            logger.warning(f"Response failed ethical validation for session {request.sessionId}")
            response_text = "I'm sorry, I can't help with that. Is there something else I can assist you with?"
        
        # Extract intelligence with error handling
        try:
            intelligence = intelligence_extractor.extract_from_message(message_text)
            if intelligence:
                session_manager.add_intelligence(request.sessionId, intelligence)
                logger.debug(f"Intelligence extracted for session {request.sessionId}")
        except Exception as e:
            error_handler.handle_extraction_error(message_text, e)
            # Continue processing even if extraction fails
        
        # Behavioral analysis with error handling
        try:
            behavioral_update = intelligence_extractor.analyze_behavior(
                message_text,
                conversation_history
            )
            if behavioral_update:
                session_manager.update_behavioral_analysis(request.sessionId, behavioral_update)
                logger.debug(f"Behavioral analysis updated for session {request.sessionId}")
        except Exception as e:
            logger.warning(f"Behavioral analysis failed for session {request.sessionId}: {e}")
            # Continue processing even if behavioral analysis fails
        
        # Add agent response to session
        if response_text:
            agent_message = MessageObject(
                sender="user",
                text=response_text,
                timestamp=current_timestamp + 1000  # 1 second later
            )
            session_manager.add_message(request.sessionId, agent_message)
        
        # Check for conversation completion and trigger reporting
        try:
            if session_manager.should_complete_conversation(request.sessionId):
                logger.info(f"Completing conversation for session {request.sessionId}")
                session_manager.complete_conversation(request.sessionId)
                # Intelligence reporting is automatically triggered by session manager
        except Exception as e:
            error_handler.handle_session_error(request.sessionId, 'conversation_completion', e)
            # Don't fail the request if completion fails
        
        # Record successful request
        processing_time = time.time() - start_time
        service_monitor.record_request(processing_time, success=True)
        
        logger.info(f"Successfully processed request for session {request.sessionId} in {processing_time:.3f}s")
        
        return ChatResponse(
            status="success",
            reply=str(response_text or "I'm here to help. What can I do for you?")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        processing_time = time.time() - start_time
        service_monitor.record_request(processing_time, success=False)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        processing_time = time.time() - start_time
        service_monitor.record_request(processing_time, success=False)
        
        logger.error(f"Unexpected error processing chat request for session {request.sessionId}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request - please try again"
        )


def _fallback_scam_detection(message_text: str) -> object:
    """
    Fallback scam detection when AI service is unavailable.
    
    Args:
        message_text: Message to analyze
        
    Returns:
        Simple scam detection result
    """
    class FallbackScamResult:
        def __init__(self, is_scam: bool, confidence: float):
            self.is_scam = is_scam
            self.confidence = confidence
    
    text_lower = message_text.lower()
    
    # Simple keyword-based detection
    scam_keywords = [
        'bank account', 'send money', 'transfer', 'urgent', 'verify',
        'suspended', 'blocked', 'otp', 'pin', 'cvv', 'government',
        'police', 'arrest', 'legal action', 'fine', 'penalty'
    ]
    
    keyword_count = sum(1 for keyword in scam_keywords if keyword in text_lower)
    
    if keyword_count >= 3:
        return FallbackScamResult(True, 0.8)
    elif keyword_count >= 2:
        return FallbackScamResult(True, 0.6)
    elif keyword_count >= 1:
        return FallbackScamResult(True, 0.4)
    else:
        return FallbackScamResult(False, 0.1)


@app.post("/admin/cleanup")
async def cleanup_sessions(api_key: str = Depends(verify_api_key)):
    """Administrative endpoint to cleanup old sessions."""
    try:
        # Cleanup stale sessions
        stale_count = session_manager.cleanup_stale_sessions()
        
        # Archive old completed sessions
        archived_count = session_manager.archive_completed_sessions(max_completed_sessions=50)
        
        return {
            "status": "success",
            "stale_sessions_cleaned": stale_count,
            "sessions_archived": archived_count,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="Cleanup operation failed")


@app.post("/admin/force-complete/{session_id}")
async def force_complete_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Administrative endpoint to force complete a session."""
    try:
        success = session_manager.force_complete_session(session_id, "Manual admin completion")
        
        if success:
            return {
                "status": "success",
                "message": f"Session {session_id} completed successfully",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Force completion failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Force completion failed")


if __name__ == "__main__":
    import uvicorn
    
    # Set environment variables if not already set
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not set. AI features will use fallback responses.")
    
    if not os.getenv("API_KEY"):
        logger.info("API_KEY not set. Using default key for hackathon.")
    
    logger.info("Starting Agentic Honey-Pot server...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production stability
        log_level="info",
        access_log=True
    )

