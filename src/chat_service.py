"""
Chat service module for managing chat history and messages.
Implements query-time limiting to prevent unbounded context growth.
Uses async SQLAlchemy 2.0 for FastAPI compatibility.
"""

from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities import ChatSession, ChatMessage
from .config import Config


class ChatService:
    """Service class for managing chat sessions and messages."""
    
    def __init__(self, max_history_messages: int = None):
        """
        Initialize the ChatService.
        
        Args:
            max_history_messages: Maximum messages to retrieve. Defaults to config value.
        """
        self._max_history_messages = max_history_messages or Config.MAX_HISTORY_MESSAGES
    
    async def get_chat_history(self, db: AsyncSession, session_id: int, limit: int = None) -> list[dict]:
        """
        Retrieve chat history for a session, limited to the most recent N messages.
        
        Args:
            db: Async database session.
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
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == session_id)
            .order_by(ChatMessage.date.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
        # Reverse to chronological order and format for Gemini API
        history = []
        for message in reversed(messages):
            history.append({
                "role": message.role,
                "parts": [{"text": message.text}]
            })
        
        return history
    
    async def add_message(self, db: AsyncSession, session_id: int, text: str, date: datetime, role: str) -> ChatMessage:
        """
        Add a message to a chat session.
        
        Args:
            db: Async database session.
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
        db.add(chat_message)
        await db.commit()
        await db.refresh(chat_message)
        return chat_message
    
    async def clear_chat_history(self, db: AsyncSession, session_id: int) -> int:
        """
        Delete all messages for a chat session.
        
        Args:
            db: Async database session.
            session_id: The chat session ID to clear messages for.
        
        Returns:
            The number of messages deleted.
        """
        result = await db.execute(
            delete(ChatMessage).where(ChatMessage.chat_id == session_id)
        )
        await db.commit()
        return result.rowcount

    async def get_or_create_session(self, db: AsyncSession, chat_id: int) -> ChatSession:
        """
        Retrieve an existing chat session or create a new one if it doesn't exist.
        
        Args:
            db: Async database session.
            chat_id: The chat ID to retrieve or create the session for.
            
        Returns:
            The ChatSession instance.
        """
        result = await db.execute(
            select(ChatSession).where(ChatSession.chat_id == chat_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            session = ChatSession(chat_id=chat_id)
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        return session
