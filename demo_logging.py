#!/usr/bin/env python3
"""
Demo script to showcase the enhanced logging and observability features
of the Weather Agent.

Run this script to see how the agent logs its thought processes, tool calls,
and decision-making in real-time.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.agent_service import WeatherAgentService

async def demo_agent_logging():
    """Demonstrate the agent's logging capabilities"""
    
    print("🤖 Weather Agent Logging Demo")
    print("=" * 50)
    print("This demo shows the agent's internal thought process and tool calls.")
    print("Watch the logs to see how the agent makes decisions!\n")
    
    # Initialize the agent
    agent = WeatherAgentService()
    
    # Test queries that will trigger different behaviors
    test_queries = [
        {
            "query": "What's the weather in Paris?",
            "description": "Current weather query - should call weather API"
        },
        {
            "query": "Will it rain tomorrow in London?", 
            "description": "Forecast query - should call forecast API"
        },
        {
            "query": "¿Qué tiempo hace en Madrid?",
            "description": "Spanish query - should detect language and respond in Spanish"
        },
        {
            "query": "Hello, how are you today?",
            "description": "Non-weather query - should not call weather APIs"
        },
        {
            "query": "What's the weather like in NonExistentCity12345?",
            "description": "Invalid location - should handle gracefully"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"📝 Query: '{test_case['query']}'")
        print(f"🔍 Watch the logs below to see the agent's reasoning...\n")
        
        try:
            # Process the query - this will generate detailed logs
            result = await agent.process_query(test_case["query"])
            
            print(f"✅ Response: {result.natural_response}")
            print(f"⏱️ Processing time: {result.processing_time_ms:.1f}ms")
            print(f"📊 Weather data included: {result.weather_data is not None}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        
        # Small delay between queries for readability
        await asyncio.sleep(1)
    
    print("\n🎉 Demo completed!")
    print("\nKey logging features demonstrated:")
    print("• 🧠 THINK phase: Query analysis, language detection, action planning")
    print("• ⚡ ACT phase: Tool calls, API requests, success/failure tracking")
    print("• 👁️ OBSERVE phase: Response generation, language matching")
    print("• 🏷️ Request tracking: Unique request IDs for tracing")
    print("• ⏱️ Performance monitoring: Timing for each phase")
    print("• 🔧 Fallback handling: Graceful degradation when services fail")
    
    # Show log file locations
    log_dir = Path("logs")
    if log_dir.exists():
        print(f"\n📁 Log files written to:")
        for log_file in log_dir.glob("*.log*"):
            print(f"   • {log_file}")
    
    print("\n💡 Tips for production monitoring:")
    print("• Set ENVIRONMENT=production for JSON structured logs")
    print("• Set LOG_LEVEL=DEBUG for maximum detail")
    print("• Use log aggregation tools like ELK stack or Datadog")
    print("• Monitor request_id patterns for user journey tracking")

async def demo_production_logging():
    """Show what production logs look like"""
    print("\n🏭 Production Logging Preview")
    print("=" * 50)
    print("Setting ENVIRONMENT=production to show JSON structured logs...\n")
    
    # Temporarily set production environment
    original_env = os.getenv("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "production"
    
    # Re-setup logging to see the difference
    from app.main import setup_logging
    setup_logging()
    
    # Run a quick query to show production logs
    agent = WeatherAgentService()
    await agent.process_query("What's the weather in Tokyo?")
    
    # Restore original environment
    if original_env:
        os.environ["ENVIRONMENT"] = original_env
    else:
        os.environ.pop("ENVIRONMENT", None)
    
    print("\n📋 Production logs are JSON formatted for easy parsing by:")
    print("• Log aggregation systems (ELK, Splunk, Datadog)")
    print("• Monitoring dashboards")
    print("• Automated alerting systems")
    print("• Performance analytics tools")

def main():
    """Main entry point"""
    
    # Set development environment for demo
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    print("Starting Weather Agent Logging Demo...")
    print("Make sure you have your API keys set up!")
    print("(OpenAI and OpenWeatherMap APIs)\n")
    
    try:
        # Run the demo
        asyncio.run(demo_agent_logging())
        
        # Show production logging
        asyncio.run(demo_production_logging())
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure your API keys are configured correctly!")

if __name__ == "__main__":
    main() 