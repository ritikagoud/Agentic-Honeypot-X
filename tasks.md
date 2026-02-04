# Implementation Plan: Agentic Honey-Pot for Scam Detection & Intelligence Extraction

## Overview

This implementation plan breaks down the agentic honey-pot system into discrete, incremental coding tasks. Each task builds upon previous work to create a comprehensive AI-powered scam detection and intelligence extraction system. The implementation follows a modular architecture with clear separation of concerns, ensuring maintainability and extensibility.

## Tasks

- [x] 1. Set up project structure and core dependencies
  - Create project directory structure with all required Python modules
  - Set up requirements.txt with FastAPI, Pydantic, Google AI SDK, tenacity for retry logic, Hypothesis for testing
  - Create main.py as FastAPI application entry point
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 2. Implement core data models and validation schemas
  - [x] 2.1 Create Pydantic models in models.py
    - Define ChatRequest, ChatResponse, MessageObject, MetadataObject schemas
    - Implement IntelligenceData, BehavioralMetrics, SessionData models
    - Add request/response validation with proper error handling
    - _Requirements: 7.1, 7.2_

  - [ ]* 2.2 Write property test for data model validation
    - **Property 9: Request Validation and Processing**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ] 3. Implement authentication and API infrastructure
  - [x] 3.1 Create FastAPI application with authentication middleware
    - Implement x-api-key header validation
    - Set up POST /chat endpoint with proper routing
    - Add error handling middleware for authentication failures
    - _Requirements: 1.2, 1.3, 1.5_

  - [ ] 3.2 Implement response formatting and error handling
    - Ensure all responses follow {"status": "success", "reply": "string"} format
    - Create descriptive error messages for various failure scenarios
    - Add proper HTTP status codes for different error types
    - _Requirements: 1.4, 7.5_

  - [ ]* 3.3 Write property tests for authentication and response format
    - **Property 1: Authentication and Authorization**
    - **Property 2: Response Format Consistency**
    - **Validates: Requirements 1.3, 1.4, 1.5, 7.5**

- [ ] 4. Implement scam detection engine
  - [x] 4.1 Create scam_detector.py with Gemini AI integration
    - Set up Google AI Studio API client for Gemini 1.5 Flash
    - Implement scam pattern detection logic for urgency tactics, financial solicitations
    - Create confidence scoring system for detection accuracy
    - Add fallback rule-based detection for AI service failures
    - _Requirements: 2.1, 2.2, 2.4_

  - [ ] 4.2 Implement detection trigger and response logic
    - Connect scam detection to agent activation
    - Implement neutral response generation for non-scam messages
    - Add detection result logging and monitoring
    - _Requirements: 2.3, 2.5_

  - [ ]* 4.3 Write property tests for scam detection
    - **Property 3: Scam Detection and Agent Activation**
    - **Validates: Requirements 2.1, 2.3, 2.4, 2.5, 3.1**

- [ ] 5. Checkpoint - Ensure core API and detection functionality works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Mrs. Sharma persona and AI agent logic
  - [x] 6.1 Create agent_logic.py with persona implementation
    - Implement Mrs. Sharma character traits (polite, technology-naive, helpful)
    - Create strategic vulnerability response patterns with active baiting
    - Implement locale-aware communication (Hinglish for Indian users)
    - Add persona consistency tracking across conversation turns
    - _Requirements: 3.2, 3.3, 7.4_

  - [ ] 6.2 Implement conversation management and context awareness
    - Create multi-turn conversation handling with context preservation
    - Implement agent activation and deactivation logic
    - Add natural conversation flow without revealing AI nature
    - Ensure persona consistency across all interactions
    - _Requirements: 3.1, 3.4, 3.5_

  - [ ]* 6.3 Write property tests for persona behavior
    - **Property 4: Persona Consistency and Strategic Vulnerability**
    - **Property 5: Locale-Aware Communication**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 7.4**

