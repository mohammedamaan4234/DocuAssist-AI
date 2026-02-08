# DocuAssist AI - REST API Reference

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently supports anonymous requests. Add API keys for production.

---

## Chat Endpoints

### POST /chat/query
**Process user query through RAG pipeline**

**Request:**
```json
{
  "query": "How do I reset my password?",
  "user_id": "user_123",
  "system_prompt": null
}
```

**Response (200):**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "To reset your password:\n1. Go to the login page\n2. Click 'Forgot Password'\n3. Enter your email address\n4. Check your inbox for reset link\n5. Follow the link and create new password",
  "retrieved_documents": [
    {
      "text": "Password Reset Guide: To reset your password...",
      "relevance_score": 0.95
    },
    {
      "text": "Account Recovery Options: If you can't access your email...",
      "relevance_score": 0.82
    }
  ],
  "metrics": {
    "retrieval_latency_ms": 45.2,
    "generation_latency_ms": 1250.5,
    "total_latency_ms": 1295.7,
    "document_count": 2
  },
  "success": true
}
```

**Error (400):**
```json
{
  "detail": "Query cannot be empty"
}
```

**Error (500):**
```json
{
  "detail": "Query processing failed"
}
```

**Parameters:**
- `query` (required): User question (1-1000 characters)
- `user_id` (optional): Identifier for feedback tracking
- `system_prompt` (optional): Custom behavior definition

**Response Fields:**
- `query_id`: Unique identifier for this query (use for feedback)
- `response`: Generated answer
- `retrieved_documents`: Source documents with scores
- `metrics`: Performance data
- `success`: Boolean status

---

### GET /chat/history/{user_id}
**Retrieve conversation history for a user**

**Response (200):**
```json
{
  "user_id": "user_123",
  "message_count": 3,
  "messages": [
    {
      "query": "How do I reset my password?",
      "response": "To reset your password...",
      "timestamp": 1672531200.0
    },
    {
      "query": "What's your refund policy?",
      "response": "Our refund policy allows...",
      "timestamp": 1672531400.0
    }
  ]
}
```

**Parameters:**
- `user_id` (required): User identifier

**Notes:**
- Returns last 10 messages
- Useful for multi-turn conversations
- Enables context from previous queries

---

### GET /chat/health
**Check RAG pipeline health status**

**Response (200):**
```json
{
  "status": "healthy",
  "components": {
    "vector_store": {
      "status": "healthy",
      "total_vectors": 5000,
      "index_name": "docuassist"
    }
  }
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some issues but still functioning
- `unhealthy`: Critical system down

---

## Document Endpoints

### POST /documents/upload
**Upload and index documents**

**Request:**
```json
{
  "documents": [
    {
      "id": "password_reset_guide",
      "text": "How to Reset Your Password\n\nStep 1: Go to login page\nStep 2: Click 'Forgot Password'\nStep 3: ...",
      "metadata": {
        "source": "help_docs",
        "category": "account",
        "version": "1.2",
        "updated_date": "2024-01-15"
      }
    },
    {
      "id": "billing_faq",
      "text": "Billing FAQs\n\nQ: How am I charged?\nA: We charge monthly...",
      "metadata": {
        "source": "faq",
        "category": "billing"
      }
    }
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "documents_indexed": 2,
  "message": "Successfully indexed 2 documents"
}
```

**Error (400):**
```json
{
  "detail": "No documents provided"
}
```

**Parameters:**
- `documents` (required): Array of document objects
  - `id` (required): Unique document identifier
  - `text` (required): Document content (will be embedded)
  - `metadata` (optional): Key-value pairs for context

**Best Practices:**
- Documents: 100-2000 words each
- Clear, well-written content
- Logical chunking by topic
- Include metadata for filtering
- Update documents regularly

---

### DELETE /documents/{doc_id}
**Delete document from vector store**

**Response (200):**
```json
{
  "success": true,
  "message": "Document password_reset_guide deleted"
}
```

**Parameters:**
- `doc_id` (required): Document ID to delete

**Notes:**
- Immediate removal from index
- Cannot be undone
- Queries won't retrieve deleted docs

---

### GET /documents/health
**Check document store status**

**Response (200):**
```json
{
  "status": "healthy",
  "total_vectors": 5000,
  "index_name": "docuassist"
}
```

---

## Feedback Endpoints

### POST /feedback/submit
**Submit user feedback on response quality**

**Request:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "rating": 5,
  "feedback_text": "Response was accurate and helpful"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Feedback recorded: 5/5"
}
```

**Error (400):**
```json
{
  "detail": "Rating must be between 1 and 5"
}
```

**Parameters:**
- `query_id` (required): ID from original query response
- `user_id` (required): User identifier
- `rating` (required): 1-5 star rating
- `feedback_text` (optional): Text feedback (max 500 chars)

**Rating Legend:**
| Rating | Meaning | Action |
|--------|---------|--------|
| 5 | Excellent - Accurate, comprehensive | Keep as-is |
| 4 | Good - Helpful with minor issues | Monitor |
| 3 | Average - Basic answer | Review content |
| 2 | Poor - Some inaccuracies | Update docs |
| 1 | Very Poor - Unusable response | Urgent review |

---

### GET /feedback/metrics
**Get aggregate feedback statistics**

**Response (200):**
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

**Note:** Meta endpoint in development for v1.1

---

## Health Endpoints

### GET /
**Root endpoint with API information**

**Response (200):**
```json
{
  "name": "DocuAssist AI",
  "version": "1.0.0",
  "description": "RAG-based Customer Support Chatbot",
  "endpoints": {
    "documentation": "/api/docs",
    "openapi": "/api/openapi.json",
    "health": "/api/health"
  }
}
```

---

### GET /api/health
**General health check**

**Response (200):**
```json
{
  "status": "healthy",
  "service": "DocuAssist AI",
  "version": "1.0.0"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Query processed successfully |
| 400 | Bad Request | Empty query, invalid rating |
| 401 | Unauthorized | Invalid API key (future) |
| 404 | Not Found | User ID not found |
| 500 | Server Error | LLM unavailable, DB connection error |

### Error Response Format
```json
{
  "detail": "Descriptive error message"
}
```

### Common Errors

**Empty Query**
```json
{
  "detail": "Query cannot be empty"
}
```

**Invalid Rating**
```json
{
  "detail": "Rating must be between 1 and 5"
}
```

**Service Unavailable**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting (Future)

Production deployment will include:
- Per-user rate limits (100 req/hour)
- Per-IP throttling (1000 req/hour)
- Burst allowance (10 req/second)
- Queue for excess requests

---

## Examples

### Using cURL

**Query:**
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I cancel my subscription?",
    "user_id": "john@example.com"
  }'
