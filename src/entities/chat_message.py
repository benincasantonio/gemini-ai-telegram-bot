"""ChatMessage entity."""

from sqlalchemy import Column, Integer, Text, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ChatMessage(Base):
    """Represents a single message in a chat session."""
    __tablename__ = 'chat_message'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat_session.id'), nullable=False)
    text = Column(Text)
    date = Column(DateTime(timezone=True))  # Supports timezone-aware datetimes
    role = Column(String(20))
    
    session = relationship('ChatSession', back_populates='messages')
