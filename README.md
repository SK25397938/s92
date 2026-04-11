S92 – Intelligent Financial Compliance Assistant
Overview

S92 is an intelligent finance platform designed to simplify complex banking and regulatory information using AI. It combines a Retrieval-Augmented Generation (RAG) based AI assistant with a structured learning dashboard, enabling users to both ask questions and understand financial compliance concepts.

The system helps users understand topics such as RBI guidelines, forex regulations, tax compliance, and banking norms in a clear and explainable manner.

What is S92?

S92 is a decision-support and knowledge assistant for financial compliance.

It functions as:

An AI agent that answers queries using real financial documents
A learning module that provides structured explanations
An explainable system that shows sources and document references
Features
RAG-based AI assistant using financial documents
Source-backed answers with direct PDF page linking
Context-aware follow-up question handling
Filtering of irrelevant or non-finance queries
Interactive learning dashboard with structured content
Clean chat interface with loading feedback
Modular and scalable backend architecture

What-If Analysis Module

The What-If module is an interactive feature designed to simulate financial scenarios and help users understand the consequences of their decisions before taking action.

It allows users to input hypothetical situations such as sending money abroad, exceeding regulatory limits, or performing specific financial transactions. The system then evaluates the scenario using predefined rules and regulatory guidelines (such as RBI and FEMA) and provides a structured response explaining whether the action is compliant, risky, or restricted.

Key Capabilities
Scenario-based analysis of financial decisions
Rule-based compliance evaluation
Clear explanation of outcomes and risks
Helps users understand limits, restrictions, and regulatory impact
Supports better decision-making without real financial risk
Example Use Cases
What happens if I send more than the LRS limit?
Can I use forex for investment abroad?
What if KYC is not completed?
What are the consequences of non-compliance?

Setup Instructions
1. Clone the Repository
git clone <your-repo-url>
cd S92
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Add Environment Variables

Create a .env file in the s92/backend/:

OPENAI_API_KEY=your_api_key_here
5. Add Documents for RAG

Place all documents inside:

regulations

Include:

RBI documents
Bank PDFs
Custom structured text guides


6. Run Ingestion
python -m backend.ai_agent.ingest

This step processes documents and stores embeddings for retrieval.

7. Start Backend Server
in the command prompt in vs code type : uvicorn backend.main:app --reload

8. Start frontend
in new command prompt within vs code type : python -m http.server 5500
then go to : http://127.0.0.1:5500/login.html


Example Queries
What is the LRS limit?
How to send money abroad?
What are RBI forex rules?
How to get a credit card?


How It Works
User submits a query
System retrieves relevant document chunks
Language model generates a response using retrieved context
Sources are mapped to exact document pages
Structured output is displayed in the UI
