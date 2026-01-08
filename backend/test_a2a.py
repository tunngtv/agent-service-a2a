import asyncio
import json
from typing import Dict, List
import pytest
from fastapi.testclient import TestClient
from server.main import app
from agent_service.agent import AgentService


def test_health_endpoint():
    """Test the health endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_models():
    """Test the models endpoint"""
    client = TestClient(app)
    response = client.get("/a2a/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)


def test_a2a_messages_basic():
    """Test the basic message functionality"""
    client = TestClient(app)
    response = client.post(
        "/a2a/messages",
        json={"messages": [{"role": "user", "content": "Hello, how are you?"}]},
        params={"conversation_id": "test_conversation"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_conversation_state():
    """Test that conversation state is maintained"""
    client = TestClient(app)
    
    # First message
    response1 = client.post(
        "/a2a/messages",
        json={"messages": [{"role": "user", "content": "My name is John."}]},
        params={"conversation_id": "state_test"}
    )
    assert response1.status_code == 200
    
    # Second message that should reference the first
    response2 = client.post(
        "/a2a/messages",
        json={"messages": [{"role": "user", "content": "What is my name?"}]},
        params={"conversation_id": "state_test"}
    )
    assert response2.status_code == 200


def test_reset_conversation():
    """Test resetting conversation functionality"""
    client = TestClient(app)
    
    # Send a message to establish conversation state
    response = client.post(
        "/a2a/messages",
        json={"messages": [{"role": "user", "content": "Remember this."}]},
        params={"conversation_id": "reset_test"}
    )
    assert response.status_code == 200
    
    # Reset the conversation
    reset_response = client.delete("/a2a/conversations/reset_test")
    assert reset_response.status_code == 200
    assert reset_response.json() == {"message": "Conversation reset_test reset successfully"}


def test_agent_service_initialization():
    """Test that AgentService initializes correctly"""
    agent = AgentService()
    assert hasattr(agent, 'conversations')
    assert isinstance(agent.conversations, dict)


def test_agent_service_conversation_management():
    """Test AgentService conversation management methods"""
    agent = AgentService()
    
    # Test initial state
    history = agent.get_conversation_history("test_conv")
    assert history == []
    
    # Add some messages
    test_messages = [{"role": "user", "content": "Hello"}]
    agent.update_conversation_history("test_conv", test_messages)
    
    # Check that history is updated
    history = agent.get_conversation_history("test_conv")
    assert history == test_messages
    
    # Test reset
    agent.reset_conversation("test_conv")
    history = agent.get_conversation_history("test_conv")
    assert history == []


if __name__ == "__main__":
    pytest.main([__file__])