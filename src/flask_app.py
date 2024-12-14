from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Application started')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)
    role = db.Column(db.String(20))


class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    messages = db.relationship('ChatMessage', backref='chat_session')