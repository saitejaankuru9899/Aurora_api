import time
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Import our custom modules
from enhanced_qa_engine import enhanced_qa_engine
from logger_service import api_logger

# Initialize FastAPI app with enhanced configuration
app = FastAPI(
    title="Aurora Enhanced Question-Answering API",
    description="An intelligent question-answering system for Aurora member data using advanced NLP techniques",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    
    class Config:
        schema_extra = {
            "example": {
                "question": "When is Sophia planning her trip to Paris?"
            }
        }
    
class AnswerResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    messages_searched: Optional[int] = None
    question_type: Optional[str] = None
    target_entities: Optional[List[str]] = None
    method: str = "enhanced_nlp"
    timestamp: str
    processing_time_ms: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Sophia Al-Farsi mentioned 'this Friday'. (From: 'Please book a private jet to Paris for this Friday.')",
                "confidence": 0.8,
                "messages_searched": 17,
                "question_type": "when",
                "target_entities": ["Sophia", "Paris"],
                "method": "enhanced_nlp",
                "timestamp": "2024-01-15T10:30:45.123456",
                "processing_time_ms": 245.67
            }
        }

class LogStatsResponse(BaseModel):
    log_files: dict
    request_count: Optional[int] = None
    error_count: Optional[int] = None
    total_log_size_mb: Optional[float] = None

