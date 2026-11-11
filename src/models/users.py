from sqlalchemy import Column, Integer, String, Float, ForeignKey, func
from src.models import Base, session
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class Role(str, enum.Enum):
    ADMIN = 'ADMIN'
    SELLER = 'SELLER'

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)    
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., 'admin', 'user'
    active = Column(Integer, default=1)  # 1 for active, 0 for inactive

    def __init__(self, email, password, name, role):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.role = role

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', active={self.active})>"
    
    def get_paginated(page, per_page):
        total_users = session.query(func.count(Users.id)).scalar()
        users = session.query(Users).offset((page - 1) * per_page).limit(per_page).all()
        return users, total_users
    
    def get_by_id(user_id):
        user = session.query(Users).filter_by(id=user_id).first()
        return user
    
    def get_by_email(email):
        user = session.query(Users).filter_by(email=email).first()
        return user
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        session.add(self)
        session.commit()
    
    def update(self):
        session.commit()