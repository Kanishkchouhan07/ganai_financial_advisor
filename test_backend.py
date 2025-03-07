import requests
import sys
import json

def test_backend(base_url):
    """Test if the backend is running and accessible."""
    print(f"Testing backend at: {base_url}")
    
    # Test endpoints
    endpoints = [
        ("Root", ""),
        ("Health", "/health"),
        ("Test", "/test"),
        ("API", "/api/predict")
    ]
    
    for name, path in endpoints:
        url = f"{base_url}{path}"
        print(f"\nTesting {name} endpoint: {url}")
        
        try:
            if path == "/api/predict":
                # POST request for API endpoint
                response = requests.post(
                    url, 
                    json={"input_data": "Test query"}, 
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
            else:
                # GET request for other endpoints
                response = requests.get(url, timeout=10)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("Response:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter backend base URL (e.g., https://your-backend.onrender.com): ")
    
    # Remove trailing slash if present
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    test_backend(base_url) 