# Middleware to log all requests
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware to log all incoming requests"""
    
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    method = request.method
    path = request.url.path
    
    # Skip logging for health checks and docs
    if path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    # Log basic request info (detailed Q&A logging happens in the endpoint)
    if path not in ["/", "/stats", "/examples"]:
        print(f"📡 {method} {path} | IP: {client_ip} | Time: {processing_time:.2f}ms | Status: {response.status_code}")
    
    return response

@app.get("/")
async def root():
    """Root endpoint with comprehensive API information"""
    return {
        "service": "Aurora Enhanced Question-Answering API",
        "version": "2.0.0",
        "status": "operational",
        "description": "Intelligent Q&A system with advanced NLP capabilities and comprehensive logging",
        "features": [
            "🔍 Searches all 3,349+ member messages",
            "🧠 Dynamic entity extraction (people, places, events)",
            "🎯 Smart keyword filtering and relevance scoring",
            "⚡ Contextual answer generation with precise extraction",
            "🏷️ Multi-entity recognition and analysis",
            "📊 Comprehensive logging and analytics",
            "🔒 Request validation and error handling"
        ],
        "endpoints": {
            "ask": "/ask - POST/GET endpoint for questions",
            "health": "/health - System health check",
            "stats": "/stats - System and usage statistics",
            "logs": "/logs - Logging system statistics",
            "examples": "/examples - Example questions and usage guide",
            "docs": "/docs - Interactive API documentation"
        },
        "data_source": "Aurora member messages API (3,349+ messages)",
        "engine": "Enhanced NLP Engine v2.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    
    try:
        # Test data service connection
        from data_service import data_service
        sample_data = await data_service.fetch_member_data()
        data_health = len(sample_data) > 0
        
        # Check log system
        log_stats = api_logger.get_log_stats()
        log_health = "error" not in log_stats
        
        overall_health = data_health and log_health
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "operational",
                "qa_engine": "operational",
                "data_service": "operational" if data_health else "degraded",
                "logging_system": "operational" if log_health else "degraded"
            },
            "data_connection": {
                "status": "connected" if data_health else "disconnected",
                "sample_messages_available": len(sample_data) if data_health else 0
            },
            "system_info": {
                "engine_type": "Enhanced NLP Engine",
                "version": "2.0.0",
                "capabilities": ["entity_extraction", "semantic_search", "contextual_answers"]
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "api": "operational",
                "qa_engine": "degraded",
                "data_service": "error",
                "logging_system": "unknown"
            }
        }

@app.get("/stats")
async def api_stats():
    """Comprehensive API statistics and system information"""
    
    try:
        # Get data service statistics
        from data_service import data_service
        
        # Get basic data statistics
        sample_data = await data_service.fetch_member_data()
        analysis = await data_service.analyze_data_structure()
        
        # Get logging statistics
        log_stats = api_logger.get_log_stats()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "engine_type": "Enhanced NLP Engine v2.0",
                "api_version": "2.0.0",
                "uptime_info": "Available since API start"
            },
            "capabilities": {
                "question_types": ["when", "what", "where", "who", "how_many", "why", "how"],
                "features": {
                    "entity_extraction": True,
                    "multi_message_search": True,
                    "contextual_answers": True,
                    "precise_extraction": True,
                    "semantic_search": True,
                    "comprehensive_logging": True
                }
            },
            "data_info": {
                "total_available_messages": "3,349+",
                "sample_messages_cached": len(sample_data),
                "unique_senders": analysis.get("unique_senders", "unknown"),
                "search_method": "semantic_similarity + entity_matching",
                "data_source": "Aurora member messages API"
            },
            "supported_questions": [
                "When is [person] planning [activity]?",
                "How many [items] does [person] have/need?",
                "What [restaurant/place] did [person] book?",
                "Where is [person] going for [event]?",
                "Who booked/mentioned [item/service]?",
                "Why did [person] do [action]?",
                "How does [person] [action]?"
            ],
            "logging_stats": log_stats,
            "performance": {
                "avg_processing_time": "~200-500ms",
                "cache_enabled": True,
                "pagination_support": True,
                "error_handling": "comprehensive"
            }
        }
        
    except Exception as e:
        return {
            "status": "partial",
            "timestamp": datetime.now().isoformat(),
            "message": f"Stats partially available: {str(e)}",
            "engine_type": "Enhanced NLP Engine v2.0",
            "basic_info": {
                "api_version": "2.0.0",
                "status": "operational"
            }
        }

@app.get("/logs", response_model=LogStatsResponse)
async def log_statistics():
    """Get comprehensive logging system statistics"""
    
    try:
        log_stats = api_logger.get_log_stats()
        
        return LogStatsResponse(
            log_files=log_stats.get("log_files", {}),
            request_count=log_stats.get("request_count"),
            error_count=log_stats.get("error_count"),
            total_log_size_mb=log_stats.get("total_log_size_mb")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log statistics: {str(e)}"
        )

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest, req: Request):
    """
    Main endpoint for asking questions about member data using enhanced NLP
    """
    
    start_time = time.time()
    client_ip = req.client.host if req.client else "unknown"
    user_agent = req.headers.get("user-agent", "unknown")
    
    # Basic input validation
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    question = request.question.strip()
    
    # Advanced input validation
    if len(question) > 500:
        raise HTTPException(
            status_code=400, 
            detail="Question too long. Please limit to 500 characters."
        )
    
    if len(question) < 5:
        raise HTTPException(
            status_code=400, 
            detail="Question too short. Please provide a more detailed question."
        )
    
    # Log the API request
    api_logger.log_api_request(
        question=question,
        method="POST",
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    # Enhanced logging with question analysis preview
    print(f"🔍 Received question: {question}")
    
    try:
        # Use the enhanced intelligent Q&A engine
        print("🧠 Processing with Enhanced NLP Engine...")
        result = await enhanced_qa_engine.answer_question(question)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log successful response
        api_logger.log_qa_response(
            question=question,
            answer=result["answer"],
            confidence=result.get("confidence", 0),
            method="enhanced_nlp",
            success=True
        )
        
        # Enhanced console logging for debugging
        print(f"✅ Processing complete:")
        print(f"   - Question type: {result.get('question_type', 'unknown')}")
        print(f"   - Entities found: {result.get('target_entities', [])}")
        print(f"   - Messages searched: {result.get('messages_searched', 0)}")
        print(f"   - Confidence: {result.get('confidence', 0):.2f}")
        print(f"   - Processing time: {processing_time_ms:.2f}ms")
        
        return AnswerResponse(
            answer=result["answer"],
            confidence=result.get("confidence"),
            messages_searched=result.get("messages_searched"),
            question_type=result.get("question_type"),
            target_entities=result.get("target_entities"),
            method="enhanced_nlp",
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Enhanced error logging with stack trace
        error_traceback = traceback.format_exc()
        
        api_logger.log_error(
            question=question,
            error_message=str(e),
            error_type=type(e).__name__,
            stack_trace=error_traceback
        )
        
        # Log failed response
        api_logger.log_qa_response(
            question=question,
            answer="",
            confidence=0,
            method="enhanced_nlp",
            success=False
        )
        
        print(f"❌ Error processing question: {e}")
        print(f"   Question was: {question}")
        print(f"   Processing time: {processing_time_ms:.2f}ms")
        print(f"   Error type: {type(e).__name__}")
        
        # Graceful error handling with helpful message
        error_message = "I encountered an issue while processing your question. "
        
        if "timeout" in str(e).lower():
            error_message += "The request timed out. Please try again with a simpler question."
        elif "connection" in str(e).lower() or "fetch" in str(e).lower():
            error_message += "I'm having trouble accessing the data source. Please try again in a moment."
        elif "http" in str(e).lower():
            error_message += "There's an issue with the data service. Please try again later."
        else:
            error_message += "Please try rephrasing your question or try again later."
        
        raise HTTPException(
            status_code=500, 
            detail=error_message
        )

@app.get("/ask")
async def ask_question_get(question: Optional[str] = None, req: Request = None):
    """
    GET endpoint for asking questions (alternative to POST)
    """
    
    client_ip = req.client.host if req and req.client else "unknown"
    user_agent = req.headers.get("user-agent", "unknown") if req else "unknown"
    
    if not question:
        raise HTTPException(
            status_code=400, 
            detail="Question parameter is required. Example: /ask?question=When is Sophia going to Paris?"
        )
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Log the API request
    api_logger.log_api_request(
        question=question.strip(),
        method="GET",
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    # Use the same logic as POST endpoint
    request_obj = QuestionRequest(question=question.strip())
    return await ask_question(request_obj, req)

@app.get("/examples")
async def example_questions():
    """
    Endpoint providing example questions and comprehensive usage guide
    """
    return {
        "service": "Aurora Enhanced Q&A API",
        "version": "2.0.0",
        "example_questions": [
            {
                "question": "When is Sophia planning her trip to Paris?",
                "type": "temporal",
                "description": "Asks about timing/scheduling information",
                "expected_answer_type": "Specific time reference like 'this Friday'"
            },
            {
                "question": "How many people does Fatima need dinner for?",
                "type": "quantity", 
                "description": "Asks about numbers/quantities/counts",
                "expected_answer_type": "Specific number like 'four people'"
            },
            {
                "question": "What restaurant did Fatima book?",
                "type": "entity_identification",
                "description": "Asks about specific places/establishments",
                "expected_answer_type": "Restaurant name like 'The French Laundry'"
            },
            {
                "question": "Where is Armand going for the opera?",
                "type": "location",
                "description": "Asks about places/destinations",
                "expected_answer_type": "Location name like 'Milan'"
            },
            {
                "question": "Who booked a private jet?",
                "type": "person_identification",
                "description": "Asks about people/actors in events",
                "expected_answer_type": "Person name with context"
            }
        ],
        "usage_tips": [
            "✅ Be specific with names - use full names when possible (e.g., 'Sophia Al-Farsi')",
            "✅ Ask about one thing at a time for best results",
            "✅ Include context like 'trip', 'dinner', 'opera' to help the system understand",
            "✅ Questions starting with When/What/Where/Who/How many work best",
            "✅ Use proper capitalization for names and places",
            "⚠️ Avoid very complex questions with multiple sub-questions",
            "⚠️ Be patient - complex searches may take a few seconds"
        ],
        "api_usage": {
            "post_request": {
                "url": "/ask",
                "method": "POST",
                "body": {"question": "Your question here"},
                "content_type": "application/json"
            },
            "get_request": {
                "url": "/ask?question=Your%20question%20here",
                "method": "GET"
            }
        },
        "response_format": {
            "answer": "The extracted answer from member messages",
            "confidence": "Confidence score (0-1)",
            "messages_searched": "Number of messages analyzed",
            "question_type": "Detected question type",
            "target_entities": "List of people/places/things mentioned",
            "method": "Processing method used",
            "timestamp": "When the response was generated",
            "processing_time_ms": "How long processing took"
        }
    }

# Global exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "message": "Please check the API documentation for available endpoints",
        "available_endpoints": ["/", "/health", "/ask", "/stats", "/logs", "/examples", "/docs"],
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    return {
        "error": "Request validation failed",
        "message": "Please check your request format",
        "details": str(exc),
        "example": {"question": "When is Sophia planning her trip to Paris?"},
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "message": "The server encountered an unexpected error",
        "suggestion": "Please try again or contact support if the issue persists",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Enhanced startup logging
    print("🚀 Starting Aurora Enhanced Q&A API Server...")
    print("=" * 60)
    print("📡 Features: Enhanced NLP, Dynamic Entity Extraction, Comprehensive Search")
    print("📊 Logging: Comprehensive request/response/error logging enabled")
    print("🔗 Access API docs at: http://localhost:8000/docs")
    print("💡 Try example questions at: http://localhost:8000/examples")
    print("📈 View system stats at: http://localhost:8000/stats")
    print("📋 Check logs at: http://localhost:8000/logs")
    print("=" * 60)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)