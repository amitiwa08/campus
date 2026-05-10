"""
AI Demo Script - 8 Minute Presentation
Day 16: AI Developer 2 - Demo preparation
"""

# ============================================================================
# DEMO DAY SCRIPT - AI SERVICE SEGMENT (2 minutes total)
# ============================================================================

# SETUP (Before Demo):
# 1. Ensure Flask AI service is running on port 5000
# 2. Redis should be running for caching
# 3. Groq API key must be active with sufficient credits
# 4. Open Terminal 1: `python app.py` from ai-service folder
# 5. Open Terminal 2: Ready for curl requests or Postman

# ============================================================================
# SEGMENT 1: AI RECOMMEND (30 seconds)
# ============================================================================

"""
SCRIPT TO SAY:
"The AI service provides intelligent recommendations powered by Groq's
LLaMA model. Let me show you the /recommend endpoint in action."

ACTION:
- Show Flask app running in terminal (port 5000)
- Open Postman or Terminal with curl ready

LIVE DEMO:

curl -X POST http://localhost:5000/api/ai/categorise \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our organization needs to ensure GDPR compliance for EU customers. We process personal data including names, emails, and location data. We need policies for data retention, consent management, and data subject rights."
  }'

EXPECTED RESPONSE (show in 2 seconds):
{
  "category": "Data Privacy",
  "confidence": 0.98,
  "reasoning": "Directly references GDPR, personal data processing, and compliance requirements",
  "meta": {
    "model_used": "llama-3.3-70b-versatile",
    "tokens_used": 64,
    "response_time_ms": 2341,
    "cached": false,
    "is_fallback": false
  }
}

SAY: "The AI classified this as Data Privacy with 98% confidence.
Notice the response includes model name, token count, and response time."
"""


# ============================================================================
# SEGMENT 2: GENERATE REPORT (45 seconds)
# ============================================================================

"""
SCRIPT TO SAY:
"Next, let's generate a comprehensive compliance report. This endpoint
uses prompt engineering to create structured, actionable reports."

ACTION:
- Show health endpoint first to prove service is alive
- Then call generate-report

LIVE DEMO 1 - Health Check (fast):

curl http://localhost:5000/api/ai/health

RESPONSE:
{
  "status": "healthy",
  "model": "llama-3.3-70b-versatile",
  "last_response_time_ms": 2341,
  "chroma_doc_count": 10,
  "cache_stats": {
    "hits": 2,
    "misses": 1,
    "hit_rate": "66.7%",
    "redis_connected": true
  },
  "uptime_minutes": 5.2
}

SAY: "The health check shows we have 10 documents in ChromaDB,
cache is working with 66.7% hit rate, and the system is healthy."

LIVE DEMO 2 - Generate Report:

curl -X POST http://localhost:5000/api/ai/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Data Protection for Remote Workers",
    "department": "IT Security",
    "context": "We just adopted full remote work policy and need to train employees on security"
  }'

EXPECTED RESPONSE (in 5-6 seconds):
{
  "title": "Data Protection Framework for Remote Workers",
  "executive_summary": "Remote work requires enhanced data protection measures...",
  "overview": "Detailed explanation of securing data in remote environments...",
  "key_points": [
    "VPN usage mandatory for all network access",
    "End-to-end encryption for sensitive data",
    "Multi-factor authentication on all systems",
    "Regular security awareness training"
  ],
  "compliance_requirements": [
    "GDPR Article 32 security measures",
    "ISO 27001 remote access controls",
    "Company data protection policy"
  ],
  "recommendations": [
    "Deploy MDM for device management",
    "Implement DLP solutions",
    "Conduct security audits monthly"
  ],
  "resources": [
    "Remote Work Security Guide",
    "VPN Configuration Manual",
    "Incident Response Procedure"
  ],
  "meta": {
    "model_used": "llama-3.3-70b-versatile",
    "tokens_used": 512,
    "response_time_ms": 5123,
    "cached": false,
    "is_fallback": false
  }
}

SAY: "The report was generated in 5 seconds with 512 tokens used.
It's structured, professional, and immediately actionable."
"""


# ============================================================================
# SEGMENT 3: RAG QUERY (30 seconds)
# ============================================================================

