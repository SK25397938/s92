from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.database import Base
from datetime import datetime

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    image_url = Column(String)
    source = Column(String)
    url = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
