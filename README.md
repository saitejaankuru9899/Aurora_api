# Aurora Enhanced Question-Answering API 🚀

An intelligent question-answering system for Aurora member data using advanced NLP techniques and comprehensive logging.

## 🌟 Features

### 🧠 Enhanced NLP Engine
- **Dynamic Entity Extraction**: Automatically identifies people, places, and organizations
- **Smart Keyword Filtering**: Intelligent relevance scoring and context analysis
- **Multi-Question Type Support**: when, what, where, who, how many, why, how
- **Contextual Answer Generation**: Provides precise, targeted answers from message content
- **Semantic Search**: Searches through all 3,349+ member messages intelligently

### 📊 Comprehensive Logging
- **Request/Response Logging**: Complete API interaction tracking
- **Processing Analytics**: Question analysis, search results, and performance metrics
- **Error Tracking**: Detailed error logging with stack traces
- **JSON Structured Logs**: Machine-readable logs for analytics
- **Performance Monitoring**: Response times and system health tracking

### 🔧 Robust Architecture
- **FastAPI Framework**: Modern, high-performance API with automatic documentation
- **Enhanced Error Handling**: Graceful failures with helpful error messages
- **Input Validation**: Comprehensive request validation and sanitization
- **Health Monitoring**: System health checks and status reporting
- **CORS Support**: Cross-origin request handling

## 📁 Project Structure

```
aurora-qa-api/
├── main.py                     # Main FastAPI application
├── enhanced_qa_engine.py       # Core Q&A processing engine
├── precise_answer_extractor.py # Answer extraction logic
├── data_service.py             # Aurora API data management
├── logger_service.py           # Comprehensive logging system
├── test_api.py                 # Complete test suite
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
└── logs/                       # Log files directory
    ├── api_requests.log        # API request logs
    ├── qa_processing.log       # Q&A processing logs
    ├── errors.log              # Error logs
    └── structured_logs.jsonl   # JSON structured logs
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd aurora-qa-api

# Create virtual environment
python -m venv aurora_qa_env

# Activate virtual environment
# Windows:
aurora_qa_env\Scripts\activate
# macOS/Linux:
source aurora_qa_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python main.py
```

The API will start on `http://localhost:8000`

### 3. Test the System

```bash
# Run comprehensive test suite
python test_api.py

# Or test individual endpoints
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "When is Sophia planning her trip to Paris?"}'
```

## 📖 API Documentation

### Core Endpoints

#### POST `/ask` - Ask Questions
Submit questions about Aurora member data.

**Request:**
```json
{
  "question": "When is Sophia planning her trip to Paris?"
}
```

**Response:**
```json
{
  "answer": "Sophia Al-Farsi mentioned 'this Friday'. (From: 'Please book a private jet to Paris for this Friday.')",
  "confidence": 0.8,
  "messages_searched": 17,
  "question_type": "when",
  "target_entities": ["Sophia", "Paris"],
  "method": "enhanced_nlp",
  "timestamp": "2024-01-15T10:30:45.123456",
  "processing_time_ms": 245.67
}
```

#### GET `/ask?question=...` - Alternative Question Interface
Ask questions via GET request with URL parameters.

**Example:**
```
GET /ask?question=How many people does Fatima need dinner for?
```

### Utility Endpoints

- **GET `/`** - API information and feature overview
- **GET `/health`** - System health check and service status
- **GET `/stats`** - Comprehensive system statistics and capabilities
- **GET `/logs`** - Logging system statistics
- **GET `/examples`** - Example questions and usage guide
- **GET `/docs`** - Interactive API documentation (Swagger UI)

## 🎯 Supported Question Types

### ⏰ Temporal Questions (When)
- "When is [person] planning [activity]?"
- "What time is [person]'s [event]?"

**Example Response:**
```
Sophia Al-Farsi mentioned "this Friday". (From: "Please book a private jet to Paris for this Friday.")
```

### 📊 Quantity Questions (How Many)
- "How many [items] does [person] need?"
- "How much [thing] did [person] mention?"

**Example Response:**
```
Fatima El-Tahir mentioned 4 people. (From: "Can you confirm my dinner reservation at The French Laundry for four people tonight?")
```

### 🏢 Entity Questions (What)
- "What [restaurant/place] did [person] book?"
- "What is [person]'s [preference]?"

**Example Response:**
```
Fatima El-Tahir mentioned "The French Laundry". (From: "Can you confirm my dinner reservation at The French Laundry...")
```

### 📍 Location Questions (Where)
- "Where is [person] going for [event]?"
- "Where did [person] book [item]?"

**Example Response:**
```
Armand Dupont mentioned "Milan". (From: "I need two tickets to the opera in Milan this Saturday.")
```

### 👤 Person Questions (Who)
- "Who booked [item/service]?"
- "Who mentioned [topic]?"

