import streamlit as st
import requests
import json
from typing import Dict, List
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Huberman Health AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Then replace any localhost:8000 references with BACKEND_URL

def main():
    # Title and description
    st.title("🧠 Huberman Health AI Assistant")
    st.markdown("""
    **Get science-based health recommendations from Andrew Huberman's podcast library**
    
    Ask about any health topic and get relevant video recommendations with exact timestamps where Dr. Huberman discusses your concern.
    """)
    
    # Disclaimer
    with st.expander("⚠️ Important Health Disclaimer"):
        st.warning("""
        This tool provides educational content based on Andrew Huberman's podcast transcripts. 
        It is NOT medical advice and should not replace consultation with healthcare professionals.
        Always consult with qualified medical professionals for health concerns.
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Search Settings")
        max_results = st.slider("Max video results", min_value=1, max_value=5, value=3)
        
        st.header("📚 Example Queries")
        example_queries = [
            "I have trouble sleeping",
            "How to reduce stress and anxiety",
            "I feel tired and low energy",
            "Ways to improve focus and concentration", 
            "Stomach problems and gut health",
            "How to build muscle effectively",
            "Natural ways to boost mood"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.search_query = query
    
    # Main search interface
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "💬 Ask your health question:",
            placeholder="e.g., I have stomach ache, trouble sleeping, low energy...",
            value=st.session_state.get('search_query', ''),
            key="search_input"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Handle search
    if search_button and search_query:
        search_health_content(search_query, max_results)
    elif search_query and 'last_search' in st.session_state and st.session_state.last_search == search_query:
        # Display cached results
        display_cached_results()

def search_health_content(query: str, max_results: int):
    """Search for health content and display results"""
    with st.spinner("🔍 Searching Huberman's podcast library..."):
        try:
            # Make API request
            response = requests.post(
                f"{API_BASE_URL}/search",
                json={"query": query, "max_results": max_results},
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Cache results
                st.session_state.search_results = results
                st.session_state.last_search = query
                
                display_search_results(results)
                
            elif response.status_code == 404:
                st.error("❌ No relevant content found for your query. Try rephrasing your question.")
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the API. Make sure the backend server is running on http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

def display_cached_results():
    """Display cached search results"""
    if 'search_results' in st.session_state:
        display_search_results(st.session_state.search_results)

def display_search_results(results: Dict):
    """Display search results"""
    st.success(f"✅ Found {results['total_results']} relevant videos")
    
    # AI Recommendation
    if results.get('recommendation'):
        st.subheader("🤖 AI Health Recommendation")
        st.info(results['recommendation'])
    
    # Video Results
    st.subheader("📹 Relevant Videos")
    
    for i, video in enumerate(results['videos'], 1):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {i}. {video['title']}")
                
                # Relevance score
                relevance_percentage = min(100, int((video['relevance_score'] / 10) * 100))
                st.progress(relevance_percentage / 100, text=f"Relevance: {relevance_percentage}%")
                
                # Context
                if video['context']:
                    st.markdown("**📝 Relevant Context:**")
                    st.markdown(f"*\"{video['context'][:200]}...\"*")
                
                # Description
                if video['description']:
                    with st.expander("📖 Episode Description"):
                        st.markdown(video['description'])
            
            with col2:
                st.markdown("**⏰ Timestamp:**")
                st.code(video.get('timestamp', 'N/A'))
                
                # YouTube link
                youtube_url = video['url']
                if video.get('timestamp') and video['timestamp'] != 'N/A':
                    # Convert timestamp to seconds for YouTube URL
                    try:
                        time_parts = video['timestamp'].split(':')
                        if len(time_parts) == 2:
                            minutes, seconds = map(int, time_parts)
                            total_seconds = minutes * 60 + seconds
                            youtube_url += f"&t={total_seconds}s"
                    except:
                        pass
                
                st.link_button("▶️ Watch Video", youtube_url, use_container_width=True)
                
                # Embed option
                if st.button(f"📺 Embed", key=f"embed_{i}"):
                    st.session_state[f"show_embed_{i}"] = not st.session_state.get(f"show_embed_{i}", False)
            
            # Embedded video
            if st.session_state.get(f"show_embed_{i}", False):
                video_id = video['video_id']
                if video.get('timestamp') and video['timestamp'] != 'N/A':
                    try:
                        time_parts = video['timestamp'].split(':')
                        if len(time_parts) == 2:
                            minutes, seconds = map(int, time_parts)
                            total_seconds = minutes * 60 + seconds
                            embed_url = f"https://www.youtube.com/embed/{video_id}?start={total_seconds}"
                        else:
                            embed_url = f"https://www.youtube.com/embed/{video_id}"
                    except:
                        embed_url = f"https://www.youtube.com/embed/{video_id}"
                else:
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                
                st.markdown(f'<iframe width="100%" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', 
                           unsafe_allow_html=True)
            
            st.divider()

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Footer
def display_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🧠 Huberman Health AI Assistant | Built with Streamlit & FastAPI</p>
        <p>Data source: <a href='https://www.youtube.com/@hubermanlab' target='_blank'>Huberman Lab Podcast</a></p>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

# Check API status
api_status = check_api_status()
if not api_status:
    st.error("❌ Backend API is not running. Please start the FastAPI server first.")
    st.code("cd backend && uvicorn main:app --reload")
else:
    st.success("✅ Backend API is running")

# Run main app
if __name__ == "__main__":
    main()
    display_footer()
