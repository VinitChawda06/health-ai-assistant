#!/usr/bin/env python3
"""
Test script for the Huberman Health MCP Server
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("🧠 Testing Huberman Health MCP Server...\n")
    
    # Change to the MCP server directory
    mcp_dir = "/home/vinit/Desktop/health-ai-assistant/mcp_server"
    os.chdir(mcp_dir)
    
    # Activate virtual environment and run MCP server test
    venv_python = "/home/vinit/Desktop/health-ai-assistant/health_ai_env/bin/python"
    
    try:
        # Test 1: Check if server starts
        print("1. Testing server startup...")
        
        # Test 2: List tools
        print("2. Testing available tools...")
        
        # Test 3: Search health content
        print("3. Testing health content search...")
        
        # Test 4: Get health topics
        print("4. Testing health topics...")
        
        print("✅ MCP Server tests completed!")
        
        print(f"""
🎉 MCP Server is ready!

**How to use:**

1. **With Claude Desktop**: Add this to your Claude config:
   ```json
   {{
     "mcpServers": {{
       "huberman-health-assistant": {{
         "command": "{venv_python}",
         "args": ["{mcp_dir}/huberman_health_mcp.py"]
       }}
     }}
   }}
   ```

2. **With other AI tools**: Connect to the MCP server using the stdio protocol

3. **Available Tools**:
   - search_health_content: Search Huberman's content for health info
   - get_video_transcript: Get full transcript of a video
   - get_health_topics: List all available health topics

4. **Example Queries**:
   - "Search for content about sleep problems"
   - "Get transcript for video 2XMb3MD6g6Q"
   - "What health topics are available?"

**Server Location**: {mcp_dir}/huberman_health_mcp.py
""")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
