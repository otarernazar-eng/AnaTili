import hashlib
from database import SessionLocal, User, Vocabulary, Material, Session as DbSessionModel
from sqlalchemy.orm import Session
import json
import datetime

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(db: Session, username, password, role, full_name="", age=None, language_level="", interests=""):
    # Check if exists
    if db.query(User).filter(User.username == username).first():
        return None
    
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        password_hash=hashed_password,
        role=role,
        full_name=full_name,
        age=age,
        language_level=language_level,
        interests=interests,
        free_time="",
        volunteer_hours=0.0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username, password):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if user.password_hash != hash_password(password):
        return None
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_potential_matches(db: Session, user: User):
    # Basic matching logic
    if user.role == "Менти (Ученик)":
        target_role = "Ментор"
    elif user.role == "Ментор":
        target_role = "Менти (Ученик)"
    else:
        return []
        
    # Find users of opposite role
    candidates = db.query(User).filter(User.role == target_role).all()
    
    # Simple scoring: 1 point for same language level, 1 point for shared interest words
    matches = []
    user_interests = set([x.strip().lower() for x in user.interests.split(',') if x.strip()]) if user.interests else set()
    
    for cand in candidates:
        score = 0
        if cand.language_level == user.language_level:
            score += 2
            
        cand_interests = set([x.strip().lower() for x in cand.interests.split(',') if x.strip()]) if cand.interests else set()
        common_interests = user_interests.intersection(cand_interests)
        score += len(common_interests)
        
        matches.append({"user": cand, "score": score, "common": list(common_interests)})
        
    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

from database import Vocabulary, Material

def seed_initial_data(db: Session):
    # Check if vocab exists
    if not db.query(Vocabulary).first():
        words = [
            {"word": "Сәлем", "translation": "Привет", "example": "Сәлем, қалайсың?", "pronunciation": "Са-лем"},
            {"word": "Рахмет", "translation": "Спасибо", "example": "Көп рахмет!", "pronunciation": "Рах-мет"},
            {"word": "Отбасы", "translation": "Семья", "example": "Менің отбасым үлкен.", "pronunciation": "От-ба-сы"},
            {"word": "Кітап", "translation": "Книга", "example": "Бұл өте қызықты кітап.", "pronunciation": "Кі-тап"},
        ]
        for w in words:
            db.add(Vocabulary(**w, level="A1"))
        
    # Check if literature exists
    if not db.query(Material).filter(Material.type == 'literature').first():
        lit = Material(
            type="literature",
            title="Слова Назидания (Қара сөздер) - Слово Первое",
            content="Хорошо я жил или плохо, а пройдено немало: в борьбе и ссорах, судах и спорах, страданиях и тревогах дошел до преклонных лет, выбившись из сил, пресытившись всем, обнаружил бренность и бесплодность своих деяний...\n\n**Интерактивный сценарий:** Если бы вы оказались на месте Абая, какому делу вы бы посвятили остаток своих дней?",
            level="B1"
        )
        db.add(lit)
    db.commit()

def get_all_vocabulary(db: Session):
    return db.query(Vocabulary).all()

def get_literature(db: Session):
    return db.query(Material).filter(Material.type == 'literature').all()

def add_vocabulary(db: Session, word: str, translation: str, example: str, pronunciation: str, level: str):
    v = Vocabulary(word=word, translation=translation, example=example, pronunciation=pronunciation, level=level)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

def add_literature(db: Session, title: str, content: str, level: str):
    m = Material(type="literature", title=title, content=content, level=level)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def create_meeting_session(db: Session, mentor_id: int, mentee_id: int, date: datetime.datetime, link: str):
    new_session = DbSessionModel(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        date=date,
        status="scheduled",
        meeting_link=link
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_user_sessions(db: Session, user_id: int, role: str):
    if role == "Ментор":
        return db.query(DbSessionModel).filter(DbSessionModel.mentor_id == user_id).all()
    elif role == "Менти (Ученик)":
        return db.query(DbSessionModel).filter(DbSessionModel.mentee_id == user_id).all()
    return []

def get_all_users_by_role(db: Session, role: str):
    return db.query(User).filter(User.role == role).all()

