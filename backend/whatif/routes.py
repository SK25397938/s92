from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.auth.utils import decode_token
from backend.auth.models import User, WhatIfSession, Message
from backend.whatif.whatif_engine import what_if_agent
from pydantic import BaseModel
import json

router = APIRouter()
security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_id = decode_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def detect_scenario_type(history: str, new_message: str):
    prompt = f"""
You are a financial scenario classifier.

Conversation so far:
{history}

New message:
{new_message}

Is this a NEW scenario or continuation of SAME scenario?

Reply ONLY with:
NEW
or
CONTINUE
"""
    result = what_if_agent(prompt)
    text = str(result).upper()

    if "NEW" in text:
        return "NEW"
    return "CONTINUE"


class MessageRequest(BaseModel):
    session_id: int
    message: str


# ---------------------------
# CREATE SESSION
# ---------------------------
@router.post("/create")
def create_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = WhatIfSession(user_id=user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "message": "Session created"
    }


# ---------------------------
# SEND MESSAGE
# ---------------------------
@router.post("/message")
def send_message(
    data: MessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(WhatIfSession).filter(
        WhatIfSession.id == data.session_id,
        WhatIfSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = Message(
        session_id=session.id,
        role="user",
        content=data.message
    )
    db.add(user_msg)

    messages = db.query(Message).filter(
        Message.session_id == session.id
    ).order_by(Message.timestamp).all()

    context = ""
    for m in messages:
        context += f"{m.role.upper()}: {m.content}\n"

    decision = detect_scenario_type(context, data.message)

    if decision == "NEW":
        full_input = f"USER: {data.message}"
    else:
        full_input = context + f"\nUSER: {data.message}"

    ai_response = what_if_agent(full_input)

    ai_msg = Message(
        session_id=session.id,
        role="assistant",
        content=json.dumps(ai_response)
    )
    db.add(ai_msg)

    db.commit()

    return ai_response


# ---------------------------
# GET HISTORY
# ---------------------------
@router.get("/history/{session_id}")
def get_history(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(WhatIfSession).filter(
        WhatIfSession.id == session_id,
        WhatIfSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(Message).filter(
    Message.session_id == session_id
).order_by(Message.timestamp).all()

    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp
        }
        for m in messages
    ]

@router.get("/list")
def list_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(WhatIfSession).filter(
        WhatIfSession.user_id == user.id
    ).order_by(WhatIfSession.id.desc()).all()

    return [{"id": s.id} for s in sessions]

@router.delete("/delete/{session_id}")
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(WhatIfSession).filter(
        WhatIfSession.id == session_id,
        WhatIfSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.query(Message).filter(Message.session_id == session_id).delete()
    db.delete(session)
    db.commit()

    return {"message": "Deleted"}


@router.post("/title")
def generate_title(
    data: MessageRequest,
    user: User = Depends(get_current_user)
):
    prompt = f"""
Generate a short 3-5 word title for this financial scenario:

{data.message}

Rules:
- Keep it concise
- No punctuation
- No full sentence
- Only title

Example:
"₹10 lakh abroad transfer FEMA compliance"
→ "Foreign Transfer Compliance"
"""

    result = what_if_agent(prompt)

    return {"title": str(result).strip()}