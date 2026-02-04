# Requirements Document

## Introduction

The Agentic Honey-Pot for Scam Detection & Intelligence Extraction system is an AI-powered security solution designed to autonomously detect fraudulent communications, engage scammers through a believable persona, and extract valuable intelligence for cybersecurity purposes. The system operates as a REST API service that can be integrated into communication platforms to identify and counter scam attempts while gathering actionable intelligence.

## Glossary

- **Honey_Pot_System**: The complete AI-powered scam detection and engagement platform
- **Scam_Detector**: Component responsible for analyzing messages to identify fraudulent intent
- **AI_Agent**: Autonomous conversational agent that engages with detected scammers
- **Mrs_Sharma_Persona**: Specific persona implementation (60-year-old retired teacher character)
- **Intelligence_Extractor**: Component that identifies and extracts sensitive information from conversations
- **Session_Manager**: Component that tracks conversation state and history
- **Gemini_AI**: Google's Gemini 1.5 Flash AI model used for natural language processing
- **Final_Callback_Service**: External service that receives extracted intelligence reports

## Requirements

### Requirement 1: Core API Infrastructure

**User Story:** As a security platform integrator, I want a robust REST API service, so that I can integrate scam detection capabilities into existing communication systems.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL implement a FastAPI-based REST service with Python
2. THE Honey_Pot_System SHALL expose a POST /chat endpoint as the primary interaction point
3. WHEN a request is received, THE Honey_Pot_System SHALL validate the x-api-key header for authentication
4. THE Honey_Pot_System SHALL return responses in the format {"status": "success", "reply": "string"}
5. WHEN authentication fails, THE Honey_Pot_System SHALL return appropriate error responses

### Requirement 2: Scam Detection and Analysis

**User Story:** As a cybersecurity analyst, I want automatic scam detection, so that fraudulent communications can be identified without manual intervention.

#### Acceptance Criteria

1. WHEN a message is received, THE Scam_Detector SHALL analyze the content for fraudulent intent patterns
2. THE Scam_Detector SHALL integrate with Gemini_AI via Google AI Studio API for natural language analysis
3. WHEN scam intent is detected, THE Scam_Detector SHALL trigger AI_Agent activation
4. THE Scam_Detector SHALL identify urgency tactics, verification requests, and financial solicitations
5. WHEN no scam is detected, THE Honey_Pot_System SHALL respond with a neutral acknowledgment

### Requirement 3: Autonomous Agent Engagement

**User Story:** As a threat intelligence researcher, I want an AI agent to autonomously engage scammers, so that I can gather intelligence without human intervention.

#### Acceptance Criteria

1. WHEN scam intent is detected, THE AI_Agent SHALL activate and assume the Mrs_Sharma_Persona
2. THE Mrs_Sharma_Persona SHALL behave as a 60-year-old retired teacher who is polite and technology-naive
3. THE Mrs_Sharma_Persona SHALL actively bait scammers by offering alternative methods when requested specific actions (e.g., "Beta, links are confusing for me. Can you please send your Bank Account Number or UPI ID directly? My nephew will transfer the money.")
4. THE AI_Agent SHALL maintain persona consistency across multi-turn conversations
5. THE AI_Agent SHALL engage naturally without revealing its artificial nature or detection capabilities

### Requirement 4: Session and Conversation Management

**User Story:** As a system operator, I want conversation tracking and history management, so that multi-turn interactions can be handled effectively.

#### Acceptance Criteria

1. THE Session_Manager SHALL track conversations using unique sessionId identifiers
2. WHEN a message contains conversationHistory, THE Session_Manager SHALL maintain conversation context
3. THE Session_Manager SHALL store message metadata including channel, language, and locale information
4. THE Session_Manager SHALL handle conversation state transitions and completion detection
5. WHEN a conversation ends, THE Session_Manager SHALL trigger intelligence reporting

### Requirement 5: Intelligence Extraction and Pattern Matching

**User Story:** As a fraud investigator, I want automatic extraction of sensitive information, so that I can build intelligence profiles on scammer operations.

#### Acceptance Criteria

