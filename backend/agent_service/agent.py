from typing import List, Dict, Any, Generator, AsyncGenerator
import os
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


class AgentService:
    """
    Single root Agent Service using LangChain
    Implements token streaming for SSE
    """
    
    def __init__(self):
        # Check if we can import the OpenAI module
        try:
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY", "mock-key")
            if api_key == "mock-key":
                print("Warning: OPENAI_API_KEY not set, using mock responses")
            
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=api_key
            )
            self.use_real_llm = True
        except ImportError:
            print("Warning: langchain-openai not available, using mock responses")
            self.use_real_llm = False
    
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
    
    async def aprocess_messages(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Async version for processing messages
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
                async for chunk in self._simulate_token_streaming_async(response_text):
                    yield chunk
            except Exception as e:
                # Fallback to mock response if real LLM fails
                response_text = f"Mock response: {self._generate_mock_response(user_input)}"
                async for chunk in self._simulate_token_streaming_async(response_text):
                    yield chunk
        else:
            # Use mock response
            response_text = self._generate_mock_response(user_input)
            async for chunk in self._simulate_token_streaming_async(response_text):
                yield chunk