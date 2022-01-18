import telebot
from telegram.client import Telegram, AuthorizationState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import DBManager
from utils import check_photos, TgRequest
from os.path import join, exists
from os import environ
import dotenv
dotenv.load_dotenv('.env')

bot = telebot.TeleBot(token=environ["token"])
engine = create_engine(f'sqlite:///cab.db')

from create_db import User, Base

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
