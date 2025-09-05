# 🧠 Huberman Health AI Assistant

A comprehensive health assistant that searches Andrew Huberman's podcast library to answer user queries with specific video recommendations and precise timestamps.

## 🎯 Project Overview

This project implements a complete health AI assistant with:

- **FastAPI Backend**: AI-powered semantic search across Huberman Lab transcripts
- **Streamlit Frontend**: Clean, responsive web interface for health queries
- **MCP Server**: Model Context Protocol server for AI integration
- **OpenRouter Integration**: Cost-efficient AI recommendations using GPT-3.5
- **Smart Search**: Enhanced keyword matching for health topics with timestamp extraction

## 🚀 Features

### ✅ Core Functionality
- 🔍 **Smart Health Search**: Search 10+ Huberman Lab episodes for health content
- ⏰ **Precise Timestamps**: Get exact timestamps where topics are discussed
- 🤖 **AI Recommendations**: GPT-3.5 powered health advice based on Huberman's content
- 📱 **Responsive UI**: Beautiful Streamlit interface with video embedding
- 🔗 **MCP Integration**: Connect to Claude, GPT, and other AI systems

### 🎥 Available Content
- Sleep & Circadian Rhythms
- Stress & Anxiety Management  
- Focus & Attention (ADHD)
- Dopamine & Motivation
- Brain & Neuroscience
- Nutrition & Fasting
- Exercise & Fitness

## 📁 Project Structure

```
health-ai-assistant/
├── backend/                 # FastAPI backend server
│   └── main.py             # Main API server with health search
├── frontend/               # Streamlit web interface
│   └── app.py             # Web UI for health queries
├── mcp_server/            # Model Context Protocol server
│   ├── huberman_health_mcp.py  # MCP server implementation
│   ├── mcp_config.json         # MCP configuration
│   └── test_mcp.py            # MCP server tests
├── data/                  # Huberman Lab podcast data
│   ├── videos.json        # Video metadata
│   ├── merged.json        # Videos + transcripts
│   └── *.json            # Individual video transcripts
├── health_ai_env/         # Python virtual environment
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
└── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- OpenRouter API key (for AI features)

### 1. Clone & Setup
```bash
cd health-ai-assistant
chmod +x setup.sh run_backend.sh run_frontend.sh
./setup.sh
```

### 2. Configure API Key
Edit `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your API key from [OpenRouter.ai](https://openrouter.ai/)

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
./run_backend.sh
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh  
# Frontend runs on http://localhost:8501
```

## 🔧 Usage

### Web Interface
1. Open http://localhost:8501
2. Enter a health query (e.g., "I have trouble sleeping")
3. Get AI recommendations and relevant videos with timestamps
4. Click video links to watch at specific timestamps

### API Usage
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "stress management", "max_results": 3}'
```

### MCP Server (AI Integration)
For Claude Desktop, add to your config:
```json
{
  "mcpServers": {
    "huberman-health-assistant": {
      "command": "/path/to/health_ai_env/bin/python",
      "args": ["/path/to/mcp_server/huberman_health_mcp.py"]
    }
  }
}
```

## 🧪 Testing

### Test Backend
```bash
curl http://localhost:8000/health
```

### Test MCP Server
```bash
cd mcp_server
python test_mcp.py
```

### Example Queries
- "I have trouble sleeping"
- "How to reduce stress and anxiety"  
- "Ways to improve focus and concentration"
- "Natural ways to boost energy"
- "How to build muscle effectively"

## 📊 API Endpoints

### FastAPI Backend (`localhost:8000`)

#### `GET /`
- Health check and server info

#### `GET /health`  
- Server status and loaded video count

#### `POST /search`
- Search health content
- Body: `{"query": "health question", "max_results": 3}`
- Returns: AI recommendations + relevant videos with timestamps

## 🤖 MCP Server Tools

### Available Tools
1. **search_health_content**: Search Huberman's content for health information
2. **get_video_transcript**: Get full transcript of a specific video  
3. **get_health_topics**: List all available health topics

### Resources
- `huberman://videos`: Video metadata
- `huberman://transcripts`: Full transcripts
- `huberman://health-topics`: Health topics index

## 💰 Cost Efficiency

- **OpenRouter GPT-3.5**: ~$0.001 per search query
- **Smart Caching**: Reduces API calls
- **Targeted Search**: Only processes relevant content

## 🔒 Health Disclaimer

⚠️ **Important**: This tool provides educational content based on Andrew Huberman's podcast transcripts. It is NOT medical advice and should not replace consultation with healthcare professionals.

## 🗂️ Data Source

Content sourced from [Huberman Lab Podcast](https://www.youtube.com/@hubermanlab) - 10 recent episodes with full transcripts and timestamps.

## 🛣️ Next Steps

1. **✅ Core Application** - FastAPI + Streamlit ✅
2. **✅ MCP Server** - Model Context Protocol integration ✅  
3. **🔄 Monitoring** - Add Prometheus metrics
4. **🔄 Deployment** - Docker containerization
5. **🔄 CI/CD** - GitHub Actions pipeline
6. **🔄 Enhanced AI** - Better embeddings and semantic search

## 📋 Requirements Met

✅ **Data Collection**: Using Apify-scraped Huberman Lab content  
✅ **MCP Server**: Custom server for health query processing  
✅ **AI Integration**: OpenRouter GPT-3.5 for recommendations  
✅ **Frontend**: Clean, responsive Streamlit interface  
✅ **Health Disclaimers**: Proper medical disclaimers included  
✅ **Budget Efficiency**: Cost-effective API usage (~$0.001/query)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Huberman Lab content is used under fair use for educational purposes.

---

**Built with ❤️ for health and science education**
