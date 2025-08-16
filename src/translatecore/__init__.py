"""
TranslateCore - Advanced Translation Library

A powerful, multilingual translation library that combines offline and online translation capabilities.
Supports multiple translation services with automatic fallback, caching, and offline translation using Argos Translate.

Key Features:
- Offline translation with Argos Translate
- Multiple online translation services (Google, DeepL, Microsoft, etc.)
- Automatic service fallback and error handling
- Translation caching for better performance
- Flexible configuration system
- CLI interface for easy use
- Docker support for containerized deployments

Author: AI Assistant
License: MIT
"""

from .enhanced_translator import EnhancedTranslator
from .offline_translator import OfflineTranslator
from .config_loader import APIConfigLoader

__version__ = "1.0.0"
__author__ = "AI Assistant"
__license__ = "MIT"

__all__ = [
    "EnhancedTranslator",
    "OfflineTranslator", 
    "APIConfigLoader",
]
