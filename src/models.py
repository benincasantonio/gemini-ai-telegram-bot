from .telegram_bot_api import db

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)
    messages = db.relationship('ChatMessage', backref='chat_session')
    