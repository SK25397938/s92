from sentence_transformers import SentenceTransformer
import numpy as np
from backend.ai_agent.vector_store import load_vector_store
from mistralai import Mistral
from rank_bm25 import BM25Okapi
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = Mistral(api_key=API_KEY)

SOURCE_MAP = {
    "axis.pdf": "axis.pdf",
    "BANK OF BARODA.pdf": "bank_of_baroda.pdf",
    "FEEDRAL BANK.pdf": "feedral.pdf",
    "HDFC Bank.pdf": "hdfc.pdf",
    "IDFC FIRST Bank.pdf": "idfc.pdf",
    "RBI.pdf": "RBI.pdf",
    "sbi.pdf": "sbi.pdf"
}

LINK_MAP = {
    "rbi": [
        {"title": "RBI Guidelines", "url": "https://www.rbi.org.in"}
    ],
    "hdfc": [
        {"title": "HDFC Forex Services", "url": "https://www.hdfcbank.com/personal/money-transfer/foreign-exchange"}
    ],
    "icici": [
        {"title": "ICICI Forex Guide", "url": "https://www.icicibank.com/forex"}
    ],
    "sbi": [
        {"title": "SBI Forex", "url": "https://sbi.co.in"}
    ],
    "axis": [
        {"title": "Axis Forex", "url": "https://www.axisbank.com"}
    ],
    "education": [
        {"title": "RBI LRS Scheme", "url": "https://www.rbi.org.in"}
    ],
    "default": [
        {"title": "RBI Official Website", "url": "https://www.rbi.org.in"}
    ]
}

def detect_mode(question: str):
    q = question.lower()

    if any(w in q for w in ["how", "steps", "guide", "help", "process"]):
        return "GUIDE"

    if any(w in q for w in ["what if", "risk", "penalty", "illegal","consequence", "can i", "is it allowed","will i get caught", "problem if"]):
        return "INLINE_WHATIF"

    if any(w in q for w in ["scenario", "case", "suppose", "if i do"]):
        return "REDIRECT"

    return "EXPLAIN"

def detect_depth(question: str):
    q = question.lower()

    if len(q.split()) <= 3:
        return "SHORT"

    if any(w in q for w in ["what", "define", "meaning"]):
        return "SHORT"

    if any(w in q for w in ["list", "types", "points"]):
        return "POINTS"

    return "DETAILED"

