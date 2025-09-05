from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="Huberman Health AI Assistant", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Initialize OpenAI client for OpenRouter
openai_client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

class HealthQuery(BaseModel):
    query: str
    max_results: int = 3

class SearchResult(BaseModel):
    video_id: str
    title: str
    url: str
    relevance_score: float
    timestamp: Optional[str] = None
    context: str
    description: str

class HealthAssistant:
    def __init__(self):
        self.data_path = "../data"
        self.videos_data = None
        self.merged_data = None
        self.video_embeddings = {}
        self.load_data()
    
    def load_data(self):
        """Load video and transcript data"""
        try:
            # Load videos data
            with open(f"{self.data_path}/videos.json", 'r') as f:
                self.videos_data = json.load(f)
            
            # Load merged data
            with open(f"{self.data_path}/merged.json", 'r') as f:
                self.merged_data = json.load(f)
            
            print(f"Loaded {len(self.videos_data)} videos and {len(self.merged_data)} merged records")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.videos_data = []
            self.merged_data = []
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenRouter"""
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",  # Cost-efficient embedding model
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a dummy embedding if API fails
            return [0.0] * 1536
    
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
    
    async def search_health_content(self, query: str, max_results: int = 3) -> List[SearchResult]:
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
                    
                    result = SearchResult(
                        video_id=video_id,
                        title=title,
                        url=url,
                        relevance_score=total_score,
                        timestamp=timestamp,
                        context=context,
                        description=description
                    )
                    results.append(result)
            
            except Exception as e:
                print(f"Error processing video {video.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    async def get_health_recommendation(self, query: str, search_results: List[SearchResult]) -> str:
        """Generate health recommendation using OpenRouter"""
        try:
            context = "\n\n".join([
                f"Video: {result.title}\nContext: {result.context}\nTimestamp: {result.timestamp}"
                for result in search_results
            ])
            
            prompt = f"""You are a health assistant based on Andrew Huberman's podcast content. 
            
User query: {query}

Relevant content from Huberman Lab:
{context}

Based on this content, provide a helpful response that:
1. Directly addresses the user's health query
2. References the specific Huberman Lab content
3. Includes practical, science-based recommendations
4. Mentions that this is educational content and not medical advice
5. Suggests watching the relevant videos with timestamps

Keep the response concise but informative (200-300 words)."""

            response = openai_client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # Cost-efficient model
                messages=[
                    {"role": "system", "content": "You are a helpful health assistant based on Andrew Huberman's podcast content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "I found relevant content for your query. Please check the video recommendations below for detailed information."

# Initialize the health assistant
health_assistant = HealthAssistant()

@app.get("/")
async def root():
    return {"message": "Huberman Health AI Assistant API", "status": "running"}

@app.post("/search", response_model=Dict[str, Any])
async def search_health_content(query: HealthQuery):
    """Search for health-related content in Huberman's videos"""
    try:
        # Search for relevant content
        search_results = await health_assistant.search_health_content(query.query, query.max_results)
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No relevant content found for your query")
        
        # Generate AI recommendation
        recommendation = await health_assistant.get_health_recommendation(query.query, search_results)
        
        return {
            "query": query.query,
            "recommendation": recommendation,
            "videos": [result.dict() for result in search_results],
            "total_results": len(search_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "videos_loaded": len(health_assistant.videos_data)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