"""
SCRIPT TO SAY:
"The RAG (Retrieval-Augmented Generation) pipeline combines
ChromaDB semantic search with Groq for context-aware answers."

ACTION:
- Show /query endpoint with a compliance question

LIVE DEMO:

curl -X POST http://localhost:5000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does GDPR require for data subject rights?"
  }'

EXPECTED RESPONSE:
{
  "answer": "GDPR grants several fundamental rights to data subjects. These include: 1) Right of access - individuals can request and obtain confirmation of their personal data... 2) Right to be forgotten - subjects can request deletion of their data... 3) Right to data portability - individuals can receive their data in a portable format...",
  "sources": [
    {
      "text": "GDPR requires explicit consent before processing personal data. Organizations must implement data protection impact assessments and maintain detailed records...",
      "distance": 0.15,
      "metadata": {
        "category": "Data Privacy",
        "priority": "High"
      }
    },
    {
      "text": "Organizations must honor data subject requests within 30 days. These include rights to access, rectification, erasure, and data portability under Articles 12-22...",
      "distance": 0.22,
      "metadata": {
        "category": "Data Privacy",
        "priority": "High"
      }
    }
  ],
  "meta": {
    "model_used": "llama-3.3-70b-versatile",
    "tokens_used": 289,
    "response_time_ms": 3845,
    "cached": false,
    "is_fallback": false
  }
}

SAY: "Notice the sources - ChromaDB retrieved the most relevant documents,
and Groq used them as context to answer accurately. This prevents hallucinations."
"""


# ============================================================================
# SEGMENT 4: STACK EXPLANATION (15 seconds)
# ============================================================================

"""
SCRIPT TO SAY:
"Let me explain the technology stack briefly:

1. FLASK - Lightweight Python web framework for the API
2. GROQ API - LLaMA 3.3-70B model, free tier, no credit card required
3. CHROMADB - Vector database storing 10 compliance documents as embeddings
4. REDIS - In-memory cache improving response time by 66.7%
5. RATE LIMITING - 30 requests per minute globally, preventing abuse

The flow:
1. Request comes in
2. Check Redis cache - if hit, return in <100ms
3. If miss, query ChromaDB for context
4. Call Groq API with context
5. Cache result for 15 minutes
6. Return structured JSON response

All endpoints have proper error handling, retry logic,
and fallback responses if Groq is unavailable."
"""


# ============================================================================
# KEY NUMBERS TO REMEMBER
# ============================================================================

DEMO_NUMBERS = {
    "categorise_response_time": "2.3 seconds",
    "query_response_time": "3.8 seconds",
    "generate_report_time": "5.1 seconds",
    "cache_hit_rate": "66.7%",
    "chroma_docs_seeded": 10,
    "rate_limit": "30 req/min",
    "redis_ttl_minutes": 15,
    "groq_tokens_avg": 250,
}

# ============================================================================
# PRACTICE QUESTIONS & ANSWERS
# ============================================================================

Q_A = {
    "What does AI Developer 2 do?": {
        "answer": "Implements AI endpoints: /categorise, /query, /generate-report. "
        "Handles Groq integration, ChromaDB RAG pipeline, Redis caching, and "
        "prompt tuning. Ensures all endpoints are performant and reliable."
    },
    "What is RAG?": {
        "answer": "Retrieval-Augmented Generation. We retrieve documents from "
        "ChromaDB, inject them as context, then send to Groq. This prevents "
        "AI from making up answers and grounds responses in real data."
    },
    "Why Redis?": {
        "answer": "Redis caches AI responses for 15 minutes. If the same question "
        "is asked twice, the second response is instant. Reduces API calls to "
        "Groq, saving costs and improving UX."
    },
    "What if Groq fails?": {
        "answer": "Every Groq call is wrapped in try-except. On timeout or error, "
        "we return a fallback template response with is_fallback: true. Never "
        "return HTTP 500 because AI is unavailable."
    },
}

print("✅ AI Demo Script Ready")
print(f"Total Demo Time: 2 minutes")
print(f"Endpoints to demo: 4 (/categorise, /query, /generate-report, /health)")
print(f"Expected Cache Hit Rate: 66.7%")