def ask_agent(question, history=""):
    question = question.strip()

    original_question = question

    history_lines = [line for line in history.strip().split("\n") if line.strip() != ""]

    follow_up_triggers = [
        "explain more", "explain in detail", "step by step",
        "elaborate", "more detail", "how exactly",
        "can you explain", "tell me more"
    ]

    is_follow_up = any(p in original_question.lower() for p in follow_up_triggers)

    last_user_query = ""
    for line in reversed(history_lines):
        if "?" in line:
            last_user_query = line
            break

    if is_follow_up and last_user_query:
        question = last_user_query + " " + question

    mode = detect_mode(original_question)
    response_style = detect_depth(original_question)

    if is_follow_up:
        mode = "GUIDE"

    index, texts, metadata, tokenized_texts = load_vector_store()

    bm25 = BM25Okapi(tokenized_texts)
    tokenized_query = question.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_top_idx = np.argsort(bm25_scores)[-3:][::-1]

    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding), k=5)
    is_finance = True
    if len(D[0]) == 0 or D[0][0] > 1.3:
        is_finance = False

    combined_indices = list(I[0]) + list(bm25_top_idx)
    combined_indices = list(dict.fromkeys(combined_indices))
    
    context_chunks = []

    if len(D[0]) == 0 or D[0][0] > 1.3:
        context_chunks = combined_indices[:3]

    for i in combined_indices:
        chunk = texts[i]
        if sum(word in chunk.lower() for word in tokenized_query) >= 1:
            context_chunks.append(i)

    if not context_chunks:
        context_chunks = combined_indices[:3]

    context_chunks = context_chunks[:2]
    priority_chunks = []

    for i in context_chunks:
        raw_source = metadata[i].get("source")
        source = SOURCE_MAP.get(raw_source, raw_source).lower()
        q = question.lower()

        if "guide" in source or "basics" in source:
            priority_chunks.insert(0, i)
            continue

        if "rbi" in q and "rbi" in source:
            priority_chunks.insert(0, i)
        elif "hdfc" in q and "hdfc" in source:
            priority_chunks.insert(0, i)
        elif "sbi" in q and "sbi" in source:
            priority_chunks.insert(0, i)
        else:
            priority_chunks.append(i)

    context_chunks = priority_chunks[:2]

    context = ""
    history = "\n".join(history.split("\n")[-6:])

    for i in context_chunks:
        chunk = texts[i]
        processed_source = metadata[i].get("source")
        source = SOURCE_MAP.get(processed_source, processed_source)
        page = metadata[i]["page"]

        context += f"""
TEXT:
{chunk}

SOURCE:
{source} page {page}

"""

    prompt = f"""
You are a financial assistant.

Conversation so far:
{history}

Mode: {mode}
Response Style: {response_style}

STRICT RULES (FOLLOW EXACTLY):

EXPLAIN:
- Give detailed explanations (3–5 sentences)
- Explain clearly like teaching a beginner
- Include practical examples where relevant
- Mention important limits, rules, or conditions if applicable
- Avoid generic statements

GUIDE:
- Give step-by-step actionable guidance
- Use clean bullet points
- Avoid numbering unless necessary
- Put ALL steps inside "key_points"
- Each step should be short and actionable
- Do NOT start with a long paragraph
- Include what to do if stuck
- Do NOT repeat the same content in both "answer" and "key_points"

INLINE_WHATIF:
- Maximum 2–4 lines
- Clearly mention risk + consequence
- No detailed explanation

REDIRECT:
- Do NOT answer
- ONLY say: "This scenario is better handled in What-If Simulation"

RESPONSE STYLE CONTROL:

SHORT:
- Only "answer" (1–2 lines)

POINTS:
- "answer" should be 1 short line
- ALL content must go in "key_points"

DETAILED:
- Explanation in "answer"
- Optional points in "key_points"

IMPORTANT:
- Do NOT put lists inside "answer"
- Use "key_points" for lists/steps only

Return JSON:

Rules:
- "answer" must be plain text only
- Do NOT include {{}}, [], **, -, or any formatting symbols
- Do NOT include lists inside "answer"
- "key_points" must be a clean list of simple strings
- Each key point must be plain text (no symbols like -, *, **)
- Never return JSON inside JSON

Format EXACTLY like:

{{
 "answer": "Simple clean explanation",
 "key_points": [
  "Point one",
  "Point two",
  "Point three"
 ]
}}

Context:
{context}

Question:
{question}
"""

    response = client.chat.complete(
        model="mistral-small",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()
    content = content.replace("json", "").replace("```", "").strip()

    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        cleaned_json = content[start:end]

        data = json.loads(cleaned_json)

        if not isinstance(data, dict):
          raise Exception()

    except:
        data = {
            "answer": content,
            "key_points": []
    }

    if isinstance(data.get("answer"), str) and data["answer"].strip().startswith("{"):
       try:
           data = json.loads(data["answer"])
       except:
        pass

    q = (question + " " + context).lower()
    links = []

    if "hdfc" in q and "hdfc" in original_question.lower():
        links += LINK_MAP["hdfc"]

    if "icici" in q and "icici" in original_question.lower():
        links += LINK_MAP["icici"]

    if "sbi" in q and "sbi" in original_question.lower():
        links += LINK_MAP["sbi"]

    if "axis" in q and "axis" in original_question.lower():
        links += LINK_MAP["axis"]

    if "rbi" in q or "lrs" in q:
        links += LINK_MAP["rbi"]

    if "education" in q or "study" in q:
        links += LINK_MAP["education"]

    if not links:
        links = LINK_MAP["default"]

    def clean_text(text):
       text = str(text)
       return text.replace("{","").replace("}","").replace("[","").replace("]","").replace("*","")

    if "answer" in data:
       data["answer"] = clean_text(data["answer"])

    if "key_points" in data:
       data["key_points"] = [clean_text(str(p)) for p in data["key_points"]]


    if is_finance:
        data["helpful_links"] = links
    else:
        data["helpful_links"] = [] 
   
    seen_files = set()
    seen_pages = set()
    unique_sources = []

    for i in context_chunks:
        file = SOURCE_MAP.get(metadata[i].get("source"), metadata[i].get("source"))
        page = metadata[i]["page"]

        if (file, page) in seen_pages:
            continue

        if file not in seen_files:
            unique_sources.append({
               "file": file,
               "page": page,
               "url": f"/docs/{file}#page={page}"
            })
            seen_files.add(file)

        seen_pages.add((file, page)) 

    data["sources"] = unique_sources
    data["mode"] = mode

    if not is_finance:
        return {
          "answer": "This assistant currently handles finance and banking related queries only.",
          "key_points": [
             "Ask about forex rules, RBI guidelines, LRS limits, or banking services",
             "Try questions related to money transfer, taxation, or financial compliance"
           ],
           "sources": [],
           "helpful_links": [],
           "mode": mode
        }   

    return data