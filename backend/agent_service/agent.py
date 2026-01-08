from typing import List, Dict, Any, Generator, AsyncGenerator
import os
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is not installed, skip loading
    pass


class AgentService:
    """
    Single root Agent Service using LangChain
    Implements token streaming for SSE
    """
    
    def __init__(self):
        import os
        
        # Determine LLM provider based on environment and available keys
        llm_provider = self._detect_llm_provider()
        
        # Initialize conversation storage
        self.conversations = {}
        
        if llm_provider == "openai":
            # Check if we can import the OpenAI module
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError("langchain-openai package is required for OpenAI provider. Install with: pip install langchain-openai")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required when LLM_PROVIDER=openai")
            
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.7,
                api_key=api_key
            )
            self.use_real_llm = True
            print(f"Initialized OpenAI provider with model: {model}")
        
        elif llm_provider == "gemini":
            # Check if we can import the Google GenAI module
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                raise ImportError("langchain-google-genai package is required for Gemini provider. Install with: pip install langchain-google-genai")
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required when LLM_PROVIDER=gemini")
            
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=0.7,
                google_api_key=api_key
            )
            self.use_real_llm = True
            print(f"Initialized Gemini provider with model: {model}")
        
        elif llm_provider == "mock":
            # Force mock mode
            self.use_real_llm = False
            print("Initialized mock provider")
        
        else:
            # This should not happen if _detect_llm_provider is implemented correctly
            raise ValueError(f"Unknown LLM provider: {llm_provider}")

    def _detect_llm_provider(self):
        import os
        
        # Check if LLM_PROVIDER is explicitly set
        explicit_provider = os.getenv("LLM_PROVIDER", "").lower()
        print(f"DEBUG: LLM_PROVIDER environment variable = '{explicit_provider}'")
        
        if explicit_provider:
            if explicit_provider in ["openai", "gemini", "mock"]:
                print(f"DEBUG: Using explicit provider: {explicit_provider}")
                return explicit_provider
            else:
                raise ValueError(f"Invalid LLM_PROVIDER: {explicit_provider}. Supported values: openai, gemini, mock")
        
        # If no explicit provider, auto-detect based on available API keys
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        print(f"DEBUG: GEMINI_API_KEY exists: {bool(gemini_key)}")
        print(f"DEBUG: OPENAI_API_KEY exists: {bool(openai_key)}")
        
        if gemini_key:
            print("Auto-detecting provider: gemini (GEMINI_API_KEY found)")
            return "gemini"
        elif openai_key:
            print("Auto-detecting provider: openai (OPENAI_API_KEY found)")
            return "openai"
        else:
            print("No API keys found, defaulting to mock provider")
            return "mock"
    
    def reset_conversation(self, conversation_id: str = "default"):
        """Reset a specific conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_conversation_history(self, conversation_id: str = "default"):
        """Get conversation history for a specific conversation"""
        return self.conversations.get(conversation_id, [])
    
    def update_conversation_history(self, conversation_id: str, messages: List[Dict[str, str]]):
        """Update conversation history"""
        self.conversations[conversation_id] = messages
    
    def _generate_mock_response(self, user_input: str) -> str:
        """Generate a mock response based on user input"""
        responses = [
            f"I understand you're asking about '{user_input}'. This is a simulated response from the AI assistant.",
            f"Thanks for your message: '{user_input}'. How can I assist you further?",
            f"Regarding '{user_input}', I'm an AI assistant designed to help with various queries.",
            f"I've processed your input '{user_input}' and generated this helpful response.",
            f"That's an interesting point about '{user_input}'. Here's what I think..."
        ]
        return random.choice(responses)
    
    def _simulate_token_streaming(self, response_text: str) -> Generator[str, None, None]:
        """Simulate token streaming by breaking response into chunks"""
        # Break the response into words and yield them one by one with small delays
        words = response_text.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            # Add a small delay to simulate streaming
            time.sleep(0.02)
    
    async def _simulate_token_streaming_async(self, response_text: str) -> AsyncGenerator[str, None]:
        """Async version to simulate token streaming by breaking response into chunks"""
        # Break the response into words and yield them one by one with small delays
        words = response_text.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            # Add a small async delay to simulate streaming
            await asyncio.sleep(0.02)
    
    def process_messages(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Process a list of messages and yield token deltas for SSE streaming
        """
        # Get the latest user message as input
        if messages and messages[-1]["role"] == "user":
            user_input = messages[-1]["content"]
        else:
            user_input = "Hello"  # Default input if no user message is provided
        
        if self.use_real_llm:
            # Use real LLM if available
            try:
                from langchain_core.messages import HumanMessage
                from langchain_core.prompts import ChatPromptTemplate
                
                # Create a simple prompt
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful AI assistant. Respond concisely and accurately."),
                    ("human", "{input}")
                ])
                
                chain = prompt | self.llm
                response = chain.invoke({"input": user_input})
                
                # Simulate token streaming by breaking the response into chunks
                response_text = response.content if hasattr(response, 'content') else str(response)
                yield from self._simulate_token_streaming(response_text)
            except Exception as e:
                # Fallback to mock response if real LLM fails
                response_text = f"Mock response: {self._generate_mock_response(user_input)}"
                yield from self._simulate_token_streaming(response_text)
        else:
            # Use mock response
            response_text = self._generate_mock_response(user_input)
            yield from self._simulate_token_streaming(response_text)
    
    async def aprocess_messages(self, messages: List[Dict[str, str]], conversation_id: str = "default") -> AsyncGenerator[str, None]:
        """
        Async version for processing messages
        """
        # Get existing conversation history
        history = self.get_conversation_history(conversation_id)
        
        # Combine history with new messages
        all_messages = history + messages
        
        # Get the latest user message as input
        if messages and messages[-1]["role"] == "user":
            user_input = messages[-1]["content"]
        else:
            user_input = "Hello"  # Default input if no user message is provided
        
        if self.use_real_llm:
            # Use real LLM if available
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                from langchain_core.prompts import ChatPromptTemplate
                
                # Create a prompt with conversation history
                formatted_messages = []
                formatted_messages.append(("system", "You are a helpful AI assistant. Respond concisely and accurately."))
                
                # Add conversation history
                for msg in all_messages:
                    role = msg["role"]
                    content = msg["content"]
                    formatted_messages.append((role, content))
                
                prompt = ChatPromptTemplate.from_messages(formatted_messages)
                
                chain = prompt | self.llm
                response = chain.invoke({})
                
                # Simulate token streaming by breaking the response into chunks
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Update conversation history after response
                self.update_conversation_history(conversation_id, all_messages + [{"role": "assistant", "content": response_text}])
                
                async for chunk in self._simulate_token_streaming_async(response_text):
                    yield chunk
            except Exception as e:
                # Fallback to mock response if real LLM fails
                response_text = f"Mock response: {self._generate_mock_response(user_input)}"
                
                # Update conversation history after response
                self.update_conversation_history(conversation_id, all_messages + [{"role": "assistant", "content": response_text}])
                
                async for chunk in self._simulate_token_streaming_async(response_text):
                    yield chunk
        else:
            # Use mock response
            response_text = self._generate_mock_response(user_input)
            
            # Update conversation history after response
            self.update_conversation_history(conversation_id, all_messages + [{"role": "assistant", "content": response_text}])
            
            async for chunk in self._simulate_token_streaming_async(response_text):
                yield chunk