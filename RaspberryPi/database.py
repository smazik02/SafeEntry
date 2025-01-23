from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Boolean, Column, TIMESTAMP, func

db = SQLAlchemy()


class AccessCard(db.Model):
    __tablename__ = 'ACCESS_CARDS'

    id = Column(String, primary_key=True)
    is_locked = Column(Boolean, nullable=False)
    in_room = Column(Boolean, nullable=False)


class AccessAttempt(db.Model):
    __tablename__ = 'ACCESS_ATTEMPTS'

    id = Column(Integer, primary_key=True)
    access_card = Column(String, nullable=False)
    attempt_time = Column(TIMESTAMP, default=func.now())
    was_accepted = Column(Boolean, nullable=False)
    reason = Column(Text)
