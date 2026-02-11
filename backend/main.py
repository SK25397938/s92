from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base, SessionLocal
from backend.models import News
from backend.news_fetcher import fetch_finance_news
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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
