from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer, primary_key=True)
    phone = Column(String)


engine = create_engine(f'sqlite:///cab.db')
Base.metadata.create_all(engine)