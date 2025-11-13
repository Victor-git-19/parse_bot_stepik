from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from app.core.db import Base


class User(Base):
    tg_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False, default="друг")
    stepik_url = Column(String, nullable=False)

    solved_tasks = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)

    notify_hour = Column(Integer, default=20)
    notify_minute = Column(Integer, default=0)

    last_update = Column(DateTime, default=datetime.utcnow)
