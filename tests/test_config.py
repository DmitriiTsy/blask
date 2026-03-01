"""Tests for configuration."""

import os
from unittest.mock import patch

import pytest

from src.config.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        """Test default settings values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.log_level == "INFO"
            assert settings.environment == "development"
            assert settings.default_model == "gpt-4o-mini"
            assert settings.default_temperature == 0.7

    def test_load_from_env(self):
        """Test loading settings from environment."""
        env_vars = {
            "OPENAI_API_KEY": "test_key",
            "LOG_LEVEL": "DEBUG",
            "ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.openai_api_key == "test_key"
            assert settings.log_level == "DEBUG"
            assert settings.environment == "production"

    def test_optional_keys(self):
        """Test that optional keys can be None."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.openai_api_key is None
            assert settings.anthropic_api_key is None
            assert settings.serpapi_key is None


class TestGetSettings:
    """Tests for get_settings function."""

    def test_singleton_pattern(self):
        """Test that get_settings returns same instance (cached)."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_returns_settings_instance(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
