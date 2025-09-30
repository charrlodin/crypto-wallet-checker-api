"""
Test script for the Crypto Wallet Checker API
"""
import sys
import json
sys.path.insert(0, '.')

from main import app, startup_event
from fastapi.testclient import TestClient
import asyncio

# Run startup
asyncio.run(startup_event())

# Create test client
client = TestClient(app)

print("\n" + "="*60)
print("TESTING CRYPTO WALLET CHECKER API")
print("="*60)

# Test 1: Root endpoint
print("\n1. Testing root endpoint...")
response = client.get("/")
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Tornado Cash address (sanctioned)
print("\n2. Testing Tornado Cash address (should be flagged)...")
response = client.post("/wallet/check", json={
    "chain": "ethereum",
    "address": "0x722122df12d4e14e13ac3b6895a86e84145b6967"
})
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Address: {result['address']}")
print(f"   Scam Flag: {result['scam_flag']}")
print(f"   Risk Score: {result['risk_score']}")
print(f"   Label: {result['label']}")
print(f"   Reasons: {result['reasons']}")

# Test 3: Known scam address
print("\n3. Testing known scam address (PlusToken)...")
response = client.post("/wallet/check", json={
    "chain": "ethereum",
    "address": "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b"
})
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Address: {result['address']}")
print(f"   Scam Flag: {result['scam_flag']}")
print(f"   Risk Score: {result['risk_score']}")
print(f"   Label: {result['label']}")
print(f"   Reasons: {result['reasons']}")

# Test 4: Clean address (random but valid format)
print("\n4. Testing clean address...")
response = client.post("/wallet/check", json={
    "chain": "ethereum",
    "address": "0x1234567890123456789012345678901234567890"
})
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Address: {result['address']}")
print(f"   Scam Flag: {result['scam_flag']}")
print(f"   Risk Score: {result['risk_score']}")
print(f"   Label: {result['label']}")
print(f"   Reasons: {result['reasons']}")

# Test 5: With phishing domain
print("\n5. Testing with phishing domain...")
response = client.post("/wallet/check", json={
    "chain": "ethereum",
    "address": "0x1234567890123456789012345678901234567890",
    "domain": "metamask-secure.com"
})
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Risk Score: {result['risk_score']}")
print(f"   Label: {result['label']}")
print(f"   Reasons: {result['reasons']}")

# Test 6: Status endpoint
print("\n6. Testing status endpoint...")
response = client.get("/status")
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   API Status: {result['status']}")
print(f"   Version: {result['version']}")
print(f"   Data Sources:")
for key, value in result['data_sources'].items():
    if isinstance(value, dict):
        print(f"     {key}: {value}")
    else:
        print(f"     {key}: {value}")

# Test 7: Invalid address
print("\n7. Testing invalid address (should error)...")
response = client.post("/wallet/check", json={
    "chain": "ethereum",
    "address": "invalid"
})
print(f"   Status: {response.status_code}")
print(f"   Error: {response.json()['detail']}")

# Test 8: Bitcoin address
print("\n8. Testing Bitcoin address...")
response = client.post("/wallet/check", json={
    "chain": "bitcoin",
    "address": "1Jn9fT5LqWNqnMWwXBSfXPpAbvfNZRJqJv"
})
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Address: {result['address']}")
print(f"   Scam Flag: {result['scam_flag']}")
print(f"   Risk Score: {result['risk_score']}")
print(f"   Label: {result['label']}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60 + "\n")
