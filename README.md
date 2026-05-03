# 🎨 Creative Campaign Agent

An AI-powered marketing campaign generator built with **Cycls SDK** and **FastAPI**. Generate culturally-relevant marketing campaigns for Saudi audiences with strategic insights and compelling copywriting.

## ✨ Features

- 🧠 **Dual-Agent Architecture** - Strategist + Copywriter with critic loops
- 🌍 **Bilingual Support** - Generate campaigns in English or Arabic (Saudi dialect)
- 💾 **Memory System** - Learns from previous campaigns for better results
- 📊 **Real-time Streaming** - Watch strategy and copy generation as it happens
- 🎯 **Saudi-Focused** - Culturally-specific marketing strategies
- 🔄 **Self-Improving** - Critic loops ensure 7/10 quality score minimum

## 🏗️ Architecture

User Input (Form)
↓
Strategist Agent (GPT-4o-mini)
↓
Strategy Critic (Score 0-10)
↓ (if <7, revise)
Copywriter Agent (GPT-4o-mini)
↓
Copy Critic (Score 0-10)
↓ (if <7, revise)
Final Campaign Output
↓
Memory Storage (for future campaigns)


## 📋 Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/) (required for Cycls)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **Git** (optional) - [Download](https://git-scm.com/)

## 🚀 Quick Start

### 1. Clone the Repository

git clone https://github.com/saqib-shafiq/creative-agent-modular.git
cd creative-agent-modular

### 2. Create Virtual Environment

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

**### 3. Install Dependencies**

pip install -r requirements.txt


**### 4. Set Up Environment Variables**

# Required: Your OpenAI API key
OPENAI_API_KEY=sk-proj-your-key-here

# Optional: Cycls Cloud API key (for deployment only)
CYCLS_API_KEY=your-cycls-key-here

⚠️ IMPORTANT: Never commit your .env file! It's already in .gitignore.

**### 5. Run the Agent**

cycls run cycls_agent.py

This will:

Build a Docker container with all dependencies

Start the FastAPI server

Open the web interface at http://localhost:8080


**Option B: Run with Uvicorn (Direct Python)**

python cycls_agent.py

**📝 Usage Guide**

**Web Form Interface**

1. Open your browser to http://localhost:8080
2. Fill out the campaign brief:
    Product Name: e.g., "Mint & Lemon"
    Product Description: Key features and benefits
    Target Audience: Demographics and psychographics
    Brand Voice: Select from dropdown
    Output Language: English or Arabic
3. Click Generate Campaign
4. Watch as the agent:
    Loads memory from previous campaigns
    Develops strategic positioning
    Writes compelling copy
    Streams results in real-time


**Example Campaign Brief**

Product Name: Mint & Lemon
Product Description: A refreshing, sparkling drink made from natural ingredients with zero sugar
Target Audience: Young professionals and students in Saudi cities (18-30)
Brand Voice: Authentic, Refreshing
Output Language: English

**📁 Project Structure**
creative-agent-refactor/
├── cycls_agent.py          # Main Cycls agent with FastAPI
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables (gitignored)
├── .gitignore             # Git ignore rules
├── app/
│   ├── services/
│   │   ├── ai_service.py   # Campaign generation pipeline
│   │   ├── memory.py        # Persistent memory system
│   │   └── prompts.py       # LLM prompts for agents
│   └── utils/
│       └── helpers.py       # Utility functions
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # HTML templates
└── venv/                   # Virtual environment (gitignored)


**🔧 Configuration**

**Adjusting Agent Behavior**

Edit app/services/ai_service.py to modify:
    Number of critic loops (default: 2 attempts)
    Quality threshold (default: 7/10)
    Temperature settings (strategy: 0.7, copy: 0.85)
    Model selection (currently: gpt-4o-mini)

**Memory Settings**

The agent stores the last 8 campaigns by default. Modify in app/services/memory.py:

if len(_memory_store) > 8:  # Change this number
    _memory_store.pop(0)

**🚢 Deployment**

**Deploy to Cycls Cloud**

# Set your Cycls API key
export CYCLS_API_KEY=your-key-here

**🐛 Troubleshooting**

**Common Issues & Solutions**

**Issue***	                 **Solution**
ModuleNotFoundError:         No module named 'app.services'	Ensure app/__init__.py exists and you're using cycls run (not direct Python)
Error:                       templates/index.html not found	The agent includes fallback HTML - it will still work. Create templates/index.html for custom UI.
Docker not found	           Install Docker Desktop and ensure it's running
OpenAI API key invalid	     Check your .env file and ensure OPENAI_API_KEY is set correctly
Cycls API key error	         Only needed for deployment. For local development, it's optional.

**📊 Performance**
**Average response time:** 10-20 seconds
**Token usage:**           ~2000 tokens per campaign
**Cost per campaign:**     ~$0.01 (GPT-4o-mini)
**Concurrent users:**      Limited by OpenAI rate limits
