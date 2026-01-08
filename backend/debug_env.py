"""Debug script to check environment variables and provider detection"""

import os
from agent_service.agent import AgentService

def debug_environment():
    print("=== Environment Debug ===")
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"GEMINI_MODEL: {os.getenv('GEMINI_MODEL')}")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
    
    print("\n=== Creating AgentService ===")
    try:
        agent = AgentService()
        print(f"use_real_llm: {agent.use_real_llm}")
        if hasattr(agent, 'llm'):
            print(f"LLM type: {type(agent.llm)}")
    except Exception as e:
        print(f"Error creating AgentService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_environment()