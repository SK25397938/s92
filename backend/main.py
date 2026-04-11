from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from backend.database import engine, Base, SessionLocal
from backend.models import News
from backend.news_fetcher import fetch_finance_news
from backend.ai_agent.rag_pipeline import ask_agent
from backend.whatif.whatif_engine import what_if_agent
from backend.auth.routes import router as auth_router
from backend.whatif.routes import router as session_router
from backend.ai_agent.routes import router as ai_router

app = FastAPI()
app.include_router(ai_router, prefix="/api/ai")
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(session_router, prefix="/api/session", tags=["Session"])
app.mount("/docs", StaticFiles(directory="docs"), name="docs")
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_finance_news, "interval", minutes=30)
scheduler.start()

@app.get("/api/news")
def get_news():
    db = SessionLocal()
    news = db.query(News).order_by(News.published_at.desc()).limit(20).all()
    db.close()
    return news

@app.get("/api/news/{news_id}")
def get_article(news_id: int):
    db = SessionLocal()
    article = db.query(News).filter(News.id == news_id).first()
    db.close()
    return article

@app.get("/api/fetch-news")
def manual_fetch():
    fetch_finance_news()
    return {"message": "News fetched successfully"}

class Question(BaseModel):
    question: str

@app.post("/api/ask")
def ask(question: Question):
    return ask_agent(question.question)

@app.post("/api/what-if")
def what_if(question: Question):
    return what_if_agent(question.question)

@app.get("/api/dashboard")
def dashboard():
    return {
        "queries": 156,
        "risk": "Medium",
        "compliance": 89
    }

@app.get("/api/budget")
def get_budget():
    return {
        "labels": ["Infrastructure", "Healthcare", "Education", "Defense", "Others"],
        "allocation": [30, 25, 20, 15, 10],
        "monthly": [65, 59, 80, 81, 56, 55]
    }

@app.get("/api/tax")
def get_tax():
    return [
        {"range": "0-5L", "rate": 0},
        {"range": "5-10L", "rate": 20},
        {"range": "10-20L", "rate": 30},
        {"range": "20L+", "rate": 30}
    ]