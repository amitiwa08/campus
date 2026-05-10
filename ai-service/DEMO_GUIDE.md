# AI Service Demo Guide

This guide explains how to showcase the CampusPe AI Service using the premium dashboard.

## Prerequisites
1. **Python 3.9+** installed.
2. **Groq API Key**: Ensure `GROQ_API_KEY` is set in the `.env` file.
3. **Redis** (Optional but recommended): Improves speed via caching.

## Setup & Running

### 1. Start the AI Service
Open a terminal in the `ai-service` directory and run:
```bash
python app.py
```
The service will start on `http://localhost:5000`.

### 2. Open the Premium Dashboard
Locate the `premium_dashboard.html` file in the `ai-service` folder and open it in any modern web browser (Chrome/Edge/Firefox).

## Key Features to Demo

### A. Real-time Report Generation
- Enter a topic (e.g., "Conflict of Interest for Executives").
- Select a department.
- Watch the **Terminal Logs** at the bottom to see the request hit the backend.
- Observe the **Llama 3.3 70B** response rendered as a professional report.

### B. High-Speed Inference
- Point out the `meta.response_time_ms` in the terminal logs.
- Groq's LPU hardware ensures reports are generated in seconds, not minutes.

### C. Smart Categorization
- Paste any compliance-related text into the Classifier.
- See how accurately the AI identifies the regulatory domain (e.g., Data Privacy vs. Finance).

### D. Security & Resilience
- Mention the **Rate Limiting** (30 req/min) shown in `app.py`.
- Mention the **Retry Logic** in `GroqClient` which handles API timeouts automatically.
