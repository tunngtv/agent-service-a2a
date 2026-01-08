"""Detailed test to check LLM provider and response with error handling"""

import os
from agent_service.agent import AgentService
import asyncio
import traceback


def check_configuration():
    print("=== Current LLM Configuration ===")
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"GEMINI_MODEL: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
    
    print("\n=== Creating AgentService ===")
    try:
        agent = AgentService()
        print(f"use_real_llm: {agent.use_real_llm}")
        print(f"LLM type: {type(agent.llm).__name__}")
        
        # Check if it's actually using the real LLM or falling back somewhere
        print(f"Agent LLM object: {agent.llm}")
        
        return agent
    except Exception as e:
        print(f"Error creating AgentService: {e}")
        traceback.print_exc()
        return None


async def test_response_detailed(agent_service):
    if not agent_service:
        print("\n❌ Cannot test - AgentService not created successfully")
        return
    
    print("\n=== Detailed Response Test ===")
    test_messages = [{"role": "user", "content": "Hello, this is a test. Reply with GEMINI_TEST_OK"}]
    
    try:
        print("Sending test message: 'Hello, this is a test. Reply with GEMINI_TEST_OK'")
        
        # Test the internal logic directly
        print(f"Agent use_real_llm: {agent_service.use_real_llm}")
        
        response_parts = []
        
        # Access the aprocess_messages method to see what happens
        async for chunk in agent_service.aprocess_messages(test_messages):
            response_parts.append(chunk)
            print(f"Chunk received: {repr(chunk)}")
        
        full_response = "".join(response_parts)
        print(f"\nFull response: {full_response}")
        
        if "GEMINI_TEST_OK" in full_response.upper():
            print("✅ Response contains expected content - using real LLM")
        elif "mock" in full_response.lower():
            print("⚠️ Response contains 'mock' - falling back to mock despite real LLM initialization")
        else:
            print(f"ℹ️ Response received but doesn't contain expected content: {full_response[:100]}...")
        
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error during response test: {e}")
        traceback.print_exc()


async def test_direct_llm_call(agent_service):
    """Test calling the LLM directly to see if there are API issues"""
    if not agent_service or not agent_service.use_real_llm:
        print("\n❌ Cannot test direct LLM call - real LLM not available")
        return
    
    print("\n=== Direct LLM Call Test ===")
    try:
        from langchain_core.messages import HumanMessage
        
        # Create a simple message
        message = HumanMessage(content="Test message - reply with DIRECT_CALL_OK")
        
        print("Making direct call to LLM...")
        response = agent_service.llm.invoke([message])
        print(f"Direct response: {response}")
        print("✅ Direct LLM call successful")
        
    except Exception as e:
        print(f"❌ Direct LLM call failed: {e}")
        traceback.print_exc()


async def main():
    agent = check_configuration()
    await test_response_detailed(agent)
    await test_direct_llm_call(agent)


if __name__ == "__main__":
    asyncio.run(main())