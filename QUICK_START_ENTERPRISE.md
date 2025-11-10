# Enterprise AI Memory Platform - Quick Start Guide

## 🚀 New Features Added

### 1. RAG Pipeline ✅
Complete Retrieval Augmented Generation pipeline with reranking:
- `/api/rag/query` - Complete RAG query (retrieve + generate)
- `/api/rag/retrieve` - Retrieve memories with reranking
- `/api/rag/generate` - Generate response from context

**Features:**
- ✅ Semantic search with ChromaDB
- ✅ Cross-encoder reranking (BGE or Cohere)
- ✅ Multi-LLM support (OpenAI GPT-4, Claude, etc.)
- ✅ Citation tracking
- ✅ Hybrid scoring (semantic + rerank)

### 2. Voice Capabilities 🎤
Speech-to-text and text-to-speech:
- `/api/voice/stt` - Convert speech to text
- `/api/voice/tts` - Convert text to speech
- `/api/voice/voice-memory` - Create memory from voice
- `/api/voice/voice-rag` - Complete voice-to-voice RAG

**Features:**
- ✅ OpenAI Whisper (STT)
- ✅ OpenAI TTS / Google TTS
- ✅ Voice memory creation
- ✅ Voice RAG queries

### 3. Enterprise Authentication 🔐
JWT-based authentication with API keys:
- `/api/auth/register` - User registration
- `/api/auth/login` - Login and get tokens
- `/api/auth/me` - Get current user info
- `/api/auth/api-keys` - Generate API keys

**Features:**
- ✅ JWT tokens (access + refresh)
- ✅ API key generation
- ✅ Password hashing (bcrypt)
- ✅ User management

## 📦 Installation

```bash
# Install new dependencies
pip install -r requirements.txt

# Install Whisper (optional, for local STT)
pip install openai-whisper

# Install FFmpeg (required for Whisper)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
```

## 🔧 Configuration

Update `.env` file:

```bash
# OpenAI (required for RAG and voice)
OPENAI_API_KEY=your_openai_api_key

# Cohere (optional, for reranking)
COHERE_API_KEY=your_cohere_api_key

# Existing configs...
NEO4J_PASSWORD=memmachine_password
```

## 🧪 Testing the Features

### RAG Query
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "retrieval_limit": 10,
    "rerank": true,
    "model": "gpt-4"
  }'
```

### Voice STT
```bash
curl -X POST http://localhost:8000/api/voice/stt \
  -F "audio=@audio.webm"
```

### Voice RAG
```bash
curl -X POST http://localhost:8000/api/voice/voice-rag \
  -F "audio=@question.webm" \
  -F "model=gpt-4"
```

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'

# Use token
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🎯 Next Steps

1. **Multi-tenancy**: Add workspace/organization support
2. **Rate limiting**: Implement per-user/org limits
3. **Analytics**: Usage tracking and monitoring
4. **Billing**: Usage-based pricing integration
5. **Advanced RAG**: Multi-vector embeddings, hybrid search
6. **Frontend**: React components for voice and RAG

## 💡 Enterprise Features Roadmap

See `ENTERPRISE_FEATURES.md` for complete roadmap.

## 🔗 Related Files

- `app/services/rag_service.py` - RAG pipeline implementation
- `app/services/voice_service.py` - Voice STT/TTS service
- `app/services/auth_service.py` - Authentication service
- `app/api/rag.py` - RAG API endpoints
- `app/api/voice.py` - Voice API endpoints
- `app/api/auth.py` - Auth API endpoints

