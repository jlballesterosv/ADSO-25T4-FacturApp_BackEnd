from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.models import Base, session


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Float, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    active = Column(Integer, default=1)  # 1 for active, 0 for inactive

    def __init__(self, name, price, category_id, description=None, stock=0):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category_id = category_id

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock}, category_id={self.category_id}, active={self.active})>"
    
    def get():
        products = session.query(Products).all()
        return products
    
    def get_by_id(product_id):
        product = session.query(Products).filter_by(id=product_id).first()
        return product
    
    def get_by_name(name):
        product = session.query(Products).filter_by(name=name).first()
        return product
    
    def save(self):
        session.add(self)
        session.commit()
    
    def update(self):
        session.commit()
    
