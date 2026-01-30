"""
Chat service module for managing chat history and messages.
Implements query-time limiting to prevent unbounded context growth.
"""

from datetime import datetime
from .flask_app import db, ChatMessage
from .config import Config


class ChatService:
    """Service class for managing chat sessions and messages."""
    
    def __init__(self, database=None, max_history_messages: int = None):
        """
        Initialize the ChatService.
        
        Args:
            database: SQLAlchemy database instance. Defaults to the app's db.
            max_history_messages: Maximum messages to retrieve. Defaults to config value.
        """
        self._db = database or db
        self._max_history_messages = max_history_messages or Config.MAX_HISTORY_MESSAGES
    
    def get_chat_history(self, session_id: int, limit: int = None) -> list[dict]:
        """
        Retrieve chat history for a session, limited to the most recent N messages.
        
        Args:
            session_id: The chat session ID to retrieve messages for.
            limit: Maximum number of messages to retrieve. Defaults to instance limit.
        
        Returns:
            List of message dicts formatted for Gemini API, in chronological order.
        """
        if limit is None:
            limit = self._max_history_messages
        
        if limit < 0:
            raise ValueError("limit must be non-negative")
        
        # Query messages ordered by date descending, limited to N
        messages = (
            self._db.session.query(ChatMessage)
            .filter_by(chat_id=session_id)
            .order_by(ChatMessage.date.desc())
            .limit(limit)
            .all()
        )
        
        # Reverse to chronological order and format for Gemini API
        history = []
        for message in reversed(messages):
            history.append({
                "role": message.role,
                "parts": [
                    {
                        "text": message.text
                    }
                ]
            })
        
        return history
    
    def add_message(self, session_id: int, text: str, date: datetime, role: str) -> ChatMessage:
        """
        Add a message to a chat session.
        
        Args:
            session_id: The chat session ID to add the message to.
            text: The message text content.
            date: The datetime of the message.
            role: The role of the sender ('user' or 'model').
        
        Returns:
            The created ChatMessage instance.
        """
        chat_message = ChatMessage(
            chat_id=session_id,
            text=text,
            date=date,
            role=role
        )
        self._db.session.add(chat_message)
        self._db.session.commit()
        return chat_message
    
    def clear_chat_history(self, session_id: int) -> int:
        """
        Delete all messages for a chat session.
        
        Args:
            session_id: The chat session ID to clear messages for.
        
        Returns:
            The number of messages deleted.
        """
        deleted_count = self._db.session.query(ChatMessage).filter_by(chat_id=session_id).delete()
        self._db.session.commit()
        return deleted_count
