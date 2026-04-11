from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.auth.utils import decode_token
from backend.auth.models import User
from backend.ai_agent.models import AISession, AIMessage
from backend.ai_agent.rag_pipeline import ask_agent, client
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


class MessageRequest(BaseModel):
    session_id: int
    message: str


def detect_context_switch(history, new_message):

    if len(history.strip()) < 20:
        return "NEW"

    prompt = f"""
Conversation:
{history}

New message:
{new_message}

Is this a NEW topic or CONTINUATION?

Reply ONLY:
NEW
or
CONTINUE
"""

    res = client.chat.complete(
        model="mistral-small",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content.upper()

    if "NEW" in text:
        return "NEW"
    return "CONTINUE"


@router.post("/session/create")
def create_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = AISession(user_id=user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "message": "Session created"
    }


@router.post("/session/message")
def send_message(
    data: MessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(AISession).filter(
        AISession.id == data.session_id,
        AISession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = AIMessage(
        session_id=session.id,
        role="user",
        content=data.message
    )
    db.add(user_msg)

    messages = db.query(AIMessage).filter(
        AIMessage.session_id == session.id
    ).order_by(AIMessage.timestamp).all()

    context = ""

    for m in messages:
        if m.role == "assistant":
            try:
                parsed = json.loads(m.content)
                text = parsed.get("answer", "")
            except:
                text = m.content
        else:
            text = m.content

        context += f"{m.role.upper()}: {text}\n"

    context = "\n".join(context.split("\n")[-6:])

    decision = detect_context_switch(context, data.message)

    if decision == "NEW":
        final_context = ""
    else:
        final_context = context

    ai_response = ask_agent(data.message, final_context)

    ai_msg = AIMessage(
        session_id=session.id,
        role="assistant",
        content=json.dumps(ai_response)
    )
    db.add(ai_msg)

    db.commit()

    return ai_response


@router.get("/session/history/{session_id}")
def get_history(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(AISession).filter(
        AISession.id == session_id,
        AISession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(AIMessage).filter(
        AIMessage.session_id == session_id
    ).order_by(AIMessage.timestamp).all()

    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": str(m.timestamp)
        }
        for m in messages
    ]

@router.get("/session/list")
def list_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(AISession).filter(
        AISession.user_id == user.id
    ).order_by(AISession.id.desc()).all()

    return [{"id": s.id} for s in sessions]


@router.delete("/session/delete/{session_id}")
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(AISession).filter(
        AISession.id == session_id,
        AISession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.query(AIMessage).filter(
        AIMessage.session_id == session_id
    ).delete()

    db.delete(session)
    db.commit()

    return {"message": "Session deleted"}