#!/usr/bin/env python3
"""
Test script to verify the app works correctly before deployment.
Run this before deploying to Railway.
"""

import os
import sys
import requests
import time
from app import app

def test_app():
    """Test the Flask app locally."""
    print("🧪 Testing Thai Tone Analyzer App...")
    print("=" * 50)
    
    # Test 1: App starts without errors
    print("1. Testing app startup...")
    try:
        with app.test_client() as client:
            print("   ✅ App starts successfully")
    except Exception as e:
        print(f"   ❌ App startup failed: {e}")
        return False
    
    # Test 2: Main page loads
    print("2. Testing main page...")
    try:
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Main page loads successfully")
            else:
                print(f"   ❌ Main page failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Main page test failed: {e}")
        return False
    
    # Test 3: Analyze endpoint
    print("3. Testing analyze endpoint...")
    try:
        with app.test_client() as client:
            # Test Thai word
            response = client.post('/analyze', json={'word': 'มา'})
            if response.status_code == 200:
                data = response.get_json()
                if 'tone' in data:
                    print("   ✅ Thai word analysis works")
                else:
                    print("   ❌ Thai word analysis failed")
                    return False
            else:
                print(f"   ❌ Analyze endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Analyze endpoint test failed: {e}")
        return False
    
    # Test 4: English translation
    print("4. Testing English translation...")
    try:
        with app.test_client() as client:
            response = client.post('/analyze', json={'word': 'hello'})
            if response.status_code == 200:
                data = response.get_json()
                if 'translation' in data:
                    print("   ✅ English translation works")
                else:
                    print("   ❌ English translation failed")
                    return False
            else:
                print(f"   ❌ Translation test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Translation test failed: {e}")
        return False
    
    # Test 5: Connectivity check
    print("5. Testing connectivity check...")
    try:
        with app.test_client() as client:
            response = client.get('/connectivity')
            if response.status_code == 200:
                data = response.get_json()
                if 'online' in data:
                    print("   ✅ Connectivity check works")
                else:
                    print("   ❌ Connectivity check failed")
                    return False
            else:
                print(f"   ❌ Connectivity check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Connectivity check test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! App is ready for deployment.")
    return True

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1)
