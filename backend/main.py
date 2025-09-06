from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import asyncio
from sentence_transformers import SentenceTransformer
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Load environment variables
load_dotenv()

app = FastAPI(title="Huberman Health AI Assistant - Monitored", version="1.1.0")

# Simple Prometheus metrics
request_count = Counter('huberman_requests_total', 'Total requests', ['method', 'endpoint'])
search_count = Counter('huberman_searches_total', 'Total search queries')
search_duration = Histogram('huberman_search_seconds', 'Search duration')

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

# Initialize OpenAI client for OpenRouter (optional for development)
openai_client = None
if OPENROUTER_API_KEY:
    openai_client = openai.OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )
    print("✅ OpenAI client initialized with API key")
else:
    print("⚠️ No API key found - AI recommendations will be disabled")
    print("💡 Add OPENROUTER_API_KEY to .env file to enable AI features")

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

class SemanticSearchEngine:
    def __init__(self):
        """Initialize semantic search with local embeddings model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, efficient model
        self.index = None
        self.segments = []
        self.segment_metadata = []
        
    def build_index(self, transcript_segments: List[Dict], batch_size: int = 100):
        """Build FAISS index from transcript segments with batch processing"""
        print("Building semantic search index...")
        
        texts = []
        for segment in transcript_segments:
            try:
                text = segment.get('text', '').strip()
                if text and len(text) > 10:  # Filter short segments
                    # Ensure text is properly encoded
                    if isinstance(text, bytes):
                        text = text.decode('utf-8', errors='ignore')
                    texts.append(text)
                    self.segment_metadata.append(segment)
            except (UnicodeDecodeError, AttributeError) as e:
                print(f"Skipping problematic segment: {e}")
                continue
        
        if not texts:
            print("No valid text segments found")
            return
            
        # Generate embeddings in batches to handle large datasets
        print(f"Generating embeddings for {len(texts)} segments in batches of {batch_size}")
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            try:
                batch_embeddings = self.model.encode(
                    batch_texts, 
                    show_progress_bar=True,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                all_embeddings.append(batch_embeddings)
                print(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")
                continue
        
        if not all_embeddings:
            print("Failed to generate any embeddings")
            return
            
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Add embeddings to index (already normalized)
        self.index.add(embeddings.astype('float32'))
        
        print(f"Built semantic index with {len(texts)} segments")
        
    def search_semantic(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search using semantic similarity with error handling"""
        if not self.index:
            return []
            
        try:
            # Ensure query is properly encoded
            if isinstance(query, bytes):
                query = query.decode('utf-8', errors='ignore')
                
            # Encode query
            query_embedding = self.model.encode(
                [query], 
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.segment_metadata) and idx >= 0:
                    segment = self.segment_metadata[idx].copy()
                    segment['semantic_score'] = float(score)
                    results.append(segment)
                    
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

class HealthAssistant:
    def __init__(self):
        self.data_path = "data/"
        self.videos_data = None
        self.merged_data = None
        self.semantic_search = SemanticSearchEngine()
        self.load_data()
        
    def load_data(self):
        """Load video and transcript data, build semantic index with proper encoding"""
        try:
            # Use UTF-8 encoding explicitly to handle special characters
            with open(f'{self.data_path}/videos.json', 'r', encoding='utf-8') as f:
                self.videos_data = json.load(f)
            with open(f'{self.data_path}/merged.json', 'r', encoding='utf-8') as f:
                self.merged_data = json.load(f)
            
            print(f"Loaded {len(self.videos_data)} videos and {len(self.merged_data)} merged records")
            
            # Build semantic search index with batch processing
            all_segments = []
            for video in self.merged_data:
                try:
                    video_id = video.get('id', '')
                    transcript = video.get('transcript', [])
                    
                    for segment in transcript:
                        try:
                            segment_with_meta = segment.copy()
                            segment_with_meta['video_id'] = video_id
                            segment_with_meta['video_title'] = video.get('title', '')
                            
                            # Ensure text is properly handled
                            if 'text' in segment_with_meta:
                                text = segment_with_meta['text']
                                if isinstance(text, bytes):
                                    text = text.decode('utf-8', errors='ignore')
                                segment_with_meta['text'] = text
                                
                            all_segments.append(segment_with_meta)
                        except Exception as e:
                            print(f"Error processing segment in video {video_id}: {e}")
                            continue
                except Exception as e:
                    print(f"Error processing video {video.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"Extracted {len(all_segments)} total segments")
            self.semantic_search.build_index(all_segments)
            
        except FileNotFoundError as e:
            print(f"Data files not found: {e}")
            print("Please ensure videos.json and merged.json exist in the data/ directory")
            self.videos_data = []
            self.merged_data = []
        except UnicodeDecodeError as e:
            print(f"Encoding error loading data: {e}")
            print("Attempting to load with different encoding...")
            try:
                # Fallback to latin-1 encoding
                with open(f'{self.data_path}/videos.json', 'r', encoding='latin-1') as f:
                    self.videos_data = json.load(f)
                with open(f'{self.data_path}/merged.json', 'r', encoding='latin-1') as f:
                    self.merged_data = json.load(f)
                print("Successfully loaded data with latin-1 encoding")
            except Exception as fallback_error:
                print(f"Fallback encoding failed: {fallback_error}")
                self.videos_data = []
                self.merged_data = []
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            self.videos_data = []
            self.merged_data = []
        except Exception as e:
            print(f"Unexpected error loading data: {e}")
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
        """Generate health recommendation using OpenRouter (if available)"""
        try:
            if not openai_client:
                # Return basic recommendation without AI when API key is missing
                return f"""Based on your query about "{query}", I found relevant content from Huberman Lab podcasts. 
                
The search returned {len(search_results)} relevant videos. Please check the video recommendations below for detailed information from Dr. Andrew Huberman's research-based content.

Note: AI-powered recommendations are currently disabled. Add your OPENROUTER_API_KEY to the .env file to enable enhanced AI responses."""

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
            return f"""Based on your query about "{query}", I found relevant content from Huberman Lab podcasts. 
            
The search returned {len(search_results)} relevant videos. Please check the video recommendations below for detailed information from Dr. Andrew Huberman's research-based content.

Note: AI recommendation service is temporarily unavailable, but the search results below contain the relevant information you're looking for."""

# Initialize the health assistant
health_assistant = HealthAssistant()

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    request_count.labels(method="GET", endpoint="/metrics").inc()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "Huberman Health AI Assistant API", "status": "running"}

@app.post("/search", response_model=Dict[str, Any])
async def search_health_content(query: HealthQuery):
    """Search for health-related content using semantic search"""
    import time
    start_time = time.time()
    
    try:
        # Track metrics
        request_count.labels(method="POST", endpoint="/search").inc()
        search_count.inc()
        
        # Search for relevant content
        search_results = await health_assistant.search_health_content(query.query, query.max_results)
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No relevant content found for your query")
        
        # Generate AI recommendation
        recommendation = await health_assistant.get_health_recommendation(query.query, search_results)
        
        # Record search duration
        search_duration.observe(time.time() - start_time)
        
        return {
            "query": query.query,
            "recommendation": recommendation,
            "videos": [result.dict() for result in search_results],
            "total_results": len(search_results),
            "search_type": "semantic_hybrid"
        }
    
    except Exception as e:
        # Record search duration even on error
        search_duration.observe(time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    request_count.labels(method="GET", endpoint="/health").inc()
    return {
        "status": "healthy", 
        "videos_loaded": len(health_assistant.videos_data),
        "semantic_index_ready": health_assistant.semantic_search.index is not None,
        "monitoring_enabled": True
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use Render's PORT environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
