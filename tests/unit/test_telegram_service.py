"""
Unit tests for TelegramService.
Tests security-related methods (no actual Telegram API calls).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSecureWebhook:
    """Tests for secure webhook functionality."""
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'})
    def test_is_secure_webhook_enabled_default(self):
        """Secure webhook should be enabled by default."""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}, clear=True):
            from src.services.telegram_service import TelegramService
            with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
                service = TelegramService()
                assert service.is_secure_webhook_enabled() is True
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'ENABLE_SECURE_WEBHOOK_TOKEN': 'True'})
    def test_is_secure_webhook_enabled_true(self):
        """Secure webhook should be enabled when set to True."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_enabled() is True
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'ENABLE_SECURE_WEBHOOK_TOKEN': 'False'})
    def test_is_secure_webhook_disabled(self):
        """Secure webhook should be disabled when set to False."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_enabled() is False
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_WEBHOOK_SECRET': 'my_secret'})
    def test_get_secure_webhook_token(self):
        """Should return the webhook secret from environment."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.get_secure_webhook_token() == "my_secret"
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}, clear=True)
    def test_get_secure_webhook_token_not_set(self):
        """Should return None when webhook secret is not set."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.get_secure_webhook_token() is None


class TestTokenValidation:
    """Tests for webhook token validation."""
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_WEBHOOK_SECRET': 'valid_secret'})
    def test_valid_token_returns_true(self):
        """Valid token should return True."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_token_valid("valid_secret") is True
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_WEBHOOK_SECRET': 'valid_secret'})
    def test_invalid_token_returns_false(self):
        """Invalid token should return False."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_token_valid("wrong_secret") is False
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_WEBHOOK_SECRET': 'valid_secret'})
    def test_none_token_returns_false(self):
        """None token should return False."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_token_valid(None) is False
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}, clear=True)  
    def test_no_secret_set_returns_false(self):
        """Should return False when no secret is configured."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_token_valid("any_token") is False
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_WEBHOOK_SECRET': 'secret'})
    def test_empty_string_token_returns_false(self):
        """Empty string token should return False."""
        from src.services.telegram_service import TelegramService
        with patch.object(TelegramService, '__init__', lambda self: setattr(self, '_telegram_app_bot', None)):
            service = TelegramService()
            assert service.is_secure_webhook_token_valid("") is False
