"""
Integration tests for chat_service module.
Tests ChatService class methods: get_chat_history, add_message, clear_chat_history.
"""

import pytest
from datetime import datetime, timedelta
from src.flask_app import app, db, ChatMessage, ChatSession
from src.chat_service import ChatService


@pytest.fixture
def test_app():
    """Create and configure a test application instance."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def chat_service(test_app):
    """Create a ChatService instance for testing."""
    return ChatService(database=db)


@pytest.fixture
def session_with_messages(test_app):
    """Create a session with a set of test messages."""
    with test_app.app_context():
        # Create a chat session
        session = ChatSession(chat_id=12345, messages=[])
        db.session.add(session)
        db.session.commit()
        
        # Create 10 messages with incrementing dates
        base_date = datetime(2026, 1, 1, 12, 0, 0)
        for i in range(10):
            message = ChatMessage(
                chat_id=session.id,
                text=f"Message {i}",
                date=base_date + timedelta(hours=i),
                role="user" if i % 2 == 0 else "model"
            )
            db.session.add(message)
        db.session.commit()
        
        yield session.id


@pytest.fixture
def empty_session(test_app):
    """Create an empty session for testing."""
    with test_app.app_context():
        session = ChatSession(chat_id=54321, messages=[])
        db.session.add(session)
        db.session.commit()
        yield session


class TestGetChatHistory:
    """Tests for the get_chat_history method."""
    
    def test_returns_empty_list_when_no_messages(self, test_app, chat_service):
        """Should return empty list when session has no messages."""
        with test_app.app_context():
            # Create empty session
            session = ChatSession(chat_id=99999, messages=[])
            db.session.add(session)
            db.session.commit()
            
            history = chat_service.get_chat_history(session.id)
            
            assert history == []
    
    def test_returns_all_messages_when_below_limit(self, test_app, chat_service, session_with_messages):
        """Should return all messages when count is below the limit."""
        with test_app.app_context():
            # Limit is 50 by default, we have 10 messages
            history = chat_service.get_chat_history(session_with_messages)
            
            assert len(history) == 10
    
    def test_returns_limited_messages_when_above_limit(self, test_app, chat_service, session_with_messages):
        """Should return only last N messages when count exceeds limit."""
        with test_app.app_context():
            # Set limit to 5
            history = chat_service.get_chat_history(session_with_messages, limit=5)
            
            assert len(history) == 5
            # Should be the last 5 messages (Message 5 through Message 9)
            assert history[0]["parts"][0]["text"] == "Message 5"
            assert history[4]["parts"][0]["text"] == "Message 9"
    
    def test_messages_in_chronological_order(self, test_app, chat_service, session_with_messages):
        """Messages should be returned in chronological order (oldest first)."""
        with test_app.app_context():
            history = chat_service.get_chat_history(session_with_messages, limit=5)
            
            # First message should be older (Message 5)
            # Last message should be newer (Message 9)
            assert history[0]["parts"][0]["text"] == "Message 5"
            assert history[-1]["parts"][0]["text"] == "Message 9"
    
    def test_message_format_for_gemini_api(self, test_app, chat_service, session_with_messages):
        """Messages should be formatted correctly for Gemini API."""
        with test_app.app_context():
            history = chat_service.get_chat_history(session_with_messages, limit=2)
            
            # Check structure of first message
            assert "role" in history[0]
            assert "parts" in history[0]
            assert isinstance(history[0]["parts"], list)
            assert "text" in history[0]["parts"][0]
    
    def test_alternating_roles_preserved(self, test_app, chat_service, session_with_messages):
        """User and model roles should be preserved correctly."""
        with test_app.app_context():
            history = chat_service.get_chat_history(session_with_messages, limit=4)
            
            # Messages 6, 7, 8, 9 (user, model, user, model)
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "model"
            assert history[2]["role"] == "user"
            assert history[3]["role"] == "model"
    
    def test_limit_of_one(self, test_app, chat_service, session_with_messages):
        """Should work correctly with limit of 1."""
        with test_app.app_context():
            history = chat_service.get_chat_history(session_with_messages, limit=1)
            
            assert len(history) == 1
            assert history[0]["parts"][0]["text"] == "Message 9"
    
    def test_limit_zero_returns_empty(self, test_app, chat_service, session_with_messages):
        """Limit of 0 should return empty list."""
        with test_app.app_context():
            history = chat_service.get_chat_history(session_with_messages, limit=0)
            
            assert history == []


class TestAddMessage:
    """Tests for the add_message method."""
    
    def test_adds_message_to_session(self, test_app, chat_service, empty_session):
        """Should add a message to the session."""
        with test_app.app_context():
            # Re-fetch session within context
            session = db.session.query(ChatSession).filter_by(chat_id=54321).first()
            message_date = datetime(2026, 1, 15, 10, 30, 0)
            
            result = chat_service.add_message(session, "Hello world", message_date, "user")
            
            assert result is not None
            assert result.text == "Hello world"
            assert result.role == "user"
            assert result.date == message_date
    
    def test_message_persisted_to_database(self, test_app, chat_service, empty_session):
        """Message should be persisted to the database."""
        with test_app.app_context():
            session = db.session.query(ChatSession).filter_by(chat_id=54321).first()
            message_date = datetime(2026, 1, 15, 10, 30, 0)
            
            chat_service.add_message(session, "Test message", message_date, "model")
            
            # Query the database directly
            messages = db.session.query(ChatMessage).filter_by(chat_id=session.id).all()
            assert len(messages) == 1
            assert messages[0].text == "Test message"
    
    def test_returns_chat_message_instance(self, test_app, chat_service, empty_session):
        """Should return a ChatMessage instance."""
        with test_app.app_context():
            session = db.session.query(ChatSession).filter_by(chat_id=54321).first()
            
            result = chat_service.add_message(session, "Test", datetime.now(), "user")
            
            assert isinstance(result, ChatMessage)
    
    def test_multiple_messages_can_be_added(self, test_app, chat_service, empty_session):
        """Should be able to add multiple messages to same session."""
        with test_app.app_context():
            session = db.session.query(ChatSession).filter_by(chat_id=54321).first()
            base_date = datetime(2026, 1, 15, 10, 0, 0)
            
            chat_service.add_message(session, "User message", base_date, "user")
            chat_service.add_message(session, "Model response", base_date + timedelta(seconds=1), "model")
            
            messages = db.session.query(ChatMessage).filter_by(chat_id=session.id).all()
            assert len(messages) == 2


class TestClearChatHistory:
    """Tests for the clear_chat_history method."""
    
    def test_deletes_all_messages(self, test_app, chat_service, session_with_messages):
        """Should delete all messages for a session."""
        with test_app.app_context():
            # Verify messages exist first
            messages_before = db.session.query(ChatMessage).filter_by(chat_id=session_with_messages).count()
            assert messages_before == 10
            
            chat_service.clear_chat_history(session_with_messages)
            
            messages_after = db.session.query(ChatMessage).filter_by(chat_id=session_with_messages).count()
            assert messages_after == 0
    
    def test_returns_deleted_count(self, test_app, chat_service, session_with_messages):
        """Should return the number of deleted messages."""
        with test_app.app_context():
            deleted = chat_service.clear_chat_history(session_with_messages)
            
            assert deleted == 10
    
    def test_returns_zero_when_no_messages(self, test_app, chat_service, empty_session):
        """Should return 0 when session has no messages."""
        with test_app.app_context():
            session = db.session.query(ChatSession).filter_by(chat_id=54321).first()
            
            deleted = chat_service.clear_chat_history(session.id)
            
            assert deleted == 0


class TestChatServiceInit:
    """Tests for ChatService initialization."""
    
    def test_uses_custom_max_history(self, test_app):
        """Should use custom max history when provided."""
        service = ChatService(database=db, max_history_messages=5)
        
        assert service._max_history_messages == 5
    
    def test_default_uses_config_value(self, test_app):
        """Should use config value when no max history provided."""
        from src.config import Config
        service = ChatService(database=db)
        
        assert service._max_history_messages == Config.MAX_HISTORY_MESSAGES
