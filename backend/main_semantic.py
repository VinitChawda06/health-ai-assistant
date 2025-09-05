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

# Load environment variables
load_dotenv()

app = FastAPI(title="Huberman Health AI Assistant - Semantic Search", version="2.0.0")

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

class SemanticSearchEngine:
    def __init__(self):
        """Initialize semantic search with local embeddings model"""
        print("Loading semantic search model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, efficient model
        self.index = None
        self.segments = []
        self.segment_metadata = []
        
    def build_index(self, transcript_segments: List[Dict]):
        """Build FAISS index from transcript segments"""
        print("Building semantic search index...")
        
        texts = []
        for segment in transcript_segments:
            text = segment.get('text', '').strip()
            if text and len(text) > 10:  # Filter short segments
                texts.append(text)
                self.segment_metadata.append(segment)
        
        if not texts:
            print("No valid text segments found")
            return
            
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} segments...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ Built semantic index with {len(texts)} segments")
        
    def search_semantic(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search using semantic similarity"""
        if not self.index:
            return []
            
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.segment_metadata):
                segment = self.segment_metadata[idx].copy()
                segment['semantic_score'] = float(score)
                results.append(segment)
                
        return results

class HealthAssistant:
    def __init__(self):
        self.data_path = "data"
        self.videos_data = None
        self.merged_data = None
        self.semantic_search = SemanticSearchEngine()
        self.load_data()
        
    def load_data(self):
        """Load video and transcript data, build semantic index"""
        try:
            with open(f'{self.data_path}/videos.json', 'r') as f:
                self.videos_data = json.load(f)
            with open(f'{self.data_path}/merged.json', 'r') as f:
                self.merged_data = json.load(f)
            
            print(f"Loaded {len(self.videos_data)} videos and {len(self.merged_data)} merged records")
            
            # Build semantic search index
            all_segments = []
            for video in self.merged_data:
                video_id = video.get('id', '')
                transcript = video.get('transcript', [])
                for segment in transcript:
                    segment_with_meta = segment.copy()
                    segment_with_meta['video_id'] = video_id
                    segment_with_meta['video_title'] = video.get('title', '')
                    all_segments.append(segment_with_meta)
            
            self.semantic_search.build_index(all_segments)
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.videos_data = []
            self.merged_data = []

    def format_timestamp(self, start_time):
        """Convert seconds to MM:SS format"""
        try:
            seconds = float(start_time)
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}:{remaining_seconds:02d}"
        except:
            return "0:00"

    async def search_health_content(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Hybrid search: Semantic + keyword matching for optimal results"""
        results = []
        
        # Step 1: Semantic search for meaning-based matches
        semantic_results = self.semantic_search.search_semantic(query, top_k=15)
        
        # Step 2: Group by video and aggregate scores
        video_scores = {}
        for segment in semantic_results:
            video_id = segment.get('video_id', '')
            if not video_id:
                continue
                
            semantic_score = segment.get('semantic_score', 0)
            
            if video_id not in video_scores:
                video_scores[video_id] = {
                    'segments': [],
                    'total_semantic_score': 0,
                    'keyword_score': 0
                }
            
            video_scores[video_id]['segments'].append(segment)
            video_scores[video_id]['total_semantic_score'] += semantic_score
        
        # Step 3: Add keyword matching boost
        query_lower = query.lower()
        health_keywords = {
            'sleep': ['sleep', 'insomnia', 'circadian', 'melatonin', 'rest'],
            'stress': ['stress', 'anxiety', 'cortisol', 'overwhelm'],
            'focus': ['focus', 'attention', 'concentration', 'ADHD'],
            'exercise': ['exercise', 'workout', 'fitness', 'muscle'],
            'nutrition': ['nutrition', 'diet', 'food', 'eating'],
            'dopamine': ['dopamine', 'motivation', 'reward'],
        }
        
        # Find matching keywords
        matching_keywords = []
        for topic, keywords in health_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_keywords.extend(keywords)
        
        if not matching_keywords:
            matching_keywords = query_lower.split()
        
        # Apply keyword boost to video titles
        for video in self.merged_data:
            video_id = video.get('id', '')
            title = video.get('title', '').lower()
            
            keyword_score = sum(3 for keyword in matching_keywords if keyword in title)
            
            if video_id in video_scores:
                video_scores[video_id]['keyword_score'] = keyword_score
        
        # Step 4: Create final results with combined scoring
        for video_id, data in video_scores.items():
            if not data['segments']:
                continue
                
            # Get best segment for this video
            best_segment = max(data['segments'], key=lambda x: x.get('semantic_score', 0))
            
            # Combined score: semantic + keyword boost
            semantic_avg = data['total_semantic_score'] / len(data['segments'])
            combined_score = (semantic_avg * 50) + (data['keyword_score'] * 10)
            
            # Get video metadata
            video_info = next((v for v in self.videos_data if v.get('id') == video_id), {})
            video_merged = next((v for v in self.merged_data if v.get('id') == video_id), {})
            
            # Format timestamp
            timestamp = self.format_timestamp(best_segment.get('start', 0))
            
            # Create search result
            result = SearchResult(
                video_id=video_id,
                title=video_merged.get('title', 'Unknown Title'),
                url=f"https://www.youtube.com/watch?v={video_id}&t={int(best_segment.get('start', 0))}s",
                relevance_score=combined_score,
                timestamp=timestamp,
                context=best_segment.get('text', '')[:200] + "...",
                description=video_info.get('description', '')[:200] + "..."
            )
            results.append(result)
        
        # Sort by combined score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    async def get_health_recommendation(self, query: str, search_results: List[SearchResult]) -> str:
        """Generate health recommendation using OpenRouter"""
        try:
            context = "\n\n".join([
                f"Video: {result.title}\nContent: {result.context}\nTimestamp: {result.timestamp}"
                for result in search_results
            ])
            
            prompt = f"""
            Based on the following content from Andrew Huberman's podcast, provide helpful health advice for: {query}

            Relevant Content:
            {context}

            Please provide:
            1. A clear, actionable recommendation
            2. Reference the specific protocols mentioned
            3. Include timing/dosage if relevant
            4. Keep it concise but comprehensive

            Remember this is educational content, not medical advice.
            """
            
            response = await asyncio.to_thread(
                openai_client.chat.completions.create,
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "I apologize, but I'm unable to generate a recommendation at this time. Please refer to the search results for Huberman's insights."

# Initialize the health assistant
health_assistant = HealthAssistant()

# API Endpoints
@app.post("/search", response_model=Dict[str, Any])
async def search_health_content(query: HealthQuery):
    """Search for health-related content using semantic search"""
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
            "total_results": len(search_results),
            "search_type": "semantic_hybrid"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "videos_loaded": len(health_assistant.videos_data),
        "semantic_index_ready": health_assistant.semantic_search.index is not None
    }

@app.get("/")
async def root():
    return {
        "message": "Huberman Health AI Assistant - Semantic Search API",
        "version": "2.0.0",
        "endpoints": ["/search", "/health"],
        "features": ["semantic_search", "keyword_boost", "ai_recommendations"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
