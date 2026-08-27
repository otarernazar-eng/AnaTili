from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20)) # 'mentor', 'mentee', 'admin'
    full_name = Column(String(100))
    age = Column(Integer)
    language_level = Column(String(20))
    interests = Column(Text)
    free_time = Column(Text)
    volunteer_hours = Column(Float, default=0.0)

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey('users.id'))
    mentee_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime)
    status = Column(String(20)) # 'scheduled', 'completed', 'cancelled'
    meeting_link = Column(String(200))
    mentor_feedback = Column(Text)
    mentee_feedback = Column(Text)

class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True)
    type = Column(String(50)) # 'speaking', 'literature', 'vocab', 'guide', 'game'
    title = Column(String(200))
    content = Column(Text)
    level = Column(String(20))

class Vocabulary(Base):
    __tablename__ = 'vocabulary'
    id = Column(Integer, primary_key=True)
    word = Column(String(100))
    translation = Column(String(100))
    example = Column(Text)
    pronunciation = Column(String(100))
    level = Column(String(20))

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100))
    description = Column(Text)
    date_earned = Column(DateTime, default=datetime.utcnow)

# Create engine
engine = create_engine('sqlite:///anatili.db', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
