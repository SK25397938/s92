import requests
import os
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models import News
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

FINANCE_KEYWORDS = [
    "RBI",
    "SEBI",
    "Budget",
    "Tax",
    "Taxes",
    "Tariff",
    "Gold",
    "Silver",
    "Inflation",
    "Interest Rate",
    "Repo Rate",
    "Stock Market",
    "Sensex",
    "Nifty",
    "Rupee",
    "Dollar",
    "Forex",
    "Oil Price",
    "Global Economy",
    "Banking",
    "IMF",
    "World Bank"
]


def fetch_finance_news():
    url = f"https://newsapi.org/v2/everything?q=finance OR gold OR silver OR rupee OR tariff OR tax OR inflation OR forex&language=en&sortBy=publishedAt&apiKey={API_KEY}"
    
    response = requests.get(url)
    articles = response.json().get("articles", [])

    db = SessionLocal()

    for article in articles:
        if not any(keyword.lower() in article["title"].lower() for keyword in FINANCE_KEYWORDS):
            continue

        exists = db.query(News).filter(News.title == article["title"]).first()
        if exists:
            continue

        news = News(
            title=article.get("title"),
            description=article.get("description"),
            content=article.get("content"),
            image_url=article.get("urlToImage"),
            source=article.get("source", {}).get("name"),
            url=article.get("url"),
            published_at=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        )

        db.add(news)

    db.commit()
    db.close()