```

**Upload Documents:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "id": "cancel_guide",
      "text": "To cancel your subscription...",
      "metadata": {"source": "help_docs"}
    }]
  }'
```

**Submit Feedback:**
```bash
curl -X POST http://localhost:8000/api/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "john@example.com",
    "rating": 5,
    "feedback_text": "Perfect answer!"
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Query
response = requests.post(
    f"{BASE_URL}/chat/query",
    json={
        "query": "How do I reset my password?",
        "user_id": "user_123"
    }
)
print(response.json())

# Upload documents
documents = [
    {
        "id": "doc_1",
        "text": "Documentation content",
        "metadata": {"source": "help"}
    }
]
response = requests.post(
    f"{BASE_URL}/documents/upload",
    json={"documents": documents}
)
print(response.json())
```

### Using JavaScript

```javascript
async function askQuestion(query) {
  const response = await fetch('http://localhost:8000/api/chat/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      user_id: 'user_123'
    })
  });
  
  const data = await response.json();
  console.log('Response:', data.response);
  console.log('Latency:', data.metrics.total_latency_ms, 'ms');
  return data;
}
```

---

## OpenAPI Documentation

Interactive documentation available at:
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/openapi.json`

---

**API Version:** 1.0.0  
**Last Updated:** 2024-01-15
