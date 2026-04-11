from mistralai import Mistral
import os
from dotenv import load_dotenv
import re
import json
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def extract_amount(text):
    match = re.search(r'(\d+[,\d]*)', text.replace(",", ""))
    if match:
        return int(match.group(1))
    return 0


def detect_event_llm(question):
    prompt = f"""
Identify ALL financial events in the scenario.

Question:
{question}

Return STRICT JSON:

{{
"event_types": ["loan_default","fraud"],
"confidence": 0-1,
"reason": "why these classifications"
}}
"""

    response = client.chat.complete(
        model="mistral-small",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    start = content.find("{")
    end = content.rfind("}") + 1

    try:
        data = json.loads(content[start:end])
        return data["event_types"], data["confidence"], data["reason"]
    except:
        return ["normal"], 0.5, "fallback classification"


def risk_color(risk):
    if risk == "High":
        return "red"
    if risk == "Medium":
        return "orange"
    if risk == "Low":
        return "green"
    return "gray"


def risk_score_engine(event_types, amount, question):
    score = 0
    text = question.lower()

    if "fraud" in event_types:
        score += 40
    if "loan_default" in event_types:
        score += 35
    if "investment_violation" in event_types:
        score += 40
    if amount > 1000000:
        score += 10
    if amount > 10000000:
        score += 15
    if "undeclared" in text:
        score += 20
    if "multiple" in text:
        score += 10

    return min(score, 100)


def timeline_engine(event_types, question):
    timeline = []

    if "fraud" in event_types:
        timeline += [
            "User interacts with fraudulent source",
            "Credentials or OTP compromised",
            "Unauthorized transaction executed",
            "User reports to bank",
            "Bank investigates liability"
        ]

    if "loan_default" in event_types:
        timeline += [
            "Loan disbursed",
            "Financial stress occurs",
            "EMI missed",
            "Account overdue",
            "Loan classified as NPA"
        ]

    if "foreign_transfer" in event_types:
        timeline += [
            "User initiates transfer",
            "Bank checks LRS eligibility",
            "Documents verified",
            "Transfer processed",
            "Reported under RBI"
        ]

    if "investment_violation" in event_types:
        timeline += [
            "Investment made",
            "Source not declared",
            "Transaction flagged",
            "Investigation initiated",
            "Penalty/legal action possible"
        ]

    return timeline if timeline else ["No clear timeline identified"]


def fraud_liability_engine(event_types, question):
    text = question.lower()

    if "fraud" not in event_types:
        return "Not applicable"

    if "phishing" in text or "otp" in text:
        return "Customer liable (credential sharing/negligence)"

    if "immediately" in text or "instant" in text:
        return "Zero liability (reported promptly)"

    if "delay" in text or "late" in text:
        return "Limited liability depending on delay"

    return "Liability subject to bank investigation"


def regulation_mapping(event_types, question):
    rules = []

    if "loan_default" in event_types:
        rules += [
            "RBI IRAC Norms",
            "Insolvency and Bankruptcy Code (IBC)"
        ]

    if "fraud" in event_types:
        rules += [
            "RBI Customer Protection Circular",
            "IT Act 2000"
        ]

    if "ai_bias" in event_types:
        rules += [
            "RBI Digital Lending Guidelines",
            "Fair Lending Practices"
        ]

    if "foreign_transfer" in event_types:
        rules += [
            "RBI Liberalised Remittance Scheme (LRS)",
            "Income Tax Act - TCS"
        ]

    if "investment_violation" in event_types:
        rules += [
            "Prevention of Money Laundering Act (PMLA)",
            "Income Tax Act"
        ]

    return list(set(rules)) if rules else ["General Banking Regulations"]


def consequence_engine(event_types, amount, question):
    consequences = []

    if "loan_default" in event_types:
        consequences += [
            "Loan classified as NPA",
            "Credit score drops",
            "Recovery/legal action possible"
        ]

    if "fraud" in event_types:
        consequences += [
            "Financial loss possible",
            "Liability depends on reporting time",
            "Bank investigation required"
        ]

    if "ai_bias" in event_types:
        consequences += [
            "Regulatory violation risk",
            "Customer discrimination impact",
            "Model audit required"
        ]

    if "foreign_transfer" in event_types and "delay" in question.lower():
        consequences += [
        "Late reporting may trigger Income Tax notice",
        "Mismatch in Form 26AS possible",
        "Bank compliance flag may increase scrutiny",
        "Penalty risk under FEMA for delayed declaration"
    ]

    if "investment_violation" in event_types:
        consequences += [
            "Tax penalties possible",
            "AML investigation risk",
            "Legal consequences"
        ]

    return consequences if consequences else ["No major consequence identified"]


def rule_engine(amount, event_types, question):
    if "fraud" in event_types:
        return "Non-Compliant", "High", "Unauthorized transaction / fraud"

    if "loan_default" in event_types:
        return "Non-Compliant", "High", "Loan default leading to NPA"

    if "ai_bias" in event_types:
        return "Review Required", "High", "Algorithmic bias risk"

    if "foreign_transfer" in event_types:
        if amount > 25000000:
            return "Non-Compliant", "High", "Exceeds RBI LRS limit"
        elif amount > 10000000:
            return "Compliant", "Medium", "High-value transfer"
        return "Compliant", "Low", "Within LRS limit"

    if "investment_violation" in event_types:
        return "Non-Compliant", "High", "Undeclared / illegal investment"

    return "Compliant", "Low", "Normal case"


def generate_response(
    question,
    status,
    risk,
    reason,
    consequences,
    regulations,
    event_types,
    confidence,
    event_reason,
    color,
    score,
    timeline,
    liability
):
    prompt = f"""
You are an expert financial compliance and risk advisor for India.

Analyze the scenario deeply and give a realistic, practical, and structured response.

Explain like:
"Here’s what’s happening, here’s the risk, and here’s what you should do"

Analyze the scenario deeply and give a realistic, practical, and structured response.

Scenario:
{question}

Detected Events: {event_types}
Confidence: {confidence}
Reason: {event_reason}

Decision:
Compliance Status: {status}
Risk Level: {risk}
Risk Score: {score}
Reason: {reason}

Timeline:
{timeline}

Fraud Liability:
{liability}

Consequences:
{consequences}

Regulations:
{regulations}

---

Return STRICT JSON:

{{
"analysis": "Explain in 2–3 concise sentences what is happening. Avoid long paragraphs.(practical tone)",
"compliance_status": "{status}",
"risk_level": "{risk}",
"risk_score": {score},
"confidence": {confidence},
"reason": "{reason}",

"what_could_happen_next": {{
    "immediate": ["short term effects"],
    "regulatory": ["mention FEMA, RBI, IT Act where relevant"],
    "tax": ["TCS, penalties, notices if applicable"],
    "worst_case": ["extreme but realistic outcomes"]
}},

"what_should_you_do": {{
    "immediate_actions": ["urgent steps"],
    "compliance_actions": ["legal / reporting steps"],
    "risk_mitigation": ["reduce damage"],
    "preventive_measures": ["avoid future issues"]
}},

"timeline": {json.dumps(timeline)},
"fraud_liability": "{liability}",
"regulations": {json.dumps(regulations)}
}}
"""

    response = client.chat.complete(
        model="mistral-small",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    content = content.replace("json", "").strip()

    start = content.find("{")
    end = content.rfind("}") + 1

    try:
        parsed = json.loads(content[start:end])
        parsed["confidence"] = confidence
        parsed["risk_color"] = color
        return parsed
    except:
        return {
            "analysis": question,
            "compliance_status": status,
            "risk_level": risk,
            "risk_score": score,
            "confidence": confidence,
            "reason": reason,
            "risk_color": color,
            "what_could_happen_next": {
                "immediate": consequences,
                "regulatory": [],
                "tax": [],
                "worst_case": []
            },
            "what_should_you_do": {
                "immediate_actions": ["Review transaction"],
                "compliance_actions": ["Ensure reporting"],
                "risk_mitigation": ["Consult bank"],
                "preventive_measures": ["Maintain records"]
            },
            "timeline": timeline,
            "fraud_liability": liability,
            "regulations": regulations
        }


def what_if_agent(question):
    amount = extract_amount(question)

    try:
        event_types, confidence, event_reason = detect_event_llm(question)
    except:
        event_types, confidence, event_reason = ["normal"], 0.5, "fallback"

    status, risk, reason = rule_engine(amount, event_types, question)

    consequences = consequence_engine(event_types, amount, question)

    regulations = regulation_mapping(event_types, question)

    score = risk_score_engine(event_types, amount, question)

    timeline = timeline_engine(event_types, question)

    liability = fraud_liability_engine(event_types, question)

    color = risk_color(risk)

    return generate_response(
        question,
        status,
        risk,
        reason,
        consequences,
        regulations,
        event_types,
        confidence,
        event_reason,
        color,
        score,
        timeline,
        liability
    )