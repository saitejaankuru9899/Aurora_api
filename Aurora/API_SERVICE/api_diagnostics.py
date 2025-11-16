import httpx
import asyncio
import json

async def diagnose_api():
    """Diagnose the Aurora API to understand its structure and endpoints"""
    
    base_url = "https://november7-730026606190.europe-west1.run.app"
    endpoints_to_test = [
        "/",
        "/docs",
        "/openapi.json", 
        "/messages",
        "/messages/",
    ]
    
    print("🔍 Aurora API Diagnostics")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Testing: {url}")
            
            try:
                response = await client.get(url)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'application/json' in content_type:
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                print(f"   Response: JSON Array with {len(data)} items")
                                if data:
                                    print(f"   Sample item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                            elif isinstance(data, dict):
                                print(f"   Response: JSON Object with keys: {list(data.keys())}")
                            else:
                                print(f"   Response: JSON {type(data).__name__}")
                        except json.JSONDecodeError:
                            print("   Response: Invalid JSON")
                    else:
                        text = response.text[:200]
                        print(f"   Response: {content_type}")
                        print(f"   Content preview: {text}...")
                        
                elif response.status_code in [301, 302, 307, 308]:
                    location = response.headers.get('location', 'No location header')
                    print(f"   Redirect to: {location}")
                else:
                    print(f"   Error response: {response.text[:200]}")
                    
            except httpx.TimeoutException:
                print("   ❌ Request timed out")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Also test with different HTTP methods
    print(f"\n📡 Testing different HTTP methods on /messages")
    methods_to_test = ['GET', 'POST', 'OPTIONS']
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for method in methods_to_test:
            try:
                response = await client.request(method, f"{base_url}/messages")
                print(f"   {method}: {response.status_code}")
                if response.status_code == 200 and method == 'GET':
                    try:
                        data = response.json()
                        print(f"   GET Success! Found {len(data)} messages")
                        if data:
                            print(f"   Sample message: {json.dumps(data[0], indent=4)}")
                        break
                    except:
                        print(f"   GET Success but not JSON: {response.text[:100]}")
            except Exception as e:
                print(f"   {method}: Error - {e}")

async def test_swagger_docs():
    """Try to access the Swagger documentation directly"""
    
    print("\n" + "=" * 60)
    print("📚 Testing Swagger Documentation")
    print("=" * 60)
    
    base_url = "https://november7-730026606190.europe-west1.run.app"
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # Try to get the OpenAPI spec
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                spec = response.json()
                print("✅ Found OpenAPI specification!")
                
                # Extract paths information
                if 'paths' in spec:
                    print("\n📍 Available endpoints:")
                    for path, methods in spec['paths'].items():
                        for method, details in methods.items():
                            summary = details.get('summary', 'No summary')
                            print(f"   {method.upper()} {path}: {summary}")
                
                # Look for messages endpoint specifically
                if '/messages' in spec.get('paths', {}):
                    messages_spec = spec['paths']['/messages']
                    print(f"\n📝 Messages endpoint details:")
                    print(json.dumps(messages_spec, indent=2))
                
            else:
                print(f"❌ Could not access OpenAPI spec: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error accessing OpenAPI spec: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_api())
    asyncio.run(test_swagger_docs())