# 💼 S92 – Intelligent Financial Compliance Assistant

## 📖 Overview

**S92** is an AI-powered financial compliance assistant that simplifies complex banking and regulatory information through **Retrieval-Augmented Generation (RAG)**. The platform combines an intelligent conversational AI with a structured learning dashboard, enabling users to ask finance-related questions and receive accurate, source-backed explanations based on official regulatory documents.

Designed as a decision-support system, S92 helps users understand regulations issued by organizations such as **RBI**, **FEMA**, and other financial authorities while promoting financial literacy through explainable AI.

---

## ✨ Features

- 🤖 AI-powered Financial Compliance Assistant
- 📚 Retrieval-Augmented Generation (RAG) Architecture
- 📄 Source-backed responses with document references
- 🔍 Context-aware follow-up conversations
- 🚫 Detection and filtering of irrelevant queries
- 📖 Interactive Learning Dashboard
- ⚡ Fast semantic document retrieval
- 💬 Modern Chat Interface with loading animations
- 🏗️ Modular and scalable backend architecture

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn

### AI & Machine Learning
- Retrieval-Augmented Generation (RAG)
- LangChain
- FAISS Vector Database
- Sentence Transformers
- OpenAI GPT Models

### Database
- SQLite

### Libraries
- PyPDF
- NumPy
- Requests
- python-dotenv

---

## 🧠 Core Modules

### 🤖 AI Compliance Assistant

The chatbot answers finance-related questions using official regulatory documents instead of relying solely on the language model.

Features include:

- Semantic document retrieval
- Source-backed responses
- Conversation memory
- Context-aware follow-up handling
- Hallucination reduction using RAG

---

### 📚 Learning Dashboard

A structured learning section designed to help users understand financial concepts.

Topics include:

- RBI Guidelines
- FEMA Regulations
- Foreign Exchange (Forex)
- Tax Compliance
- Banking Procedures
- Financial Literacy

---

### 📊 What-If Analysis Module

The **What-If Analysis Module** allows users to simulate financial scenarios before making real-world decisions.

Instead of providing generic advice, the system evaluates hypothetical situations using predefined compliance rules and regulatory guidelines.

### Key Capabilities

- 📈 Scenario-based financial analysis
- ✅ Rule-based compliance evaluation
- ⚠️ Risk assessment
- 📄 Regulatory explanation
- 💡 Decision-support recommendations

---

### Example Scenarios

- What happens if I exceed the LRS limit?
- Can I invest abroad using Forex?
- What if my KYC is incomplete?
- What are the penalties for FEMA violations?
- Can I transfer money overseas without approval?

---

## ⚙️ How It Works

1. User submits a financial query.
2. Relevant document chunks are retrieved using semantic search.
3. The LLM receives both the query and retrieved context.
4. A grounded response is generated.
5. Sources and document references are displayed in the UI.

---

## 📂 Project Structure

```text
S92/
│
├── backend/
│   ├── ai_agent/
│   │   ├── ingest.py
│   │   ├── rag_pipeline.py
│   │   ├── vector_store.py
│   │   └── ...
│   │
│   ├── main.py
│   └── ...
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── chat.html
│   └── ...
│
├── regulations/
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/<your-username>/S92.git
cd S92
```

---

### Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create a `.env` file inside the **backend** directory.

```env
OPENAI_API_KEY=your_api_key_here
```

---

### Add Financial Documents

Place all regulatory documents inside:

```text
regulations/
```

Example documents:

- RBI Circulars
- FEMA Regulations
- Banking Guidelines
- Financial Compliance PDFs

---

### Build the Knowledge Base

```bash
python -m backend.ai_agent.ingest
```

This processes all documents and creates vector embeddings for semantic retrieval.

---

### Start Backend

```bash
uvicorn backend.main:app --reload
```

---

### Start Frontend

Open another terminal.

```bash
python -m http.server 5500
```

Visit:

```
http://127.0.0.1:5500/login.html
```

---

## 💬 Example Queries

- What is the Liberalised Remittance Scheme (LRS)?
- How much money can I send abroad?
- What are RBI Forex regulations?
- Explain FEMA in simple terms.
- What happens if KYC is incomplete?
- Can I invest in foreign stocks?
- What are the penalties for non-compliance?

---

## 🚀 Future Enhancements

- 📈 AI-powered financial risk scoring
- 🧾 Personalized compliance reports
- 🌍 Multi-language support
- 📱 Mobile application
- 🔔 Regulatory update notifications
- 📊 Interactive analytics dashboard
- 🎙️ Voice-enabled AI assistant
- 🏦 Integration with banking APIs

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub!
