#!/usr/bin/env python3
"""
Test script to verify the fitness studio agent system functionality.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config.settings import get_settings
from app.models.database import DatabaseManager
from app.agents.crew_manager import CrewManager


async def test_configuration():
    """Test basic configuration."""
    print("🔧 Testing Configuration...")
    
    settings = get_settings()
    print(f"✓ Database: {settings.database_name}")
    print(f"✓ OpenAI Model: {settings.openai_model}")
    
    # Check if API key is configured
    if not settings.openai_api_key or settings.openai_api_key == "sk-your-openai-api-key-here":
        print("❌ OpenAI API key not configured!")
        print("   Please set OPENAI_API_KEY in your .env file")
        return False
    else:
        print("✓ OpenAI API key configured")
    
    return True


async def test_database_connection():
    """Test database connection."""
    print("\n🗄️  Testing Database Connection...")
    
    try:
        # Test async connection
        await DatabaseManager.connect_to_mongo()
        print("✓ Async MongoDB connection successful")
        
        # Test sync connection
        DatabaseManager.connect_to_mongo_sync()
        print("✓ Sync MongoDB connection successful")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_agent_initialization():
    """Test agent initialization."""
    print("\n🤖 Testing Agent Initialization...")
    
    try:
        crew_manager = CrewManager()
        print("✓ CrewManager initialized successfully")
        print(f"✓ Support Agent: {crew_manager.support_agent.role}")
        print(f"✓ Dashboard Agent: {crew_manager.dashboard_agent.role}")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🏋️ Fitness Studio Agent System - Test Suite")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_database_connection,
        test_agent_initialization,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    # Cleanup
    if DatabaseManager.client:
        await DatabaseManager.close_mongo_connection()
    if DatabaseManager.sync_client:
        DatabaseManager.close_mongo_connection_sync()


if __name__ == "__main__":
    asyncio.run(main())
