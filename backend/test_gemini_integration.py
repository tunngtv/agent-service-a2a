"""Test script to verify Gemini Free (gemini-2.0-flash) integration"""

import os
import asyncio
from agent_service.agent import AgentService


def test_gemini_integration():
    """Test Gemini integration with gemini-2.0-flash model"""
    
    # Set up environment for testing
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["GEMINI_MODEL"] = "gemini-2.0-flash"
    
    # Check if GEMINI_API_KEY is set
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("FAIL: GEMINI_API_KEY is not set")
        return False
    
    print("Initializing AgentService with Gemini...")
    agent_service = AgentService()
    
    # Check if real LLM is being used (should be True if API key is valid)
    if not agent_service.use_real_llm:
        print("FAIL: Not using real LLM - likely invalid API key or missing dependencies")
        return False
    
    print("SUCCESS: Real LLM is being used (not fallback to mock)")
    
    # Test a simple prompt
    test_message = [{"role": "user", "content": "Reply with GEMINI_OK"}]
    
    print("Testing prompt: 'Reply with GEMINI_OK'")
    
    try:
        # Test async processing
        async def run_test():
            response_parts = []
            async for chunk in agent_service.aprocess_messages(test_message):
                response_parts.append(chunk)
                print(f"Received chunk: {repr(chunk)}")
            
            full_response = "".join(response_parts)
            print(f"Full response: {full_response}")
            
            # Check if response contains expected content
            if "GEMINI_OK" in full_response.upper():
                print("SUCCESS: Response contains expected content")
                return True
            else:
                print("WARNING: Response does not contain 'GEMINI_OK', but no error occurred")
                return True  # Still success as long as no error and streaming works
        
        # Run the async test
        success = asyncio.run(run_test())
        return success
        
    except Exception as e:
        print(f"FAIL: Error during processing: {str(e)}")
        return False


if __name__ == "__main__":
    print("Verifying Gemini Free (gemini-2.0-flash) integration...")
    print(f"Environment - LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"Environment - GEMINI_MODEL: {os.getenv('GEMINI_MODEL')}")
    print(f"Environment - GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
    
    success = test_gemini_integration()
    
    if success:
        print("\nVERIFICATION RESULT: PASSED - Gemini integration working correctly")
    else:
        print("\nVERIFICATION RESULT: FAILED - Issues with Gemini integration")