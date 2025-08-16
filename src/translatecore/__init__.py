"""
TranslateCore - Advanced Translation Library

A powerful, multilingual translation library that combines offline and online translation capabilities.
Supports multiple translation services with automatic fallback, caching, and smart code-aware translation.

Key Features:
- Offline translation with Argos Translate
- Multiple online translation services (Google, DeepL, Microsoft, etc.)
- Smart code-aware translation (NEW in v1.1.4!)
- Automatic service fallback and error handling
- Translation caching for better performance
- Flexible configuration system
- CLI interface for easy use
- Docker support for containerized deployments

Author: Emil Rokossovskiy
License: MIT
"""

from .enhanced_translator import EnhancedTranslator
from .offline_translator import OfflineTranslator
from .config_loader import APIConfigLoader
from .smart_code_translator import SmartCodeAwareTranslator

__version__ = "1.1.4"
__author__ = "Emil Rokossovskiy"
__license__ = "MIT"

__all__ = [
    "EnhancedTranslator",
    "OfflineTranslator", 
    "APIConfigLoader",
    "SmartCodeAwareTranslator",
]
