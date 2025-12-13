"""Direct chat test."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test message
message = "Find Data Engineer jobs from top companies in the last 30 days"
print(f"Testing message: '{message}'")
print()

payload = {"message": message}
r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)

print(f"Status: {r.status_code}")
result = r.json()
print(f"Response: {result.get('response', '')}")
print(f"Tool calls: {result.get('tool_calls')}")
print(f"Conversation ID: {result.get('conversation_id')}")


