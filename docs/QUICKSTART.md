# DocuAssist AI - Getting Started Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# PINECONE_API_KEY=your_key_here
# PINECONE_ENVIRONMENT=your_environment
```

### 3. Start Backend Server
```bash
python -m uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

### 4. Open Frontend (In another terminal)
```bash
cd frontend
python -m http.server 8000  # or use any HTTP server
```

Frontend at: http://localhost:8000

### 5. Add Sample Documents
```bash
# POST request to upload documents
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc_1",
        "text": "To reset your password: 1) Go to login 2) Click Forgot Password 3) Follow email instructions",
        "metadata": {"source": "help_docs", "category": "account"}
      }
    ]
  }'
```

### 6. Test Chat
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "user_id": "test_user"
  }'
```

---

## Project Structure

```
d:\AI Capstone\Task\
├── app/                          # Main application code
│   ├── main.py                   # FastAPI app setup
│   ├── config.py                 # Configuration management
│   ├── api/                      # API endpoints
│   │   ├── chat.py              # Chat endpoints
│   │   ├── documents.py         # Document management
│   │   └── feedback.py          # Feedback collection
│   ├── rag/                      # RAG pipeline components
│   │   ├── vector_store.py      # Semantic retrieval
│   │   ├── generation.py        # LLM response generation
│   │   └── pipeline.py          # RAG orchestration
│   ├── schemas/                  # Pydantic data models
│   │   └── models.py            # Request/response schemas
│   └── utils/                    # Utilities
│       └── logger.py            # Logging configuration
├── frontend/                     # Web interface
│   ├── index.html               # Chat UI
│   ├── script.js                # Frontend logic
│   └── styles.css               # Styling
├── tests/                        # Test suite
│   ├── test_api.py              # API tests
│   └── test_rag_pipeline.py     # RAG tests
├── docs/                         # Documentation
│   ├── SYSTEM_DOCUMENTATION.md  # Full docs
│   ├── API.md                   # API reference
│   └── QUICKSTART.md            # This file
├── requirements.txt             # Python dependencies
├── .env.example                # Configuration template
└── README.md                    # Project overview
```

---

## Key Concepts

### RAG (Retrieval-Augmented Generation)
Combines semantic document search with LLM generation:
1. **Retrieve**: Find relevant docs using vector similarity
2. **Augment**: Add retrieved docs as context
3. **Generate**: LLM produces response based on context

### Vector Embeddings
- Documents and queries converted to high-dimensional vectors
- Similar meaning = similar vectors
- Pinecone stores and searches these vectors efficiently

### Pipeline Flow
```
User Query 
  → Convert to vector 
  → Search Pinecone 
  → Get top 3 docs 
  → Prompt LLM with docs 
  → Generate response 
  → User rates it
```

---

## Common Tasks

### Upload New Documents
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "billing_faq",
        "text": "Billing FAQ content...",
        "metadata": {"source": "help_docs", "category": "billing"}
      },
      {
        "id": "refund_policy",
        "text": "Refund policy text...",
        "metadata": {"source": "policies"}
      }
    ]
  }'
```

### Query the System
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is your refund policy?",
    "user_id": "john@example.com"
  }'
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "abc-123-def",
    "user_id": "user_123",
    "rating": 5,
    "feedback_text": "Great response!"
  }'
```

### Check System Health
```bash
curl http://localhost:8000/api/health
```

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

---

## Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=sk-...              # OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo         # LLM model
EMBEDDING_MODEL=text-embedding-3-small

PINECONE_API_KEY=...               # Pinecone API key
PINECONE_ENVIRONMENT=...           # Pinecone region
PINECONE_INDEX_NAME=docuassist     # Index name

LOG_LEVEL=INFO                     # Logging level
ENVIRONMENT=development            # Dev/Prod
```

---

## Performance Tuning

### Response Latency
- **Target**: <2.5 seconds end-to-end
- **Breakdown**:
  - Embedding: ~50ms
  - Vector search: ~100ms
  - LLM generation: ~1500-2000ms
  - Network: ~50-100ms

### Optimization Tips
1. Reduce `top_k` if latency is high
2. Use gpt-3.5-turbo instead of gpt-4
3. Lower `max_tokens` for shorter responses
4. Batch queries during low-traffic periods

### Quality vs Speed
- Increase `temperature` for more creative responses
- Decrease for more consistent/factual answers
- Longer `max_tokens` = more detailed responses

---

## Troubleshooting

### Module Import Errors
```bash
# Verify venv is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### API Key Issues
```bash
# Verify keys in .env
cat .env

# Test OpenAI key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Pinecone
curl -H "api-key: $PINECONE_API_KEY" \
  https://...pinecone.io/describe_index_stats
```

### Port Already in Use
```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or kill existing process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Vector Store Empty
- Check Pinecone index status
- Upload sample documents
- Verify PINECONE_INDEX_NAME matches

---

## Next Steps

1. **Customize System Prompt**: Edit `app/rag/generation.py`
2. **Add Your Documents**: Upload via `/documents/upload` endpoint
3. **Tune Parameters**: Adjust in `app/config.py`
4. **Integrate Frontend**: Customize HTML/CSS in `frontend/`
5. **Deploy**: See [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)

---

## Resources

- [Full System Documentation](SYSTEM_DOCUMENTATION.md)
- [API Reference](API.md)
- [OpenAI Docs](https://platform.openai.com/docs)
- [Pinecone Quickstart](https://docs.pinecone.io)
- [FastAPI Tutorial](https://fastapi.tiangolo.com)

---

**Questions?** Check the troubleshooting section or see full documentation.
