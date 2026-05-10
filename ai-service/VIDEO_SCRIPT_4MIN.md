# CampusPe AI Showcase: 4-Minute Video Script

**Target Time**: 4 Minutes
**Visual Style**: High-energy, professional, screen-sharing the Premium Dashboard.

---

## 0:00 - 0:45 | Introduction: The Vision
**Visual**: Show the CampusPe Logo, then switch to a "before" view (complex legal text/empty reports).
**Narrator**: 
"Compliance training and reporting are often the most time-consuming parts of enterprise operations. Manual report generation can take hours, and keeping up with evolving regulations is a massive challenge.

At CampusPe, we’ve built a high-performance AI service that turns complex compliance data into actionable reports in seconds. Today, we’re going to look under the hood at how we use Groq’s lightning-fast inference and RAG architecture to solve this."

---

## 0:45 - 1:45 | The Tech Stack: Groq & Llama 3.3
**Visual**: Screen-share the code for `services/groq_client.py` and the `app.py` startup logs.
**Narrator**:
"Our engine is powered by **Groq’s LPU technology**, delivering **Llama 3.3 70B** responses at speeds that feel local. 

Unlike traditional LLM deployments, we’ve implemented a custom **GroqClient** with exponential backoff and robust JSON parsing. This ensures that even under high load, our API remains resilient. 

We’ve also integrated **ChromaDB** for Retrieval-Augmented Generation. This means our AI doesn't just 'guess'—it searches your specific company policies and legal documents first, then uses that context to generate answers that are 100% grounded in reality."

---

## 1:45 - 3:00 | Live Demo: The Premium Dashboard
**Visual**: Switch to the `premium_dashboard.html`. Type "GDPR Remote Work Security" into the Topic box and hit 'Generate'.
**Narrator**:
"Let’s see it in action. Here is our Premium AI Dashboard. I’m going to generate a report for **Remote Work Data Security** for the Engineering department.

*(Watch the terminal at the bottom)*
Notice the terminal logs—the request is hitting our Flask backend, checking our Redis cache for an existing result, and then calling Groq. 

*(Wait 2-3 seconds for the report to appear)*
And there it is. In less than 3 seconds, we have a structured report. We have an executive summary, specific compliance requirements like 'GDPR Article 32', and even a set of actionable recommendations. 

The beauty here is the **Prompt Tuning**. We’ve engineered our prompts to act as a 'Senior Compliance Architect,' ensuring the tone is authoritative and the JSON output is perfectly structured every single time."

---

## 3:00 - 3:45 | Security & Scalability
**Visual**: Briefly show the `SECURITY_REVIEW.md` and the `categorise` endpoint in action.
**Narrator**:
"But we didn't just build a demo; we built a service ready for production. 

We conducted a full **Security Review**, implementing rate limiting to prevent abuse and input sanitization to block injection attacks. 

We also have a high-fidelity **Content Classifier**. It can take any snippet of text—like a new internal policy—and instantly categorize it into domains like Data Privacy, Healthcare, or Ethics with over 95% confidence. This allows for automated routing of compliance tasks across the entire organization."

---

## 3:45 - 4:00 | Conclusion
**Visual**: Back to the CampusPe Logo with the URL or 'Thank You' slide.
**Narrator**:
"By combining the speed of Groq, the accuracy of RAG, and a premium user experience, CampusPe is setting a new standard for AI-driven compliance. 

Fast. Secure. Grounded. That’s the future of enterprise AI. Thanks for watching."

---

### Tips for Recording:
1.  **Preparation**: Make sure your `python app.py` is running before you start.
2.  **Pacing**: Speak clearly and give the UI a second to 'breathe' after a report is generated.
3.  **Visuals**: Use a browser with a 'dark mode' extension or ensure the premium dashboard's glow effects are visible.
