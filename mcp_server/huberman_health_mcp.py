#!/usr/bin/env python3
"""
Huberman Health AI Assistant MCP Server

This Model Context Protocol server provides access to Andrew Huberman's podcast 
transcripts for health-related queries. It allows AI systems to search through
the knowledge base and get relevant health information with timestamps.
"""

import asyncio
import json
import logging
from typing import Any, Sequence, Dict, List, Optional
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("huberman-health-mcp")

class HubermanHealthMCP:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"  # Go up one level to project root
        self.videos_data: List[Dict] = []
        self.merged_data: List[Dict] = []
        self.load_data()
    
    def load_data(self):
        """Load video and transcript data"""
        try:
            # Load videos data
            videos_file = self.data_path / "videos.json"
            if videos_file.exists():
                with open(videos_file, 'r') as f:
                    self.videos_data = json.load(f)
            
            # Load merged data
            merged_file = self.data_path / "merged.json"
            if merged_file.exists():
                with open(merged_file, 'r') as f:
                    self.merged_data = json.load(f)
            
            logger.info(f"Loaded {len(self.videos_data)} videos and {len(self.merged_data)} merged records")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.videos_data = []
            self.merged_data = []
    
    def extract_relevant_segments(self, transcript: List[Dict], query: str, max_segments: int = 3) -> List[Dict]:
        """Extract relevant transcript segments based on health query"""
        if not transcript:
            return []
        
        # Enhanced keyword matching for health topics
        health_keywords = {
            'stomach': ['stomach', 'gastric', 'digestion', 'gut', 'intestine', 'digestive', 'belly', 'abdominal'],
            'sleep': ['sleep', 'insomnia', 'circadian', 'melatonin', 'rest', 'sleeping', 'sleepy', 'tired', 'fatigue', 'light', 'timing'],
            'stress': ['stress', 'anxiety', 'cortisol', 'relax', 'calm', 'stressed', 'anxious', 'overwhelm'],
            'energy': ['energy', 'fatigue', 'tired', 'dopamine', 'motivation', 'energetic', 'vitality', 'exhausted'],
            'focus': ['focus', 'attention', 'concentration', 'ADHD', 'clarity', 'focused', 'concentrate', 'distraction'],
            'depression': ['depression', 'mood', 'serotonin', 'happiness', 'depressed', 'sad', 'melancholy'],
            'pain': ['pain', 'inflammation', 'chronic', 'relief', 'ache', 'hurt', 'sore'],
            'fitness': ['muscle', 'strength', 'endurance', 'exercise', 'workout', 'training', 'fitness'],
            'brain': ['brain', 'cognitive', 'memory', 'learning', 'neuroplasticity', 'neuroscience'],
        }
        
        query_lower = query.lower()
        relevant_segments = []
        
        for segment in transcript:
            if 'text' in segment and segment['text']:
                text_lower = segment['text'].lower()
                score = 0
                
                # Direct keyword matching
                for word in query_lower.split():
                    if word in text_lower:
                        score += 2
                
                # Health category matching
                for category, keywords in health_keywords.items():
                    if any(keyword in query_lower for keyword in keywords):
                        if any(keyword in text_lower for keyword in keywords):
                            score += 3
                
                if score > 0:
                    segment_copy = segment.copy()
                    segment_copy['relevance_score'] = score
                    relevant_segments.append(segment_copy)
        
        # Sort by relevance and return top segments
        relevant_segments.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_segments[:max_segments]
    
    def format_timestamp(self, start_time: str) -> str:
        """Convert timestamp to YouTube format"""
        try:
            seconds = float(start_time)
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}:{remaining_seconds:02d}"
        except:
            return "0:00"
    
    def search_health_content(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search for relevant health content in Huberman's videos"""
        results = []
        query_lower = query.lower()
        
        # Enhanced keyword matching for health topics
        health_keywords = {
            'stomach': ['stomach', 'gastric', 'digestion', 'gut', 'intestine', 'digestive', 'belly', 'abdominal'],
            'sleep': ['sleep', 'insomnia', 'circadian', 'melatonin', 'rest', 'sleeping', 'sleepy', 'tired', 'fatigue', 'light', 'timing'],
            'stress': ['stress', 'anxiety', 'cortisol', 'relax', 'calm', 'stressed', 'anxious', 'overwhelm'],
            'energy': ['energy', 'fatigue', 'tired', 'dopamine', 'motivation', 'energetic', 'vitality', 'exhausted'],
            'focus': ['focus', 'attention', 'concentration', 'ADHD', 'clarity', 'focused', 'concentrate', 'distraction'],
            'depression': ['depression', 'mood', 'serotonin', 'happiness', 'depressed', 'sad', 'melancholy'],
            'pain': ['pain', 'inflammation', 'chronic', 'relief', 'ache', 'hurt', 'sore'],
            'fitness': ['muscle', 'strength', 'endurance', 'exercise', 'workout', 'training', 'fitness'],
            'brain': ['brain', 'cognitive', 'memory', 'learning', 'neuroplasticity', 'neuroscience'],
        }
        
        for video in self.merged_data:
            try:
                video_id = video.get('id', '')
                title = video.get('title', '')
                url = video.get('url', '')
                transcript = video.get('transcript', [])
                
                # Also check title for relevance
                title_score = 0
                title_lower = title.lower()
                
                # Direct keyword matching in title (higher weight)
                for word in query_lower.split():
                    if word in title_lower:
                        title_score += 5
                
                # Health category matching in title
                for category, keywords in health_keywords.items():
                    if any(keyword in query_lower for keyword in keywords):
                        if any(keyword in title_lower for keyword in keywords):
                            title_score += 10
                
                # Find relevant segments in transcript
                relevant_segments = self.extract_relevant_segments(transcript, query)
                
                if relevant_segments or title_score > 0:
                    # Calculate overall relevance score
                    transcript_score = sum(seg['relevance_score'] for seg in relevant_segments) if relevant_segments else 0
                    total_score = title_score + transcript_score
                    
                    # Get the best segment for context
                    if relevant_segments:
                        best_segment = relevant_segments[0]
                        context = best_segment.get('text', '')
                        timestamp = self.format_timestamp(best_segment.get('start', '0'))
                    else:
                        # If only title matched, use title as context
                        context = f"This video discusses topics related to your query: {title}"
                        timestamp = "0:00"
                    
                    # Get video description from videos_data
                    description = ""
                    for video_data in self.videos_data:
                        if video_data.get('id') == video_id:
                            description = video_data.get('description', '')[:300] + "..."
                            break
                    
                    result = {
                        'video_id': video_id,
                        'title': title,
                        'url': url,
                        'relevance_score': total_score,
                        'timestamp': timestamp,
                        'context': context,
                        'description': description
                    }
                    results.append(result)
            
            except Exception as e:
                logger.error(f"Error processing video {video.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]

# Initialize the health assistant
health_assistant = HubermanHealthMCP()

# Create the MCP server
server = Server("huberman-health-assistant")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available health resources"""
    return [
        Resource(
            uri="huberman://videos",
            name="Huberman Lab Videos",
            description="Andrew Huberman's podcast video metadata",
            mimeType="application/json"
        ),
        Resource(
            uri="huberman://transcripts", 
            name="Huberman Lab Transcripts",
            description="Full transcripts of Huberman Lab episodes",
            mimeType="application/json"
        ),
        Resource(
            uri="huberman://health-topics",
            name="Health Topics Index",
            description="Categorized health topics covered in the podcast",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource"""
    if uri == "huberman://videos":
        return json.dumps(health_assistant.videos_data, indent=2)
    elif uri == "huberman://transcripts":
        return json.dumps(health_assistant.merged_data, indent=2)
    elif uri == "huberman://health-topics":
        # Extract unique health topics
        topics = set()
        for video in health_assistant.merged_data:
            title = video.get('title', '').lower()
            if 'sleep' in title:
                topics.add('sleep')
            if 'stress' in title:
                topics.add('stress')
            if 'focus' in title or 'adhd' in title:
                topics.add('focus')
            if 'dopamine' in title:
                topics.add('dopamine')
            if 'brain' in title or 'neuro' in title:
                topics.add('brain')
            if 'fasting' in title:
                topics.add('fasting')
        
        return json.dumps({
            "available_topics": list(topics),
            "total_videos": len(health_assistant.videos_data),
            "total_transcripts": len(health_assistant.merged_data)
        }, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_health_content",
            description="Search Huberman Lab content for health-related information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Health-related query (e.g., 'sleep problems', 'stress management', 'focus improvement')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_video_transcript",
            description="Get the full transcript of a specific Huberman Lab video",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "YouTube video ID"
                    }
                },
                "required": ["video_id"]
            }
        ),
        Tool(
            name="get_health_topics",
            description="Get a list of all health topics covered in Huberman Lab",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "search_health_content":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 3)
        
        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]
        
        try:
            results = health_assistant.search_health_content(query, max_results)
            
            if not results:
                return [TextContent(
                    type="text", 
                    text=f"No relevant content found for query: '{query}'"
                )]
            
            # Format results for AI consumption
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = f"""
**Result {i}: {result['title']}**
- Relevance Score: {result['relevance_score']:.1f}
- Video URL: {result['url']}
- Timestamp: {result['timestamp']}
- Context: "{result['context'][:200]}..."
- Description: {result['description'][:150]}...

"""
                formatted_results.append(formatted_result)
            
            response = f"""Found {len(results)} relevant results for "{query}":

{''.join(formatted_results)}

**Health Disclaimer**: This information is for educational purposes only and is not medical advice. Always consult healthcare professionals for medical concerns."""
            
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Error in search_health_content: {e}")
            return [TextContent(type="text", text=f"Error searching content: {str(e)}")]
    
    elif name == "get_video_transcript":
        video_id = arguments.get("video_id", "")
        
        if not video_id:
            return [TextContent(type="text", text="Error: video_id parameter is required")]
        
        # Find the video transcript
        for video in health_assistant.merged_data:
            if video.get('id') == video_id:
                transcript = video.get('transcript', [])
                if transcript:
                    # Format transcript
                    formatted_transcript = f"**Transcript for: {video.get('title', 'Unknown')}**\n\n"
                    for segment in transcript:
                        if 'text' in segment and segment['text']:
                            timestamp = health_assistant.format_timestamp(segment.get('start', '0'))
                            formatted_transcript += f"[{timestamp}] {segment['text']}\n"
                    
                    return [TextContent(type="text", text=formatted_transcript)]
                else:
                    return [TextContent(type="text", text=f"No transcript available for video ID: {video_id}")]
        
        return [TextContent(type="text", text=f"Video not found: {video_id}")]
    
    elif name == "get_health_topics":
        # Extract health topics from titles
        topics_count = {}
        for video in health_assistant.merged_data:
            title = video.get('title', '').lower()
            
            # Count topic mentions
            if 'sleep' in title or 'circadian' in title:
                topics_count['Sleep & Circadian Rhythms'] = topics_count.get('Sleep & Circadian Rhythms', 0) + 1
            if 'stress' in title or 'anxiety' in title:
                topics_count['Stress & Anxiety'] = topics_count.get('Stress & Anxiety', 0) + 1
            if 'focus' in title or 'adhd' in title or 'attention' in title:
                topics_count['Focus & Attention'] = topics_count.get('Focus & Attention', 0) + 1
            if 'dopamine' in title:
                topics_count['Dopamine & Motivation'] = topics_count.get('Dopamine & Motivation', 0) + 1
            if 'brain' in title or 'neuro' in title:
                topics_count['Brain & Neuroscience'] = topics_count.get('Brain & Neuroscience', 0) + 1
            if 'fasting' in title or 'eating' in title:
                topics_count['Nutrition & Fasting'] = topics_count.get('Nutrition & Fasting', 0) + 1
            if 'exercise' in title or 'fitness' in title or 'strength' in title:
                topics_count['Exercise & Fitness'] = topics_count.get('Exercise & Fitness', 0) + 1
        
        topics_list = "\n".join([f"- {topic}: {count} videos" for topic, count in topics_count.items()])
        
        response = f"""**Health Topics Covered in Huberman Lab:**

{topics_list}

**Total Videos**: {len(health_assistant.videos_data)}
**Total Transcripts**: {len(health_assistant.merged_data)}

**Usage Examples**:
- Search for sleep: "I have trouble sleeping"
- Search for stress: "How to manage stress and anxiety"
- Search for focus: "Ways to improve concentration"
- Search for fitness: "How to build muscle effectively"
"""
        
        return [TextContent(type="text", text=response)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    # Run the server using stdin/stdout streams  
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            None  # Simplified initialization without complex options
        )

if __name__ == "__main__":
    asyncio.run(main())
