# DocuAssist AI - Comprehensive System Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Installation & Setup](#installation--setup)
4. [API Documentation](#api-documentation)
5. [System Components](#system-components)
6. [Deployment Guide](#deployment-guide)
7. [Monitoring & Logging](#monitoring--logging)
8. [User Guide](#user-guide)
9. [Development Roadmap](#development-roadmap)

---

## Executive Summary

**DocuAssist AI** is a production-grade RAG (Retrieval-Augmented Generation) customer support chatbot designed for small and mid-sized software companies (10-200 employees). 

### Key Features
- **Semantic Retrieval**: Vector-based document search using OpenAI embeddings
- **Intelligent Generation**: LLM-powered responses grounded in company documentation
- **Feedback Loop**: Continuous improvement through user ratings and weak supervision
- **High Performance**: Sub-2-second response latency optimized for user experience
- **Scalable Architecture**: Cloud-native design supporting growth from 100 to 10,000+ users

### Business Value
- Reduces repetitive support tickets by automatically answering common questions
- Decreases support agent burnout through intelligent ticket deflection
- Maintains consistent, accurate answers sourced from documentation
- Enables data-driven iteration based on user feedback

---

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Chat Interface - WebUI)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │              Router Endpoints                            │  │
│   │  • /api/chat/query          (Query Processing)          │  │
│   │  • /api/documents/upload    (Document Management)       │  │
│   │  • /api/feedback/submit     (Feedback Collection)       │  │
│   └──────────────────────────────────────────────────────────┘  │
└────────┬───────────────────────────────────────────────────┬────┘
         │                                                   │
         ▼                                                   ▼
    ┌─────────────────┐                            ┌──────────────────┐
    │  RAG Pipeline   │                            │  Logging/Metrics │
    │                 │                            │                  │
    │ • Retrieval     │                            │ • Query Logs     │
    │ • Generation    │                            │ • Performance    │
    │ • Feedback      │                            │ • Errors         │
    └────┬────────────┘                            └──────────────────┘
         │
    ┌────┴────────────────────────────────────┐
    │                                          │
    ▼                                          ▼
┌──────────────────────┐         ┌──────────────────────────┐
│  Vector Database     │         │   OpenAI API             │
│  (Pinecone)          │         │   • Embeddings           │
│                      │         │   • LLM Completion       │
│ • Semantic Search    │         │   • Model Selection      │
│ • Vector Storage     │         └──────────────────────────┘
│ • Approximate NN     │
└──────────────────────┘
```

### Core Pipeline

**RAG Pipeline Processing**:

1. **User Query** → 2. **Semantic Retrieval** → 3. **Context Assembly** → 4. **LLM Generation** → 5. **Response Refinement** → 6. **User Feedback**

#### Phase 1: Query Reception
- User submits natural language question
- Query ID generated for tracking
- User context retrieved from conversation history

#### Phase 2: Semantic Retrieval
- Query converted to dense vector using OpenAI embeddings
- Vector similarity search in Pinecone index
- Top-K most relevant documents retrieved (default K=3)
- Relevance scores indicate confidence (0-1 scale)

**Why Vector Search?**
- Captures semantic meaning beyond keyword matching
- Handles synonyms, paraphrasing, and conceptual similarity
- Approximate Nearest Neighbor (ANN) search enables scale
- Updated in O(1) without retraining models

#### Phase 3: Context Assembly
- Retrieved documents formatted with relevance indicators
- System prompt defines assistant behavior
- Context windows managed to prevent token overflow
- Retrieved information acts as "truth anchor"

#### Phase 4: LLM Generation
- LLM conditioned on retrieved context
- Probabilistic sequence modeling produces response
- Temperature and top-p tuned for quality vs. creativity
- Response grounded in documentation (reduces hallucination)

#### Phase 5: Response Quality Assurance
- LLM evaluation of own response quality
- Checks for unsupported claims
- Identifies confidence levels

#### Phase 6: Feedback & Iteration
- User rates response (1-5 stars)
- Optional text feedback collected
- Weak supervision signals logged
- Future: Fine-tuning and prompt optimization

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- OpenAI API Key
- Pinecone API Key
- Git (optional)

### Step 1: Clone Repository
```bash
cd d:\AI Capstone\Task
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy example to actual .env file
cp .env.example .env

# Edit .env with your API keys
# Required:
# - OPENAI_API_KEY=sk-...
# - PINECONE_API_KEY=...
# - PINECONE_ENVIRONMENT=...
```

### Step 5: Initialize Vector Database (Optional)
```bash
# If starting fresh, create sample documents
python scripts/init_samples.py
```

### Step 6: Start Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will be available at: `http://localhost:8000`

#### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

---

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
Currently supports anonymous requests. Production deployment should implement:
- API Key authentication
- JWT tokens
- OAuth2 with scopes

---

### Chat Endpoints

#### 1. POST `/chat/query`
Process user query through RAG pipeline.

**Request**:
```json
{
  "query": "How do I reset my password?",
  "user_id": "user_123",
  "system_prompt": null
}
```

**Response** (200 OK):
```json
{
  "query_id": "abc-123-def",
  "response": "To reset your password: 1) Go to login page 2) Click 'Forgot Password' 3) Enter email...",
  "retrieved_documents": [
    {
      "text": "Password reset instructions...",
      "relevance_score": 0.95
    }
  ],
  "metrics": {
    "retrieval_latency_ms": 45.2,
    "generation_latency_ms": 1250.5,
    "total_latency_ms": 1295.7,
    "document_count": 3
  },
  "success": true
}
```

**Parameters**:
- `query` (string, required): User's question (1-1000 chars)
- `user_id` (string, optional): User identifier for tracking
- `system_prompt` (string, optional): Custom behavior prompt

**Response Fields**:
- `query_id`: Unique ID for feedback tracking
- `response`: Generated answer
- `retrieved_documents`: Source documents with relevance scores
- `metrics`: Performance data
- `success`: Operation status

**Error Responses**:
- `400 Bad Request`: Empty or invalid query
- `500 Internal Server Error`: Processing failed

---

#### 2. GET `/chat/history/{user_id}`
Retrieve conversation history for a user (last 10 messages).

**Response** (200 OK):
```json
{
  "user_id": "user_123",
  "message_count": 5,
  "messages": [
    {
      "query": "How do I...",
      "response": "To...",
      "timestamp": 1672531200.0
    }
  ]
}
```

**Use Cases**:
- Multi-turn conversation context
- User engagement tracking
- Debugging conversation flows

---

#### 3. GET `/chat/health`
Check RAG pipeline health and vector store status.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "components": {
    "vector_store": {
      "status": "healthy",
      "total_vectors": 1250,
      "index_name": "docuassist"
    }
  }
}
```

---

### Document Endpoints

#### 1. POST `/documents/upload`
Upload and index documents for RAG system.

**Request**:
```json
{
  "documents": [
    {
      "id": "doc_password_reset",
      "text": "To reset your password:\n1. Visit the login page\n2. Click 'Forgot Password'...",
      "metadata": {
        "source": "help_docs",
        "category": "account",
        "version": "1.0"
      }
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "documents_indexed": 1,
  "message": "Successfully indexed 1 documents"
}
```

**Batch Upload**:
```json
{
  "documents": [
    { "id": "doc_1", "text": "...", "metadata": {} },
    { "id": "doc_2", "text": "...", "metadata": {} },
    { "id": "doc_3", "text": "...", "metadata": {} }
  ]
}
```

**Best Practices**:
- Each document should be 100-2000 words
- Use meaningful IDs for referencing
- Include metadata for filtering/tracing
- Keep documents focused on single topics

---

#### 2. DELETE `/documents/{doc_id}`
Remove document from vector store.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Document doc_123 deleted"
}
```

---

#### 3. GET `/documents/health`
Check document store (vector database) status.

**Response**:
```json
{
  "status": "healthy",
  "total_vectors": 5000,
  "index_name": "docuassist"
}
```

---

### Feedback Endpoints

#### 1. POST `/feedback/submit`
Submit user feedback on response quality.

**Request**:
```json
{
  "query_id": "abc-123-def",
  "user_id": "user_123",
  "rating": 4,
  "feedback_text": "Response was helpful but could include more examples"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Feedback recorded: 4/5"
}
```

**Rating Scale**:
- **1**: Poor - Inaccurate, unhelpful, or misleading
- **2**: Below Average - Some issues with accuracy
- **3**: Average - Acceptable but could be better
- **4**: Good - Helpful and reasonably accurate
- **5**: Excellent - Accurate, comprehensive, well-explained

**Feedback Processing**:
- Logged with timestamp and user ID
- Used for quality metrics
- Weak supervision signals for improvement
- Enables A/B testing

---

#### 2. GET `/feedback/metrics`
Aggregate feedback statistics.

**Response** (200 OK):
```json
{
  "message": "Metrics aggregation coming in v1.1",
  "metrics": {
    "average_rating": "TBD",
    "feedback_count": "TBD",
    "improvement_areas": "TBD"
  }
}
```

---

## System Components

### 1. Vector Store (`app/rag/vector_store.py`)

**Responsibility**: Semantic document retrieval

**Key Methods**:
- `get_embedding(text)` - Convert text to vector using OpenAI
- `add_documents(documents)` - Index docs in Pinecone
- `retrieve(query, top_k=3)` - Search for relevant documents
- `health_check()` - Monitor vector store status

**Technology**: Pinecone (managed vector database)

**Why Pinecone?**
- Handles high-dimensional ANN search at scale
- Automatic sharding and replication
- Real-time index updates
- Built-in monitoring and metrics

---

### 2. Generation Engine (`app/rag/generation.py`)

**Responsibility**: LLM-powered response generation

**Key Methods**:
- `generate_response(query, context_documents)` - Produce grounded response
- `evaluate_response_quality(query, response, context)` - Check for hallucinations
- `_build_context(documents)` - Format retrieved docs

**Technology**: OpenAI GPT-3.5-Turbo (or GPT-4)

**Configuration**:
- `temperature=0.7`: Balance between determinism and creativity
- `max_tokens=500`: Prevent unnecessarily long responses
- `top_p=0.95`: Nucleus sampling for quality

**Prompt Engineering**:
```
System: You are DocuAssist, an AI customer support assistant...
User: Context: [Retrieved Documents]
      Question: [User Query]

LLM responds with grounded, factual answer based only on context.
```

---

### 3. RAG Pipeline (`app/rag/pipeline.py`)

**Responsibility**: Orchestrate retrieval + generation + feedback

**Core Process**:
```
User Query
    ↓
[Retrieve Documents]
    ↓
[Assembly + Context]
    ↓
[Generate Response]
    ↓
[Format Output]
    ↓
[Collect Feedback]
    ↓
[Log Metrics]
```

**Features**:
- Conversation history tracking
- Query-response pairing with IDs
- Latency measurement and logging
- Error handling and graceful degradation

---

### 4. API Layer (`app/api/`)

**Components**:
- `chat.py` - Query and conversation endpoints
- `documents.py` - Document management
- `feedback.py` - User feedback collection

**Framework**: FastAPI
- Async/await for non-blocking I/O
- Automatic OpenAPI documentation
- Built-in validation with Pydantic
- CORS middleware for frontend integration

---

### 5. Frontend (`frontend/`)

**Architecture**:
- **HTML**: Semantic markup with accessibility
- **CSS**: Responsive design (mobile-first)
- **JavaScript**: Vanilla JS (no framework dependency)

**Key Features**:
- Real-time message streaming
- Performance metrics display
- Source document visibility
- User feedback rating system
- System health indicators
- Toast notifications

**Browser Compatibility**:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers

---

## Deployment Guide

### Local Development
```bash
# Terminal 1: Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Open frontend (optional simple server)
cd frontend
python -m http.server 8080
```

### Docker Deployment

**Dockerfile** (create in project root):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run**:
```bash
docker build -t docuassist-ai .
docker run -p 8000:8000 --env-file .env docuassist-ai
```

### Cloud Deployment (AWS Lambda / Google Cloud Run)

Suitable for serverless deployment with:
- API Gateway for routing
- Managed vector store (Pinecone)
- CloudWatch for logging
- DynamoDB for feedback storage

---

## Monitoring & Logging

### Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for issues
- `ERROR`: Error messages with context

### Log Format
```
2024-01-15 14:32:45,123 - docuassist - INFO - QUERY | USER: user_123 | TEXT: How do I...
2024-01-15 14:32:45,245 - docuassist - INFO - RETRIEVAL | QUERY: ... | RESULTS: 3 | LATENCY: 120ms
2024-01-15 14:32:46,500 - docuassist - INFO - GENERATION | LATENCY: 1250.5ms | TOKENS: 150
2024-01-15 14:32:46,502 - docuassist - INFO - FEEDBACK | USER: user_123 | RATING: 5
```

### Key Metrics

**Query Metrics**:
- Retrieval Latency: Sub-200ms target
- Generation Latency: Sub-2000ms target
- Total Latency: Sub-2500ms SLA

**Quality Metrics**:
- Average Feedback Rating: Target >4.0/5
- Hallucination Rate: Target <5%
- User Satisfaction: Target >85%

**System Health**:
- Vector Store Status: Up/Down
- LLM API Availability: Up/Down
- Error Rate: <1% target

### Monitoring Tools Integration
- **CloudWatch** (AWS): For logs and metrics
- **Datadog**: APM and distributed tracing
- **New Relic**: Application performance monitoring
- **Prometheus + Grafana**: Self-hosted monitoring

---

## User Guide

### For End Users

#### Getting Started
1. Open chat interface: `http://localhost:8000` (frontend)
2. Type your question in the input field
3. Press Send or Enter
4. Wait for AI response (typically <2.5 seconds)
5. Rate the response to improve system

#### Tips for Best Results
- **Be Specific**: "How do I reset password?" works better than "password"
- **Ask One Question**: One question per query for focused answers
- **Use Natural Language**: Don't try to use keywords, just ask naturally
- **Check Sources**: Review retrieved documents to understand answers

#### Rating System
- 👍 **5 Stars**: Excellent, accurate, comprehensive
- 👍 **4 Stars**: Good, helpful with minor issues
- 👌 **3 Stars**: Acceptable, basic answer
- 👎 **2 Stars**: Below average, some issues
- 👎 **1 Star**: Poor, inaccurate or unhelpful

---

### For Support Managers

#### Monitoring Dashboard
View in logs/metrics:
- Daily query volume
- Average user satisfaction rating
- Top questions asked
- Common improvement areas

#### Decision Framework
- **High Rating (4-5 stars)**: Keep document as-is
- **Medium Rating (3 stars)**: Review for clarity/completeness
- **Low Rating (1-2 stars)**: Update documentation or rewrite

#### Continuous Improvement
1. Review feedback weekly
2. Identify top response issues
3. Update relevant documentation
4. Re-index updated documents
5. Monitor impact on new ratings

---

## Development Roadmap

### Version 1.1 (Next Quarter)
- [ ] Feedback metrics aggregation dashboard
- [ ] Multi-language support (Spanish, French, German)
- [ ] Fine-tuning pipeline for custom models
- [ ] Webhook integration for external systems
- [ ] Advanced filtering (category, date range)

### Version 1.2
- [ ] Hybrid search (keyword + semantic)
- [ ] Citation tracking with source links
- [ ] Conversation summarization
- [ ] Suggested follow-up questions
- [ ] Analytics dashboard for admins

### Version 2.0 (Long-term)
- [ ] Multi-model ensemble (combining LLMs)
- [ ] Knowledge graph integration
- [ ] Real-time document sync
- [ ] Voice/audio input support
- [ ] Mobile app (iOS/Android)
- [ ] Enterprise SSO integration

---

## Troubleshooting

### Issue: "No relevant documents found"
**Cause**: Vector index is empty or query is too specific
**Solution**: 
1. Upload sample documents using `/documents/upload`
2. Rephrase query more broadly
3. Check Pinecone index status

### Issue: High latency (>5 seconds)
**Cause**: LLM API rate limiting or slow retrieval
**Solution**:
1. Check OpenAI API status
2. Reduce top_k parameter
3. Use GPT-3.5-turbo instead of GPT-4

### Issue: Hallucinated responses
**Cause**: Context too broad or system prompt too loose
**Solution**:
1. Improve document chunking
2. Add stricter system prompt
3. Lower temperature parameter

### Issue: CORS errors in frontend
**Cause**: Backend not allowing frontend origin
**Solution**:
1. Check CORS middleware in app/main.py
2. Add frontend URL to allowed_origins
3. Verify backend is running

---

## Contributing

To contribute to DocuAssist:

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Run test suite: `pytest tests/`
4. Submit pull request with description

---

## License

DocuAssist AI is licensed under MIT License.

---

## Support

For issues or questions:
- Create issue in GitHub repository
- Email: support@docuassist.ai
- Documentation: https://docs.docuassist.ai

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Maintained By**: DocuAssist Team
