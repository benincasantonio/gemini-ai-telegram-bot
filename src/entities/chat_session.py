"""ChatSession entity."""

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from .base import Base


class ChatSession(Base):
    """Represents a chat session with a user."""
    __tablename__ = 'chat_session'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    messages = relationship('ChatMessage', back_populates='session', cascade='all, delete-orphan')
