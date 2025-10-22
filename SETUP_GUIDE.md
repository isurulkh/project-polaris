# Project Polaris - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup (Mac M4 Pro)](#local-development-setup)
3. [Environment Configuration](#environment-configuration)
4. [Running the System](#running-the-system)
5. [Testing](#testing)
6. [Cloud Deployment](#cloud-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Python 3.10+** (M4 Pro optimized)
- **Homebrew** (Mac package manager)
- **Git**
- **Docker Desktop** (for containerized deployment)

### Required Accounts & API Keys
1. **Google AI Studio Account**
   - Sign up at: https://makersuite.google.com/
   - Generate API key
   
2. **Supabase Account**
   - Your existing Supabase project with PGVector
   - Database URL from n8n workflow setup

---

## 💻 Local Development Setup (Mac M4 Pro)

### Step 1: Install System Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11 (optimized for M4 Pro)
brew install python@3.11

# Install PostgreSQL client (for database tools)
brew install postgresql@15

# Install Redis (for caching)
brew install redis
brew services start redis

# Verify installations
python3.11 --version
psql --version
redis-cli ping
```

### Step 2: Clone and Setup Project

```bash
# Create project directory
mkdir -p ~/Projects/project-polaris
cd ~/Projects/project-polaris

# Initialize git repository (if starting from scratch)
git init

# Create virtual environment (M4-optimized)
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 3: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# For development, install additional tools
pip install black ruff mypy pytest pytest-cov pytest-asyncio
```

### Step 4: Project Structure Setup

```bash
# Create all necessary directories
mkdir -p config src/{core,agents,rag,chains,tools,prompts,utils,api/routes,api/middleware}
mkdir -p ui cli tests scripts monitoring/grafana/dashboards docs

# Create __init__.py files
find src -type d -exec touch {}/__init__.py \;
touch config/__init__.py
```

---

## 🔐 Environment Configuration

### Step 1: Create .env File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### Step 2: Configure Supabase Connection

**Your DATABASE_URL format:**
```bash
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres"
```

**Get your Supabase credentials:**
1. Go to your Supabase dashboard
2. Click on Project Settings > Database
3. Copy the "URI" connection string
4. Replace YOUR_PASSWORD with your actual password

### Step 3: Configure Google Gemini API

```bash
# Get your API key from:
# https://makersuite.google.com/app/apikey

GOOGLE_API_KEY="your_actual_api_key_here"
```

### Step 4: Verify Configuration

```bash
# Test database connection
python scripts/test_connection.py

# Should output:
# ✅ Database connection successful
# ✅ Vector store accessible
# ✅ Google Gemini API working
```

---

## 🚀 Running the System

### Method 1: Run API Server (FastAPI)

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at:
# http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Method 2: Run Streamlit UI

```bash
# In a new terminal, activate venv
source venv/bin/activate

# Run Streamlit app
streamlit run ui/streamlit_app.py --server.port 8501

# UI will open automatically at:
# http://localhost:8501
```

### Method 3: Run Both (Recommended)

```bash
# Terminal 1: API Server
source venv/bin/activate
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Streamlit UI
source venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501
```

### Method 4: Docker Compose (Production-like)

```bash
# Build and run with Docker
docker-compose up --build

# Access:
# API: http://localhost:8000
# UI: http://localhost:8501
# Prometheus: http://localhost:9090
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents/test_query_agent.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

### Manual API Testing

```bash
# Test query endpoint
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "include_sources": true
  }'

# Test summary endpoint
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize Q4 results",
    "summary_type": "executive"
  }'

# Test health endpoint
curl http://localhost:8000/api/v1/health
```

---

## ☁️ Cloud Deployment

### Option 1: Railway.app (Recommended)

```bash
# Install Railway CLI
brew install railway

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set GOOGLE_API_KEY="your_key"
railway variables set DATABASE_URL="your_supabase_url"

# Deploy
railway up

# Get deployment URL
railway domain
```

### Option 2: Google Cloud Run

```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/polaris-api

# Deploy
gcloud run deploy polaris-api \
  --image gcr.io/YOUR_PROJECT_ID/polaris-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key,DATABASE_URL=your_db_url
```

### Option 3: AWS ECS (Production)

```bash
# Install AWS CLI
brew install awscli

# Configure AWS
aws configure

# Create ECR repository
aws ecr create-repository --repository-name project-polaris

# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker build -t project-polaris .
docker tag project-polaris:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/project-polaris:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/project-polaris:latest

# Create ECS task definition and service
# (Use AWS Console or Terraform for this)
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Error: connection refused
# Solution: Check Supabase project is running and URL is correct

# Test connection manually:
psql postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres

# Check if pgvector extension exists:
\dx pgvector
```

#### 2. Google API Key Error
```bash
# Error: API key not valid
# Solution: Regenerate API key at https://makersuite.google.com/app/apikey

# Test API key:
python scripts/test_gemini_api.py
```

#### 3. Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated and dependencies installed

source venv/bin/activate
pip install -r requirements.txt
```

#### 4. M4 Pro Specific Issues
```bash
# If you encounter architecture issues with some packages:
pip install --no-binary :all: package-name

# For TensorFlow/ML packages on M4:
pip install tensorflow-macos tensorflow-metal
```

#### 5. Port Already in Use
```bash
# Error: Address already in use
# Solution: Kill process using port

# Find process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn src.api.main:app --port 8001
```

### Performance Tuning for M4 Pro

```bash
# Set environment variables for optimal performance
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=12  # M4 Pro has 12 performance cores
export MKL_NUM_THREADS=12
```

### Logging and Debugging

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# View logs
tail -f logs/polaris.log

# Or use systemlog on Mac
log stream --predicate 'process == "python3"' --level debug
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **System Info**: http://localhost:8000/api/v1/system/info
- **Health Check**: http://localhost:8000/api/v1/health/detailed
- **Prometheus Metrics**: http://localhost:9090/metrics

---

## 🎯 Next Steps

1. **Test the System**
   ```bash
   # Run quick test
   python scripts/quick_test.py
   ```

2. **Configure n8n Integration**
   - Ensure n8n workflow is running
   - Verify documents are being embedded
   - Check vector database population

3. **Customize Prompts**
   - Edit `src/prompts/*.py` files
   - Adjust temperature and parameters in `config/settings.py`

4. **Monitor Performance**
   - Access Prometheus metrics
   - Set up Grafana dashboards
   - Configure alerting

5. **Scale for Production**
   - Enable Redis caching
   - Configure load balancing
   - Set up auto-scaling
   - Implement proper authentication

---

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Examine logs in `logs/` directory

Happy coding! 🚀