- [ ] 7. Implement session management system
  - [x] 7.1 Create session_manager.py with conversation tracking
    - Implement sessionId-based conversation isolation
    - Create conversation history storage and retrieval
    - Add metadata storage for channel, language, locale information
    - Implement conversation state transitions and completion detection
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 7.2 Implement conversation completion and reporting triggers
    - Add automatic detection of conversation completion
    - Create triggers for intelligence reporting when conversations end
    - Implement session cleanup and archival processes
    - _Requirements: 4.5_

  - [ ]* 7.3 Write property tests for session management
    - **Property 6: Session Management and Context Preservation**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 8. Implement intelligence extraction engine
  - [x] 8.1 Create intelligence_extractor.py with pattern matching
    - Implement comprehensive regex patterns for bank accounts, IFSC codes
    - Create broad UPI ID extraction using [a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64} pattern
    - Add phone number extraction for 10-digit Indian mobile numbers
    - Implement URL and phishing link detection and extraction
    - Add suspicious keyword identification and extraction
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 8.2 Implement behavioral analysis and scoring
    - Create aggression level scoring system (1-10 numerical scale)
    - Implement sophistication assessment algorithms
    - Add social engineering technique identification
    - Create behavioral pattern analysis for persistence and manipulation
    - _Requirements: 11.1, 11.2, 11.3_

  - [ ]* 8.3 Write property tests for intelligence extraction
    - **Property 7: Comprehensive Intelligence Extraction**
    - **Property 12: Advanced Behavioral Analysis**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 11.1, 11.2, 11.3, 11.4, 11.5**

- [ ] 9. Implement external callback and reporting system
  - [x] 9.1 Create callback_service.py with bulletproof automatic reporting
    - Implement automatic POST to https://hackathon.guvi.in/api/updateHoneyPotFinalResult
    - Add proper authentication headers including x-api-key for callback requests
    - Implement exponential backoff retry logic using tenacity library or custom implementation
    - Set strict 10-second timeout for each callback attempt
    - Retry failed requests (non-200 status) at least 3 times with increasing delays (1s, 2s, 4s)
    - Add comprehensive error logging without crashing the application
    - _Requirements: 6.1, 6.2_

  - [x] 9.2 Implement comprehensive report generation
    - Create reports with sessionId, scam detection status, message count
    - Include all extracted intelligence (bank accounts, UPI IDs, phone numbers, links, keywords)
    - Generate actionable agent notes with behavioral analysis and threat assessment
    - Add intelligence correlation with behavioral data
    - _Requirements: 6.3, 6.4, 6.5, 11.4, 11.5_

  - [ ]* 9.3 Write property tests for reporting system
    - **Property 8: Automatic Intelligence Reporting**
    - **Validates: Requirements 4.5, 6.1, 6.3, 6.4, 6.5**

- [ ] 10. Implement error handling and resilience features
  - [x] 10.1 Add comprehensive error handling throughout all components
    - Implement graceful handling of Gemini AI service failures
    - Add proper error logging and audit trail generation
    - Create fallback mechanisms for external service unavailability
    - Implement proper exception handling and recovery
    - _Requirements: 10.3, 10.4, 8.5_

  - [x] 10.2 Implement ethical compliance and safety measures
    - Add checks to prevent impersonation of real individuals beyond Mrs. Sharma
    - Implement refusal mechanisms for illegal instructions and activities
    - Create audit logging for all system activities and decisions
    - Add compliance monitoring and reporting capabilities
    - _Requirements: 8.1, 8.2, 8.4, 8.5_

  - [ ]* 10.3 Write property tests for error handling and ethics
    - **Property 10: Ethical Behavior Compliance**
    - **Property 11: Error Handling and Service Resilience**
    - **Property 13: Audit Logging**
    - **Validates: Requirements 8.1, 8.2, 8.4, 8.5, 10.3, 10.4**

- [ ] 11. Integration and end-to-end wiring
  - [x] 11.1 Wire all components together in main.py
    - Connect API endpoints to scam detection engine
    - Integrate agent logic with session management
    - Wire intelligence extraction to reporting system
    - Ensure proper data flow between all components
    - _Requirements: All requirements integration_

  - [x] 11.2 Implement request processing pipeline
    - Create complete request-to-response processing flow
    - Add proper error propagation and handling throughout pipeline
    - Implement logging and monitoring for all pipeline stages
    - Ensure proper cleanup and resource management
    - _Requirements: 7.6_

  - [ ]* 11.3 Write integration tests for end-to-end functionality
    - Test complete conversation flows from detection to reporting
    - Validate multi-turn conversation handling
    - Test error scenarios and recovery mechanisms
    - Verify external service integration

- [ ] 12. Final checkpoint and validation
  - [x] 12.1 Comprehensive testing and validation
    - Run all property-based tests with minimum 100 iterations each
    - Validate all unit tests pass
    - Test with realistic scam conversation scenarios
    - Verify Mrs. Sharma persona believability and effectiveness

  - [x] 12.2 Performance optimization and final polish
    - Optimize response times for API endpoints
    - Ensure proper resource cleanup and memory management
    - Add final logging and monitoring enhancements
    - Validate hackathon requirements compliance

  - [x] 12.3 Final system validation
    - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and integration points
- The implementation prioritizes intelligence extraction effectiveness and persona believability
- All components include comprehensive error handling and logging
- The system maintains ethical boundaries while maximizing intelligence gathering