**Example Response:**
```
Sophia Al-Farsi (based on their message: "Please book a private jet to Paris for this Friday.")
```

## 📊 Logging System

The API provides comprehensive logging across multiple dimensions:

### Log Files
- **`api_requests.log`** - All API requests with timestamps, IPs, questions
- **`qa_processing.log`** - Q&A engine processing details and performance
- **`errors.log`** - Error tracking with stack traces and context
- **`structured_logs.jsonl`** - Machine-readable JSON logs for analytics

### Log Content
Each API request logs:
- **Request Details**: Question, client IP, user agent, timestamp
- **Processing Analysis**: Question type, entities found, keywords extracted
- **Search Results**: Messages searched, relevant messages found, relevance scores
- **Performance Metrics**: Processing time, confidence scores
- **Response Data**: Generated answer, success/failure status

### Accessing Logs
```bash
# View recent API requests
tail -f logs/api_requests.log

# View Q&A processing details
tail -f logs/qa_processing.log

# View errors
tail -f logs/errors.log

# Get log statistics via API
curl http://localhost:8000/logs
```

## 🧪 Testing

### Automated Test Suite
Run the comprehensive test suite:

```bash
python test_api.py
```

**Test Categories:**
- ✅ Basic endpoint functionality
- ✅ Question-answering accuracy
- ✅ GET endpoint support
- ✅ Error handling and validation
- ✅ Performance and load testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# System stats
curl http://localhost:8000/stats

# Example questions
curl http://localhost:8000/examples

# Test question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What restaurant did Fatima book?"}'
```

## 🔧 Configuration

### Environment Variables
The API supports these optional environment variables:

- `API_HOST` - Host to bind to (default: "0.0.0.0")
- `API_PORT` - Port to bind to (default: 8000)
- `LOG_LEVEL` - Logging level (default: "INFO")
- `CACHE_DURATION` - Data cache duration in seconds (default: 300)

### Data Source
The API connects to Aurora's member messages API:
- **Endpoint**: `https://november7-730026606190.europe-west1.run.app/messages`
- **Total Messages**: 3,349+
- **Update Frequency**: Real-time via API calls
- **Caching**: 5-minute cache for performance optimization

## 📈 Performance

### Typical Response Times
- **Simple Questions**: 200-400ms
- **Complex Multi-entity**: 400-800ms
- **Full Dataset Search**: 500-1200ms

### System Capabilities
- **Concurrent Requests**: Supports multiple simultaneous requests
- **Data Coverage**: Searches all available messages (3,349+)
- **Cache Efficiency**: Intelligent caching reduces API calls
- **Error Recovery**: Graceful handling of API limitations

## 🛠️ Development

### Adding New Question Types
1. Update `question_words` in `enhanced_qa_engine.py`
2. Add extraction logic in `precise_answer_extractor.py`
3. Update test cases in `test_api.py`

### Enhancing Answer Extraction
1. Modify extraction methods in `PreciseAnswerExtractor` class
2. Add new pattern recognition logic
3. Update logging to track new extraction types

### Custom Logging
1. Extend `APILogger` class in `logger_service.py`
2. Add new log types or formats
3. Update log analysis endpoints

## 🚨 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid question format or parameters
- **422 Unprocessable Entity**: Request validation failures
- **500 Internal Server Error**: Processing errors with helpful messages
- **Rate Limiting**: Graceful handling of API rate limits

All errors are logged with full context for debugging.

## 🔒 Security Considerations

- **Input Validation**: All inputs are validated and sanitized
- **Error Information**: Error messages don't expose sensitive system details
- **CORS Configuration**: Configured for appropriate cross-origin access
- **Logging Privacy**: Personal message content is handled responsibly

## 📚 API Usage Examples

### Python
```python
import requests

response = requests.post("http://localhost:8000/ask", 
                        json={"question": "When is Sophia going to Paris?"})
data = response.json()
print(f"Answer: {data['answer']}")
```

### JavaScript
```javascript
fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: "What restaurant did Fatima book?"})
})
.then(response => response.json())
.then(data => console.log('Answer:', data.answer));
```

### cURL
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "How many tickets does Armand need?"}'
```

## 🎯 Best Practices

### Question Formulation
- ✅ Use specific names: "Sophia Al-Farsi" instead of "Sophia"
- ✅ Include context: "trip to Paris" instead of just "trip"
- ✅ Ask one thing at a time for clarity
- ✅ Use proper capitalization for names and places

### API Usage
- ✅ Handle errors gracefully in your application
- ✅ Respect rate limits and processing times
- ✅ Use appropriate timeouts for requests
- ✅ Cache results when appropriate for your use case

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Update documentation as needed
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the `/examples` endpoint for usage guidance
- Review logs in the `logs/` directory
- Use the `/health` endpoint to verify system status
- Check the interactive documentation at `/docs`
