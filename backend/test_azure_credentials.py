"""Test script to verify Azure OpenAI credentials are working."""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from backend directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

try:
    from openai import AzureOpenAI
except ImportError:
    print("[ERROR] openai package not installed. Run: pip install openai")
    sys.exit(1)

def test_azure_credentials():
    """Test Azure OpenAI connection with a simple API call."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("API_VERSION")
    
    # Check if all required env vars are present
    if not endpoint:
        print("[ERROR] AZURE_OPENAI_ENDPOINT not found in .env file")
        return False
    if not api_key:
        print("[ERROR] AZURE_OPENAI_API_KEY not found in .env file")
        return False
    if not api_version:
        print("[ERROR] API_VERSION not found in .env file")
        return False
    
    print(f"Testing Azure OpenAI connection...")
    print(f"Endpoint: {endpoint}")
    print(f"API Version: {api_version}")
    print(f"Model: gpt-4o")
    print()
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50
        )
        
        print("[SUCCESS] Azure OpenAI credentials work!")
        response_text = response.choices[0].message.content
        # Handle potential Unicode issues in Windows console
        try:
            print(f"Response: {response_text}")
        except UnicodeEncodeError:
            print(f"Response: {response_text.encode('ascii', 'ignore').decode('ascii')}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error connecting to Azure OpenAI: {str(e)}")
        print("\nPlease check:")
        print("1. AZURE_OPENAI_ENDPOINT is correct")
        print("2. AZURE_OPENAI_API_KEY is valid and not expired")
        print("3. API_VERSION is correct (2024-12-01-preview)")
        print("4. Model 'gpt-4o' is deployed in your Azure OpenAI resource")
        return False

if __name__ == "__main__":
    success = test_azure_credentials()
    sys.exit(0 if success else 1)

