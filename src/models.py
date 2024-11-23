from .flask_app import db

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    messages = db.relationship('ChatMessage', backref='chat_session')
    