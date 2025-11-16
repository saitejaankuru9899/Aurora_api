import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

class APILogger:
    """Comprehensive logging service for Aurora Q&A API"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup different log files
        self.api_log_file = self.log_dir / "api_requests.log"
        self.qa_log_file = self.log_dir / "qa_processing.log"
        self.error_log_file = self.log_dir / "errors.log"
        self.json_log_file = self.log_dir / "structured_logs.jsonl"
        
        # Setup loggers
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # API Request Logger
        self.api_logger = logging.getLogger("aurora_api")
        self.api_logger.setLevel(logging.INFO)
        
        # Q&A Processing Logger
        self.qa_logger = logging.getLogger("aurora_qa")
        self.qa_logger.setLevel(logging.INFO)
        
        # Error Logger
        self.error_logger = logging.getLogger("aurora_errors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Clear existing handlers to avoid duplicates
        for logger in [self.api_logger, self.qa_logger, self.error_logger]:
            logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # API Request Handler
        api_handler = logging.FileHandler(self.api_log_file, encoding='utf-8')
        api_handler.setFormatter(detailed_formatter)
        self.api_logger.addHandler(api_handler)
        
        # Q&A Processing Handler
        qa_handler = logging.FileHandler(self.qa_log_file, encoding='utf-8')
        qa_handler.setFormatter(detailed_formatter)
        self.qa_logger.addHandler(qa_handler)
        
        # Error Handler
        error_handler = logging.FileHandler(self.error_log_file, encoding='utf-8')
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Console Handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(console_handler)
    
    def log_api_request(self, 
                       question: str, 
                       method: str = "POST",
                       client_ip: str = "unknown",
                       user_agent: str = "unknown"):
        """Log incoming API request"""
        
        timestamp = datetime.now().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "event_type": "api_request",
            "method": method,
            "question": question,
            "question_length": len(question),
            "client_ip": client_ip,
            "user_agent": user_agent
        }
        
        # Structured log
        self.api_logger.info(
            f"REQUEST | {method} | IP: {client_ip} | Question: '{question[:100]}{'...' if len(question) > 100 else ''}'"
        )
        
        # JSON log
        self._write_json_log(log_data)
        
        return log_data
    
    def log_qa_processing(self,
                         question: str,
                         question_analysis: Dict[str, Any],
                         messages_searched: int,
                         relevant_messages: List[Dict[str, Any]],
                         processing_time_ms: float):
        """Log Q&A processing details"""
        
        timestamp = datetime.now().isoformat()
        
        # Extract key info from relevant messages (without logging full content for privacy)
        message_summary = []
        for msg in relevant_messages[:5]:  # Top 5 most relevant
            message_summary.append({
                "user_name": msg.get("user_name", "unknown"),
                "message_length": len(msg.get("message", "")),
                "relevance_score": msg.get("relevance_score", msg.get("entity_match_score", 0))
            })
        
        log_data = {
            "timestamp": timestamp,
            "event_type": "qa_processing",
            "question": question,
            "question_analysis": {
                "question_type": question_analysis.get("question_type", "unknown"),
                "target_entities": question_analysis.get("target_entities", []),
                "keywords": question_analysis.get("keywords", []),
                "confidence": question_analysis.get("confidence", 0)
            },
            "search_results": {
                "total_messages_searched": messages_searched,
                "relevant_messages_found": len(relevant_messages),
                "top_messages": message_summary
            },
            "processing_time_ms": processing_time_ms
        }
        
        self.qa_logger.info(
            f"PROCESSING | Type: {question_analysis.get('question_type', 'unknown')} | "
            f"Entities: {question_analysis.get('target_entities', [])} | "
            f"Messages: {messages_searched} searched, {len(relevant_messages)} relevant | "
            f"Time: {processing_time_ms:.2f}ms"
        )
        
        # JSON log
        self._write_json_log(log_data)
        
        return log_data
    
    def log_qa_response(self,
                       question: str,
                       answer: str,
                       confidence: float,
                       method: str,
                       success: bool = True):
        """Log Q&A response details"""
        
        timestamp = datetime.now().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "event_type": "qa_response",
            "question": question,
            "answer": answer,
            "answer_length": len(answer),
            "confidence": confidence,
            "method": method,
            "success": success
        }
        
        status = "SUCCESS" if success else "FAILED"
        self.api_logger.info(
            f"RESPONSE | {status} | Confidence: {confidence:.2f} | "
            f"Answer: '{answer[:100]}{'...' if len(answer) > 100 else ''}'"
        )
        
        # JSON log
        self._write_json_log(log_data)
        
        return log_data
    
    def log_error(self,
                  question: str,
                  error_message: str,
                  error_type: str,
                  stack_trace: Optional[str] = None):
        """Log errors with context"""
        
        timestamp = datetime.now().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "event_type": "error",
            "question": question,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace
        }
        
        self.error_logger.error(
            f"ERROR | {error_type} | Question: '{question}' | Error: {error_message}"
        )
        
        if stack_trace:
            self.error_logger.error(f"STACK_TRACE | {stack_trace}")
        
        # JSON log
        self._write_json_log(log_data)
        
        return log_data
    
    def log_data_fetch(self,
                      operation: str,
                      messages_count: int,
                      success: bool,
                      error_message: Optional[str] = None):
        """Log data fetching operations"""
        
        timestamp = datetime.now().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "event_type": "data_fetch",
            "operation": operation,
            "messages_count": messages_count,
            "success": success,
            "error_message": error_message
        }
        
        status = "SUCCESS" if success else "FAILED"
        self.qa_logger.info(
            f"DATA_FETCH | {status} | Operation: {operation} | Messages: {messages_count}"
        )
        
        if error_message:
            self.qa_logger.error(f"DATA_FETCH_ERROR | {error_message}")
        
        # JSON log
        self._write_json_log(log_data)
        
        return log_data
    
    def _write_json_log(self, log_data: Dict[str, Any]):
        """Write structured log data to JSON Lines file"""
        
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            # If JSON logging fails, at least log to console
            print(f"Failed to write JSON log: {e}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        
        try:
            stats = {
                "log_files": {
                    "api_requests": {
                        "file": str(self.api_log_file),
                        "exists": self.api_log_file.exists(),
                        "size_mb": self.api_log_file.stat().st_size / (1024*1024) if self.api_log_file.exists() else 0
                    },
                    "qa_processing": {
                        "file": str(self.qa_log_file),
                        "exists": self.qa_log_file.exists(),
                        "size_mb": self.qa_log_file.stat().st_size / (1024*1024) if self.qa_log_file.exists() else 0
                    },
                    "errors": {
                        "file": str(self.error_log_file),
                        "exists": self.error_log_file.exists(),
                        "size_mb": self.error_log_file.stat().st_size / (1024*1024) if self.error_log_file.exists() else 0
                    },
                    "structured": {
                        "file": str(self.json_log_file),
                        "exists": self.json_log_file.exists(),
                        "size_mb": self.json_log_file.stat().st_size / (1024*1024) if self.json_log_file.exists() else 0
                    }
                },
                "total_log_size_mb": sum([
                    f["size_mb"] for f in stats.get("log_files", {}).values() 
                    if isinstance(f, dict) and "size_mb" in f
                ]) if 'stats' in locals() else 0
            }
            
            # Count total requests from JSON log
            if self.json_log_file.exists():
                try:
                    request_count = 0
                    error_count = 0
                    
                    with open(self.json_log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                if log_entry.get("event_type") == "api_request":
                                    request_count += 1
                                elif log_entry.get("event_type") == "error":
                                    error_count += 1
                            except json.JSONDecodeError:
                                continue
                    
                    stats["request_count"] = request_count
                    stats["error_count"] = error_count
                    
                except Exception as e:
                    stats["count_error"] = str(e)
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get log stats: {str(e)}"}

# Create global logger instance
api_logger = APILogger()