import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_subheader(title: str):
    """Print a formatted subheader"""
    print(f"\n📋 {title}")
    print("-" * 40)

def print_response(response, show_full_response=False):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if show_full_response:
                print("Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                # Show key fields for Q&A responses
                if "answer" in data:
                    print(f"✅ Answer: {data['answer']}")
                    print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                    print(f"🔍 Messages Searched: {data.get('messages_searched', 'N/A')}")
                    print(f"🎯 Question Type: {data.get('question_type', 'N/A')}")
                    print(f"👥 Target Entities: {data.get('target_entities', 'N/A')}")
                    print(f"⏱️ Processing Time: {data.get('processing_time_ms', 'N/A')}ms")
                else:
                    print("Response:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"Non-JSON Response: {response.text[:200]}...")
    else:
        print(f"❌ Error Response: {response.text}")

def test_basic_endpoints():
    """Test basic API endpoints"""
    
    print_header("Testing Basic API Endpoints")
    
    # Test root endpoint
    print_subheader("1. Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test health endpoint
    print_subheader("2. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test stats endpoint
    print_subheader("3. System Statistics")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=TIMEOUT)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test logs endpoint
    print_subheader("4. Log Statistics")
    try:
        response = requests.get(f"{BASE_URL}/logs", timeout=TIMEOUT)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test examples endpoint
    print_subheader("5. Examples")
    try:
        response = requests.get(f"{BASE_URL}/examples", timeout=TIMEOUT)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_question_answering():
    """Test the main question-answering functionality"""
    
    print_header("Testing Enhanced Question-Answering Engine")
    
    # Comprehensive test questions covering different types
    test_questions = [
        {
            "question": "When is Sophia planning her trip to Paris?",
            "type": "temporal",
            "description": "Testing time-based question extraction"
        },
        {
            "question": "How many people does Fatima need dinner for?",
            "type": "quantity",
            "description": "Testing quantity extraction"
        },
        {
            "question": "What restaurant did Fatima book?",
            "type": "entity",
            "description": "Testing restaurant name extraction"
        },
        {
            "question": "Where is Armand going for the opera?",
            "type": "location", 
            "description": "Testing location extraction"
        },
        {
            "question": "Who booked a private jet?",
            "type": "person",
            "description": "Testing person identification"
        },
        {
            "question": "What time is Sophia's flight to Paris?",
            "type": "temporal_specific",
            "description": "Testing specific time extraction"
        },
        {
            "question": "How many tickets does Armand need?",
            "type": "quantity_specific", 
            "description": "Testing specific quantity extraction"
        }
    ]
    
    print(f"Running {len(test_questions)} comprehensive test questions...")
    
    for i, test_case in enumerate(test_questions, 1):
        print_subheader(f"{i}. {test_case['type'].upper()}: {test_case['description']}")
        print(f"❓ Question: {test_case['question']}")
        
        start_time = time.time()
        
        try:
            # Test POST endpoint
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": test_case['question']},
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            
            end_time = time.time()
            request_time = (end_time - start_time) * 1000
            
            print(f"🕐 Request Time: {request_time:.2f}ms")
            print_response(response)
            
            # Brief pause between requests
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_get_endpoint():
    """Test GET endpoint for questions"""
    
    print_header("Testing GET Endpoint")
    
    test_questions_get = [
        "When is Sophia going to Paris?",
        "What restaurant did Fatima mention?",
        "Who needs opera tickets?"
    ]
    
    for i, question in enumerate(test_questions_get, 1):
        print_subheader(f"{i}. GET Request Test")
        print(f"❓ Question: {question}")
        
        try:
            # URL encode the question
            import urllib.parse
            encoded_question = urllib.parse.quote(question)
            
            response = requests.get(f"{BASE_URL}/ask?question={encoded_question}", timeout=TIMEOUT)
            print_response(response)
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_error_handling():
    """Test error handling and edge cases"""
    
    print_header("Testing Error Handling & Edge Cases")
    
    # Test cases for error handling
    error_test_cases = [
        {
            "name": "Empty Question",
            "data": {"question": ""},
            "expected_status": 400
        },
        {
            "name": "Very Short Question", 
            "data": {"question": "Hi"},
            "expected_status": 400
        },
        {
            "name": "Very Long Question",
            "data": {"question": "A" * 600},  # Over 500 char limit
            "expected_status": 400
        },
        {
            "name": "Missing Question Field",
            "data": {"not_question": "test"},
            "expected_status": 422
        },
        {
            "name": "Invalid JSON Structure",
            "data": "invalid json",
            "expected_status": 422
        }
    ]
    
    for i, test_case in enumerate(error_test_cases, 1):
        print_subheader(f"{i}. {test_case['name']}")
        
        try:
            if isinstance(test_case['data'], str):
                # Test invalid JSON
                response = requests.post(
                    f"{BASE_URL}/ask",
                    data=test_case['data'],
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
            else:
                response = requests.post(
                    f"{BASE_URL}/ask",
                    json=test_case['data'],
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
            
            print(f"Expected Status: {test_case['expected_status']}")
            print(f"Actual Status: {response.status_code}")
            
            if response.status_code == test_case['expected_status']:
                print("✅ Error handling working correctly")
            else:
                print("⚠️ Unexpected status code")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"Error Message: {error_data.get('detail', 'No detail provided')}")
                except:
                    print(f"Error Text: {response.text[:200]}")
            
        except Exception as e:
            print(f"❌ Request Error: {e}")

def test_performance():
    """Test API performance with multiple requests"""
    
    print_header("Testing API Performance")
    
    # Performance test question
    perf_question = "What did Sophia book?"
    num_requests = 5
    
    print(f"Running {num_requests} consecutive requests to test performance...")
    print(f"Question: {perf_question}")
    
    response_times = []
    successful_requests = 0
    
    for i in range(num_requests):
        print(f"\n🔄 Request {i+1}/{num_requests}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": perf_question},
                headers={"Content-Type": "application/json"},
                timeout=TIMEOUT
            )
            
            end_time = time.time()
            request_time = (end_time - start_time) * 1000
            response_times.append(request_time)
            
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Success - {request_time:.2f}ms")
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(0.2)
    
    # Performance summary
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 Performance Summary:")
        print(f"   Successful Requests: {successful_requests}/{num_requests}")
        print(f"   Average Response Time: {avg_time:.2f}ms")
        print(f"   Fastest Response: {min_time:.2f}ms")
        print(f"   Slowest Response: {max_time:.2f}ms")
        print(f"   Success Rate: {(successful_requests/num_requests)*100:.1f}%")

def main():
    """Main test runner"""
    
    print("🚀 Aurora Enhanced Q&A API - Comprehensive Test Suite")
    print(f"🎯 Target: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all test suites
        test_basic_endpoints()
        test_question_answering()
        test_get_endpoint()
        test_error_handling()
        test_performance()
        
        print_header("🎉 Test Suite Completed Successfully!")
        print("✅ All tests have been executed")
        print("📋 Check the console output above for detailed results")
        print("📊 Check the API logs for comprehensive logging details")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")

if __name__ == "__main__":
    main()