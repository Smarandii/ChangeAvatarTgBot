import telebot
from telegram.client import Telegram, AuthorizationState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import DBManager
from utils import check_photos, TgRequest
from os.path import join, exists
from os import environ
# import dotenv
# dotenv.load_dotenv('variables.env')

api_id = 1111111
api_hash = 'hash'
database_encryption_key = 'changekey123'
token = "token"

bot = telebot.TeleBot(token=token)

engine = create_engine(f'sqlite:///cab.db')

from create_db import User, Base

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
