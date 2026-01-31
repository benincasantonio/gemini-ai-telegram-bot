"""
Integration tests for chat_service module (async).
Tests ChatService class methods: get_chat_history, add_message, clear_chat_history.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.entities import Base, ChatSession, ChatMessage
from src.chat_service import ChatService


@pytest_asyncio.fixture
async def db_session():
    """Create an async test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def chat_service():
    """Create a ChatService instance for testing."""
    return ChatService()


@pytest_asyncio.fixture
async def session_with_messages(db_session):
    """Create a session with a set of test messages."""
    session = ChatSession(chat_id=12345)
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    
    base_date = datetime(2026, 1, 1, 12, 0, 0)
    for i in range(10):
        message = ChatMessage(
            chat_id=session.id,
            text=f"Message {i}",
            date=base_date + timedelta(hours=i),
            role="user" if i % 2 == 0 else "model"
        )
        db_session.add(message)
    await db_session.commit()
    
    return session.id


@pytest_asyncio.fixture
async def empty_session(db_session):
    """Create an empty session for testing."""
    session = ChatSession(chat_id=54321)
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session.id


class TestGetChatHistory:
    """Tests for the get_chat_history method."""
    
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_messages(self, db_session, chat_service):
        """Should return empty list when session has no messages."""
        session = ChatSession(chat_id=99999)
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        history = await chat_service.get_chat_history(db_session, session.id)
        
        assert history == []
    
    @pytest.mark.asyncio
    async def test_returns_all_messages_when_below_limit(self, db_session, chat_service, session_with_messages):
        """Should return all messages when count is below the limit."""
        history = await chat_service.get_chat_history(db_session, session_with_messages)
        
        assert len(history) == 10
    
    @pytest.mark.asyncio
    async def test_returns_limited_messages_when_above_limit(self, db_session, chat_service, session_with_messages):
        """Should return only last N messages when count exceeds limit."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=5)
        
        assert len(history) == 5
        assert history[0]["parts"][0]["text"] == "Message 5"
        assert history[4]["parts"][0]["text"] == "Message 9"
    
    @pytest.mark.asyncio
    async def test_messages_in_chronological_order(self, db_session, chat_service, session_with_messages):
        """Messages should be returned in chronological order (oldest first)."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=5)
        
        assert history[0]["parts"][0]["text"] == "Message 5"
        assert history[-1]["parts"][0]["text"] == "Message 9"
    
    @pytest.mark.asyncio
    async def test_message_format_for_gemini_api(self, db_session, chat_service, session_with_messages):
        """Messages should be formatted correctly for Gemini API."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=2)
        
        assert "role" in history[0]
        assert "parts" in history[0]
        assert isinstance(history[0]["parts"], list)
        assert "text" in history[0]["parts"][0]
    
    @pytest.mark.asyncio
    async def test_alternating_roles_preserved(self, db_session, chat_service, session_with_messages):
        """User and model roles should be preserved correctly."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=4)
        
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "model"
        assert history[2]["role"] == "user"
        assert history[3]["role"] == "model"
    
    @pytest.mark.asyncio
    async def test_limit_of_one(self, db_session, chat_service, session_with_messages):
        """Should work correctly with limit of 1."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=1)
        
        assert len(history) == 1
        assert history[0]["parts"][0]["text"] == "Message 9"
    
    @pytest.mark.asyncio
    async def test_limit_zero_returns_empty(self, db_session, chat_service, session_with_messages):
        """Limit of 0 should return empty list."""
        history = await chat_service.get_chat_history(db_session, session_with_messages, limit=0)
        
        assert history == []
    
    @pytest.mark.asyncio
    async def test_negative_limit_raises_error(self, db_session, chat_service, session_with_messages):
        """Negative limit should raise ValueError."""
        with pytest.raises(ValueError, match="limit must be non-negative"):
            await chat_service.get_chat_history(db_session, session_with_messages, limit=-1)


class TestAddMessage:
    """Tests for the add_message method."""
    
    @pytest.mark.asyncio
    async def test_adds_message_to_session(self, db_session, chat_service, empty_session):
        """Should add a message using session ID."""
        message_date = datetime(2026, 1, 15, 10, 30, 0)
        
        result = await chat_service.add_message(db_session, empty_session, "Hello world", message_date, "user")
        
        assert result is not None
        assert result.text == "Hello world"
        assert result.role == "user"
        assert result.date == message_date
    
    @pytest.mark.asyncio
    async def test_message_persisted_to_database(self, db_session, chat_service, empty_session):
        """Message should be persisted to the database."""
        message_date = datetime(2026, 1, 15, 10, 30, 0)
        
        await chat_service.add_message(db_session, empty_session, "Test message", message_date, "model")
        
        from sqlalchemy import select
        result = await db_session.execute(select(ChatMessage).where(ChatMessage.chat_id == empty_session))
        messages = result.scalars().all()
        assert len(messages) == 1
        assert messages[0].text == "Test message"
    
    @pytest.mark.asyncio
    async def test_returns_chat_message_instance(self, db_session, chat_service, empty_session):
        """Should return a ChatMessage instance."""
        result = await chat_service.add_message(db_session, empty_session, "Test", datetime.now(), "user")
        
        assert isinstance(result, ChatMessage)
    
    @pytest.mark.asyncio
    async def test_multiple_messages_can_be_added(self, db_session, chat_service, empty_session):
        """Should be able to add multiple messages to same session."""
        base_date = datetime(2026, 1, 15, 10, 0, 0)
        
        await chat_service.add_message(db_session, empty_session, "User message", base_date, "user")
        await chat_service.add_message(db_session, empty_session, "Model response", base_date + timedelta(seconds=1), "model")
        
        from sqlalchemy import select
        result = await db_session.execute(select(ChatMessage).where(ChatMessage.chat_id == empty_session))
        messages = result.scalars().all()
        assert len(messages) == 2


class TestClearChatHistory:
    """Tests for the clear_chat_history method."""
    
    @pytest.mark.asyncio
    async def test_deletes_all_messages(self, db_session, chat_service, session_with_messages):
        """Should delete all messages for a session."""
        from sqlalchemy import select, func
        
        result = await db_session.execute(
            select(func.count()).select_from(ChatMessage).where(ChatMessage.chat_id == session_with_messages)
        )
        messages_before = result.scalar()
        assert messages_before == 10
        
        await chat_service.clear_chat_history(db_session, session_with_messages)
        
        result = await db_session.execute(
            select(func.count()).select_from(ChatMessage).where(ChatMessage.chat_id == session_with_messages)
        )
        messages_after = result.scalar()
        assert messages_after == 0
    
    @pytest.mark.asyncio
    async def test_returns_deleted_count(self, db_session, chat_service, session_with_messages):
        """Should return the number of deleted messages."""
        deleted = await chat_service.clear_chat_history(db_session, session_with_messages)
        
        assert deleted == 10
    
    @pytest.mark.asyncio
    async def test_returns_zero_when_no_messages(self, db_session, chat_service, empty_session):
        """Should return 0 when session has no messages."""
        deleted = await chat_service.clear_chat_history(db_session, empty_session)
        
        assert deleted == 0


class TestGetOrCreateSession:
    """Tests for the get_or_create_session method."""
    
    @pytest.mark.asyncio
    async def test_creates_new_session_when_not_exists(self, db_session, chat_service):
        """Should create a new session when one doesn't exist."""
        session = await chat_service.get_or_create_session(db_session, 11111)
        
        assert session is not None
        assert session.chat_id == 11111
    
    @pytest.mark.asyncio
    async def test_returns_existing_session(self, db_session, chat_service):
        """Should return existing session if it exists."""
        # Create first
        session1 = await chat_service.get_or_create_session(db_session, 22222)
        # Get again
        session2 = await chat_service.get_or_create_session(db_session, 22222)
        
        assert session1.id == session2.id


class TestChatServiceInit:
    """Tests for ChatService initialization."""
    
    def test_uses_custom_max_history(self):
        """Should use custom max history when provided."""
        service = ChatService(max_history_messages=5)
        
        assert service._max_history_messages == 5
    
    def test_default_uses_config_value(self):
        """Should use config value when no max history provided."""
        from src.config import Config
        service = ChatService()
        
        assert service._max_history_messages == Config.MAX_HISTORY_MESSAGES
