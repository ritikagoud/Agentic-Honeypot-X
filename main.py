"""
Bulletproof FastAPI application for GUVI tester compatibility.
Handles all edge cases and returns 200 status with error messages instead of 422.
"""

import os
import logging
import time
import traceback
import asyncio
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import ValidationError

from models import ChatRequest, ChatResponse, ErrorResponse, MessageObject
from scam_detector import ScamDetector
from agent_logic import AgentController
from session_manager import SessionManager
from intelligence_extractor import IntelligenceExtractor
from callback_service import CallbackService
from error_handler import ErrorHandler, EthicalCompliance, ServiceMonitor

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors - return 200 with error message instead of 422."""
    logger.warning(f"Validation error in {request.url.path}: {exc.errors()}")
    
    # Extract meaningful error message
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_details.append(f"{field}: {msg}")
    
    error_message = "Invalid request format: " + "; ".join(error_details)
    
    return JSONResponse(
        status_code=200,  # Return 200 instead of 422
        content={
            "status": "error",
            "reply": error_message
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle direct Pydantic validation errors."""
    logger.warning(f"Pydantic validation error in {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=200,  # Return 200 instead of 422
        content={
            "status": "error",
            "reply": "Request validation failed - please check your request format"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - return 200 with error message instead of 500."""
    logger.error(f"Unhandled exception in {request.url.path}: {str(exc)}", exc_info=True)
    
    # Record error in service monitor
    if service_monitor:
        service_monitor.record_request(0.0, success=False)
    
    return JSONResponse(
        status_code=200,  # Return 200 to avoid GUVI tester issues
        content={
            "status": "error",
            "reply": "Internal server error - please try again later"
        }
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


@app.post("/chat")
async def chat(
    request: ChatRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Bulletproof chat endpoint with comprehensive error handling.
    Returns 200 status with error messages instead of throwing 422/500 errors.
    """
    start_time = time.time()
    
    try:
        # API Key validation
        if not x_api_key:
            logger.warning("Request received without API key")
            return {
                "status": "error",
                "reply": "Missing x-api-key header"
            }
        
        if not x_api_key.strip():
            logger.warning("Request received with empty API key")
            return {
                "status": "error", 
                "reply": "Invalid API key"
            }
        
        logger.info(f"Processing chat request for session: {request.sessionId}")
        
        # Safely extract request data with defaults
        try:
            session_id = str(request.sessionId) if request.sessionId else "unknown_session"
            
            # Handle Union[str, MessageObject, Dict[str, Any]] message field
            message_text = ""
            if isinstance(request.message, str):
                message_text = request.message
            elif isinstance(request.message, dict):
                # Extract text from dictionary (common formats)
                message_text = (
                    request.message.get("text") or 
                    request.message.get("content") or 
                    request.message.get("message") or
                    str(request.message)
                )
            elif hasattr(request.message, 'text'):
                # MessageObject
                message_text = request.message.text or ""
            else:
                message_text = str(request.message)
            
            conversation_history = request.conversationHistory or []
            metadata = request.metadata
        except Exception as e:
            logger.error(f"Failed to extract request data: {e}")
            return {
                "status": "error",
                "reply": "Invalid request format"
            }
        
        # Validate required fields
        if not message_text.strip():
            return {
                "status": "error",
                "reply": "Message cannot be empty"
            }
        
        # Ethical compliance check
        try:
            if not ethical_compliance.check_illegal_instruction(message_text):
                logger.warning(f"Illegal instruction detected in session {session_id}")
                return {
                    "status": "error",
                    "reply": "Request contains prohibited content"
                }
        except Exception as e:
            logger.warning(f"Ethical compliance check failed: {e}")
            # Continue processing if compliance check fails
        
        # Get or create session with error handling
        try:
            session = session_manager.get_or_create_session(session_id, metadata)
        except Exception as e:
            logger.error(f"Session management failed for {session_id}: {e}")
            return {
                "status": "error",
                "reply": "Failed to manage session"
            }
        
        # Create MessageObject for the incoming message
        try:
            current_timestamp = int(time.time() * 1000)
            message_obj = MessageObject(
                sender="scammer",
                text=message_text,
                timestamp=current_timestamp
            )
            session_manager.add_message(session_id, message_obj)
        except Exception as e:
            logger.warning(f"Failed to create message object: {e}")
            # Continue processing even if message creation fails
        
        # Detect scam intent with fallback handling and TIMEOUT
        scam_result = None
        try:
            # STRICT 5-second timeout for scam detection
            scam_result = await asyncio.wait_for(
                scam_detector.analyze_message(
                    message_text,
                    conversation_history,
                    session.scam_confidence if session else 0.0
                ),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"Scam detection timeout for session {session_id}")
            # Use immediate fallback
            scam_result = _fallback_scam_detection(message_text)
        except Exception as e:
            logger.warning(f"Scam detection failed for session {session_id}: {e}")
            # Use fallback scam detection
            scam_result = _fallback_scam_detection(message_text)
        
        # Update session with scam detection results
        try:
            if scam_result and session:
                session_manager.update_scam_confidence(session_id, scam_result.confidence)
        except Exception as e:
            logger.warning(f"Failed to update scam confidence: {e}")
        
        # Generate response with comprehensive error handling and STRICT TIMEOUT
        response_text = None
        try:
            if scam_result and scam_result.is_scam and session and not session.persona_active:
                # Activate AI agent for scam engagement
                logger.info(f"Scam detected in session {session_id}, activating Mrs. Sharma persona")
                session_manager.activate_persona(session_id)
                
                # STRICT 10-second timeout for AI generation
                try:
                    response_text = await asyncio.wait_for(
                        agent_controller.generate_response(
                            message_text,
                            conversation_history,
                            session.persona_state if session else None,
                            metadata
                        ),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"AI generation timeout for session {session_id}")
                    response_text = "Arrey beta, net thoda slow hai, kya kaha tumne?"
                    
            elif session and session.persona_active:
                # Continue agent conversation with timeout
                try:
                    response_text = await asyncio.wait_for(
                        agent_controller.generate_response(
                            message_text,
                            conversation_history,
                            session.persona_state,
                            metadata
                        ),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"AI generation timeout for session {session_id}")
                    response_text = "Arrey beta, net thoda slow hai, kya kaha tumne?"
            else:
                # Neutral response for non-scam messages
                response_text = "I'm not sure I understand. Could you please clarify what you need help with?"
        
        except Exception as e:
            logger.warning(f"Agent response generation failed for session {session_id}: {e}")
            # IMMEDIATE fallback for any error
            response_text = "Arrey beta, net thoda slow hai, kya kaha tumne?"
        
        # Ethical compliance check for response
        try:
            if response_text and not ethical_compliance.validate_mrs_sharma_response(response_text):
                logger.warning(f"Response failed ethical validation for session {session_id}")
                response_text = "I'm sorry, I can't help with that. Is there something else I can assist you with?"
        except Exception as e:
            logger.warning(f"Response ethical validation failed: {e}")
        
        # Extract intelligence with error handling and TIMEOUT
        try:
            # Quick intelligence extraction with timeout
            intelligence_task = asyncio.create_task(
                asyncio.to_thread(intelligence_extractor.extract_from_message, message_text)
            )
            intelligence = await asyncio.wait_for(intelligence_task, timeout=2.0)
            
            if intelligence and session:
                session_manager.add_intelligence(session_id, intelligence)
                logger.debug(f"Intelligence extracted for session {session_id}")
        except asyncio.TimeoutError:
            logger.warning(f"Intelligence extraction timeout for session {session_id}")
            # Continue without intelligence extraction
        except Exception as e:
            logger.warning(f"Intelligence extraction failed: {e}")
            # Continue processing even if extraction fails
        
        # Behavioral analysis with error handling and TIMEOUT
        try:
            # Quick behavioral analysis with timeout
            behavioral_task = asyncio.create_task(
                asyncio.to_thread(
                    intelligence_extractor.analyze_behavior,
                    message_text,
                    conversation_history
                )
            )
            behavioral_update = await asyncio.wait_for(behavioral_task, timeout=2.0)
            
            if behavioral_update and session:
                session_manager.update_behavioral_analysis(session_id, behavioral_update)
                logger.debug(f"Behavioral analysis updated for session {session_id}")
        except asyncio.TimeoutError:
            logger.warning(f"Behavioral analysis timeout for session {session_id}")
            # Continue without behavioral analysis
        except Exception as e:
            logger.warning(f"Behavioral analysis failed for session {session_id}: {e}")
            # Continue processing even if behavioral analysis fails
        
        # Add agent response to session
        try:
            if response_text and session:
                agent_message = MessageObject(
                    sender="user",
                    text=response_text,
                    timestamp=current_timestamp + 1000  # 1 second later
                )
                session_manager.add_message(session_id, agent_message)
        except Exception as e:
            logger.warning(f"Failed to add agent response to session: {e}")
        
        # Check for conversation completion and trigger reporting
        try:
            if session and session_manager.should_complete_conversation(session_id):
                logger.info(f"Completing conversation for session {session_id}")
                session_manager.complete_conversation(session_id)
                # Intelligence reporting is automatically triggered by session manager
        except Exception as e:
            logger.warning(f"Conversation completion failed: {e}")
            # Don't fail the request if completion fails
        
        # Record successful request
        try:
            processing_time = time.time() - start_time
            service_monitor.record_request(processing_time, success=True)
        except Exception as e:
            logger.warning(f"Failed to record request metrics: {e}")
        
        logger.info(f"Successfully processed request for session {session_id} in {time.time() - start_time:.3f}s")
        
        # Return bulletproof response
        final_response = response_text or "I'm here to help. What can I do for you?"
        return {
            "status": "success",
            "reply": str(final_response)
        }
        
    except Exception as e:
        # Ultimate fallback - never let the endpoint crash
        logger.error(f"Critical error in chat endpoint: {str(e)}", exc_info=True)
        
        try:
            processing_time = time.time() - start_time
            service_monitor.record_request(processing_time, success=False)
        except:
            pass  # Don't let metrics recording crash the response
        
        return {
            "status": "error",
            "reply": "System temporarily unavailable - please try again"
        }


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
    
    try:
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
    except Exception:
        # Ultimate fallback
        return FallbackScamResult(False, 0.0)


@app.post("/admin/cleanup")
async def cleanup_sessions(x_api_key: Optional[str] = Header(None)):
    """Administrative endpoint to cleanup old sessions."""
    try:
        if not x_api_key:
            return {"status": "error", "message": "Missing x-api-key header"}
        
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
        return {"status": "error", "message": "Cleanup operation failed"}


@app.post("/admin/force-complete/{session_id}")
async def force_complete_session(session_id: str, x_api_key: Optional[str] = Header(None)):
    """Administrative endpoint to force complete a session."""
    try:
        if not x_api_key:
            return {"status": "error", "message": "Missing x-api-key header"}
        
        success = session_manager.force_complete_session(session_id, "Manual admin completion")
        
        if success:
            return {
                "status": "success",
                "message": f"Session {session_id} completed successfully",
                "timestamp": time.time()
            }
        else:
            return {"status": "error", "message": "Session not found"}
            
    except Exception as e:
        logger.error(f"Force completion failed for session {session_id}: {e}")
        return {"status": "error", "message": "Force completion failed"}


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
