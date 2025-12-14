"""End-to-end test script."""
import requests
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_pdf_upload():
    """Test PDF upload."""
    print("\n=== Testing PDF Upload ===")
    pdf_path = Path(__file__).parent / "test_data" / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
    
    if not pdf_path.exists():
        print(f"ERROR: PDF file not found at {pdf_path}")
        return None
    
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/pdf", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Document ID: {result['document_id']}")
        print(f"Status: {result['topic_extract_status']}")
        return result['document_id']
    else:
        print(f"Error: {response.text}")
        return None

def test_chat_search(conversation_id=None):
    """Test chat with search request."""
    print("\n=== Testing Chat Search ===")
    payload = {
        "message": "Find Data Engineer and Database Administrator jobs from top companies in the last 30 days in the US",
        "conversation_id": conversation_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response']}")
        print(f"Conversation ID: {result['conversation_id']}")
        return result['conversation_id']
    else:
        print(f"Error: {response.text}")
        return conversation_id

def test_chat_analyze(document_id, conversation_id):
    """Test chat with analyze request."""
    print("\n=== Testing Chat Analyze ===")
    payload = {
        "message": "Now analyze the syllabus topics against the job descriptions and show me the gaps",
        "conversation_id": conversation_id,
        "document_id": document_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response']}")
        if result.get('tables'):
            table_a_count = len(result['tables'].get('table_a', []))
            table_b_count = len(result['tables'].get('table_b', []))
            print(f"Table A rows: {table_a_count}")
            print(f"Table B rows: {table_b_count}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("Starting end-to-end test...")
    print(f"Base URL: {BASE_URL}")
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                break
        except:
            time.sleep(1)
            print(f"Waiting... ({i+1}/10)")
    else:
        print("ERROR: Server not responding")
        exit(1)
    
    # Test flow
    document_id = test_pdf_upload()
    if not document_id:
        print("PDF upload failed, exiting")
        exit(1)
    
    time.sleep(2)  # Wait for topic extraction
    
    conversation_id = test_chat_search()
    if not conversation_id:
        print("Chat search failed")
        exit(1)
    
    time.sleep(5)  # Wait for search to complete
    
    success = test_chat_analyze(document_id, conversation_id)
    if success:
        print("\n=== All tests passed! ===")
    else:
        print("\n=== Some tests failed ===")
        exit(1)


