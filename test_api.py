#!/usr/bin/env python3

import requests
import json

def test_api():
    """Test the Huberman Health AI API"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Huberman Health AI API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        print("   Make sure the backend is running: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    # Test search endpoint
    try:
        test_query = {
            "query": "sleep problems",
            "max_results": 2
        }
        
        print(f"\n🔍 Testing search with query: '{test_query['query']}'")
        response = requests.post(f"{base_url}/search", json=test_query, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search endpoint working")
            print(f"   Found {result['total_results']} videos")
            if result['videos']:
                print(f"   Top result: {result['videos'][0]['title']}")
                print(f"   Timestamp: {result['videos'][0].get('timestamp', 'N/A')}")
            if result.get('recommendation'):
                print(f"   AI Recommendation (first 100 chars): {result['recommendation'][:100]}...")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The API is working correctly.")
    return True

if __name__ == "__main__":
    test_api()