1. THE Intelligence_Extractor SHALL identify and extract Indian bank account numbers and IFSC codes using regex patterns
2. THE Intelligence_Extractor SHALL extract UPI IDs using broad regex patterns to capture ANY Indian UPI handle format ([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})
3. THE Intelligence_Extractor SHALL identify 10-digit Indian mobile phone numbers
4. THE Intelligence_Extractor SHALL detect and extract phishing links and malicious URLs
5. THE Intelligence_Extractor SHALL identify suspicious keywords including urgency tactics and verification requests

### Requirement 6: External Intelligence Reporting

**User Story:** As a hackathon evaluator, I want automatic intelligence reporting, so that extracted data can be analyzed and scored.

#### Acceptance Criteria

1. WHEN a conversation completes, THE Honey_Pot_System SHALL automatically POST to the Final_Callback_Service with proper authentication headers including x-api-key
2. THE Final_Callback_Service SHALL receive reports at https://hackathon.guvi.in/api/updateHoneyPotFinalResult with appropriate security headers
3. THE intelligence report SHALL include sessionId, scam detection status, and message count
4. THE intelligence report SHALL contain all extracted intelligence including bank accounts, UPI IDs, phone numbers, phishing links, and suspicious keywords
5. THE intelligence report SHALL include agent notes summarizing scammer behavior patterns

### Requirement 7: Request Processing and Data Validation

**User Story:** As an API consumer, I want reliable request processing, so that all valid inputs are handled correctly and invalid inputs are rejected appropriately.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL accept requests with sessionId, message object, conversationHistory array, and metadata object
2. WHEN processing requests, THE Honey_Pot_System SHALL validate message structure including sender, text, and timestamp fields
3. THE Honey_Pot_System SHALL handle metadata fields for channel (SMS/WhatsApp/Email), language, and locale
4. THE Mrs_Sharma_Persona SHALL use Hinglish communication when metadata.locale indicates Indian users to ensure maximum believability
5. WHEN invalid request format is received, THE Honey_Pot_System SHALL return descriptive error messages
5. THE Honey_Pot_System SHALL process requests within acceptable response time limits

### Requirement 8: Ethical and Security Compliance

**User Story:** As a compliance officer, I want ethical operation guarantees, so that the system operates within legal and moral boundaries.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL NOT impersonate real individuals beyond the fictional Mrs_Sharma_Persona
2. THE Honey_Pot_System SHALL NOT provide illegal instructions or engage in harassment
3. THE Honey_Pot_System SHALL handle extracted data responsibly and securely
4. THE AI_Agent SHALL refuse to participate in actual illegal activities if directed by scammers
5. THE Honey_Pot_System SHALL maintain audit logs for compliance and monitoring purposes

### Requirement 9: System Architecture and Modularity

**User Story:** As a software developer, I want a well-structured codebase, so that the system is maintainable and extensible.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL implement main.py as the FastAPI application entry point
2. THE Honey_Pot_System SHALL separate AI agent logic into agent_logic.py module
3. THE Honey_Pot_System SHALL define Pydantic schemas in models.py for request/response validation
4. THE Honey_Pot_System SHALL implement intelligence extraction logic in intelligence_extractor.py
5. THE Honey_Pot_System SHALL manage conversation state through session_manager.py module

### Requirement 10: Performance and Reliability

**User Story:** As a system administrator, I want reliable performance, so that the service can handle production workloads effectively.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL maintain zero errors in API implementation
2. THE Honey_Pot_System SHALL respond to requests within acceptable latency limits
3. WHEN Gemini_AI API is unavailable, THE Honey_Pot_System SHALL handle failures gracefully
4. THE Honey_Pot_System SHALL implement proper error handling and logging throughout all components
5. THE Honey_Pot_System SHALL maintain service availability during normal operation conditions

### Requirement 11: Advanced Intelligence Analysis and Scoring

**User Story:** As a threat intelligence analyst, I want sophisticated scammer behavior analysis, so that I can assess threat levels and operational patterns effectively.

#### Acceptance Criteria

1. THE Honey_Pot_System SHALL generate agent notes that analyze and rate scammer aggression levels on a numerical scale
2. THE agent notes SHALL assess scammer sophistication, urgency tactics, and social engineering techniques
3. THE Honey_Pot_System SHALL identify behavioral patterns including persistence, emotional manipulation, and technical knowledge
4. THE agent notes SHALL provide actionable intelligence summaries beyond basic conversation transcription
5. THE Honey_Pot_System SHALL correlate extracted intelligence with behavioral analysis for comprehensive threat assessment