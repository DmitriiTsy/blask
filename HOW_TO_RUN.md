# 🚀 How to Run the Project

This guide explains how to run both the **frontend (Streamlit web app)** and **backend (CLI)** of the Blask project.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** created and activated
3. **Dependencies** installed (`pip install -r requirements.txt`)
4. **Environment variables** configured (`.env` file with API keys)

### Quick Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate    # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file with:
OPENAI_API_KEY=sk-your-key-here
SERPAPI_KEY=your-serpapi-key  # Optional but recommended
```

## 🌐 Option 1: Run Frontend (Web Interface) - RECOMMENDED

The frontend is a **Streamlit web application** that provides a user-friendly interface for all features.

### Method 1: Using the script (easiest)

```bash
./run_webapp.sh
```

### Method 2: Direct Streamlit command

```bash
streamlit run src/webapp.py
```

### Method 3: With custom port

```bash
streamlit run src/webapp.py --server.port 8501
```

### Access the Web Interface

Once started, the web app will be available at:
- **URL**: http://localhost:8501
- The browser should open automatically

### Features Available in Web Interface

1. **🔍 General Analysis Tab**
   - Enter queries about trends, competitors, statistics
   - See thinking process visualization
   - View formatted responses and visualizations

2. **🎯 Competitor Tracker Tab**
   - Track competitors for a brand
   - Monitor keywords and metrics
   - View detailed competitor analysis

3. **🌍 Market Intelligence Tab**
   - Analyze markets for multiple countries
   - View market size, platforms, opportunities
   - Legal/jurisdiction analysis

4. **📚 Knowledge Base Tab**
   - Upload documents (PDF, TXT, MD)
   - Documents are automatically indexed
   - Used automatically in all queries

## 💻 Option 2: Run Backend (CLI)

The backend can be run from the command line for programmatic access or testing.

### Method 1: Using the script

```bash
./run.sh "Your query here"
```

### Method 2: Direct Python command

```bash
# With query as argument
python3 -m src.main "What are the latest AI trends?"

# Interactive mode (will prompt for query)
python3 -m src.main
```

### Method 3: Using Python directly

```bash
python3 src/main.py "Your query here"
```

### Example CLI Queries

```bash
# Trend analysis
python3 -m src.main "Top 3 iGaming trends"

# Competitor analysis
python3 -m src.main "Find competitors for bet365"

# Market intelligence
python3 -m src.main "Analyze iGaming market in Spain"
```

## 🔄 Running Both Simultaneously

You can run both frontend and backend at the same time:

### Terminal 1: Frontend
```bash
./run_webapp.sh
# or
streamlit run src/webapp.py
```

### Terminal 2: Backend (CLI)
```bash
./run.sh "Your query"
# or
python3 -m src.main "Your query"
```

**Note**: The frontend and backend use the same codebase. The frontend is just a Streamlit wrapper around the backend graph execution.

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Make sure you're in the project root directory and virtual environment is activated.

```bash
cd /path/to/Blask
source venv/bin/activate
```

### Issue: "OPENAI_API_KEY not found"

**Solution**: Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Issue: Streamlit not found

**Solution**: Install Streamlit:

```bash
pip install streamlit
```

### Issue: Port 8501 already in use

**Solution**: Use a different port:

```bash
streamlit run src/webapp.py --server.port 8502
```

### Issue: ChromaDB errors (Knowledge Base)

**Solution**: Install ChromaDB:

```bash
pip install chromadb
```

## 📝 Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional but recommended
SERPAPI_KEY=your-serpapi-key

# Optional
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
GOOGLE_CSE_ID=your-cse-id
```

## 🎯 Quick Start Summary

```bash
# 1. Setup (one time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-your-key" > .env

# 2. Run Frontend (recommended)
./run_webapp.sh
# Open http://localhost:8501 in browser

# 3. Or Run Backend (CLI)
./run.sh "Your query"
```

## 📚 Additional Resources

- **README.md** - General project overview
- **INSTALL.md** - Detailed installation guide
- **ENV_VARIABLES.md** - Environment variables documentation
- **WEBAPP.md** - Web interface documentation
- **RUN_PROJECT.md** - CLI usage documentation

## ✅ Verification

To verify everything is working:

1. **Frontend**: Open http://localhost:8501 and try a query
2. **Backend**: Run `python3 -m src.main "test query"` and check for output

Both should execute the LangGraph workflow and return results.
