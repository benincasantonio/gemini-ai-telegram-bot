import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash-lite'