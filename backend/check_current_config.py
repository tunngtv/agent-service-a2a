"""Script to check current LLM provider configuration and test response"""

import os
from agent_service.agent import AgentService
import asyncio


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
        
        if hasattr(agent.llm, 'model') and hasattr(agent.llm, '_llm_type'):
            if 'gemini' in str(type(agent.llm)).lower():
                print(f"Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')} (Gemini)")
            elif 'openai' in str(type(agent.llm)).lower():
                print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')} (OpenAI)")
        else:
            print(f"LLM object: {agent.llm}")
            
        return agent
    except Exception as e:
        print(f"Error creating AgentService: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_response(agent_service):
    if not agent_service:
        print("\n❌ Cannot test - AgentService not created successfully")
        return
    
    print("\n=== Testing Response ===")
    test_messages = [{"role": "user", "content": "Hello, this is a test. Reply with TEST_RESPONSE_OK"}]
    
    try:
        print("Sending test message: 'Hello, this is a test. Reply with TEST_RESPONSE_OK'")
        
        response_parts = []
        async for chunk in agent_service.aprocess_messages(test_messages):
            response_parts.append(chunk)
            print(f"Chunk received: {repr(chunk)}")
        
        full_response = "".join(response_parts)
        print(f"\n✅ Full response: {full_response}")
        
        if "TEST_RESPONSE_OK" in full_response.upper():
            print("✅ Response contains expected content")
        else:
            print("⚠️ Response does not contain 'TEST_RESPONSE_OK' but no error occurred")
        
        print("✅ Test completed successfully - the LLM is responding!")
        
    except Exception as e:
        print(f"❌ Error during response test: {e}")
        import traceback
        traceback.print_exc()


async def main():
    agent = check_configuration()
    await test_response(agent)


if __name__ == "__main__":
    asyncio.run(main())