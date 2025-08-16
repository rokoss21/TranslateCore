#!/usr/bin/env python3
"""
Basic Usage Examples for TranslateCore

This script demonstrates the basic functionality of TranslateCore including:
- Simple text translation
- Offline translation
- Configuration usage
- Error handling
"""

import sys
import os

# Add src directory to path for examples
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from translatecore import EnhancedTranslator, OfflineTranslator


def example_basic_translation():
    """Demonstrate basic translation functionality"""
    print("🌍 Basic Translation Example")
    print("=" * 50)
    
    # Initialize translator with default configuration
    translator = EnhancedTranslator()
    
    # Simple translation
    text = "Hello, world!"
    result = translator.translate(text, target_lang="es")
    print(f"Original: {text}")
    print(f"Spanish: {result.translated_text}")
    print(f"Service used: {result.service_used}")
    print(f"Translation time: {result.translation_time:.2f}s")
    print()


def example_offline_translation():
    """Demonstrate offline-only translation"""
    print("🔌 Offline Translation Example")
    print("=" * 50)
    
    # Use offline-only configuration
    translator = EnhancedTranslator(config_name="offline_only")
    
    try:
        text = "Privacy is important"
        result = translator.translate(text, source_lang="en", target_lang="es")
        print(f"Original: {text}")
        print(f"Spanish: {result.translated_text}")
        print(f"✅ Translated completely offline!")
        print(f"Service used: {result.service_used}")
        print()
    except Exception as e:
        print(f"❌ Offline translation failed: {e}")
        print("Make sure Argos Translate packages are installed.")
        print()


def example_language_detection():
    """Demonstrate automatic language detection"""
    print("🔍 Language Detection Example")
    print("=" * 50)
    
    translator = EnhancedTranslator()
    
    texts = [
        "Hello, how are you?",
        "Bonjour, comment allez-vous?",
        "Hola, ¿cómo estás?",
        "Привет, как дела?",
        "こんにちは、元気ですか？"
    ]
    
    for text in texts:
        try:
            # Let the translator detect the language automatically
            result = translator.translate(text, source_lang="auto", target_lang="en")
            print(f"Text: {text}")
            print(f"Detected language: {result.source_language}")
            print(f"English: {result.translated_text}")
            print("-" * 30)
        except Exception as e:
            print(f"❌ Translation failed for '{text}': {e}")
    print()


def example_batch_translation():
    """Demonstrate batch translation"""
    print("📦 Batch Translation Example")
    print("=" * 50)
    
    translator = EnhancedTranslator()
    
    texts = [
        "Good morning!",
        "How are you today?",
        "The weather is nice.",
        "See you later!",
        "Thank you very much!"
    ]
    
    print("Translating multiple texts to Spanish...")
    try:
        for text in texts:
            result = translator.translate(text, target_lang="es")
            print(f"{text} → {result.translated_text}")
    except Exception as e:
        print(f"❌ Batch translation failed: {e}")
    print()


def example_error_handling():
    """Demonstrate proper error handling"""
    print("⚠️ Error Handling Example")
    print("=" * 50)
    
    translator = EnhancedTranslator()
    
    # Try to translate to an invalid language
    try:
        result = translator.translate("Hello", target_lang="invalid_language")
        print(f"Translation: {result.translated_text}")
    except Exception as e:
        print(f"❌ Expected error caught: {type(e).__name__}: {e}")
    
    # Try empty text
    try:
        result = translator.translate("", target_lang="es")
        print(f"Empty text translation: '{result.translated_text}'")
    except Exception as e:
        print(f"❌ Empty text error: {type(e).__name__}: {e}")
    print()


def example_configuration_comparison():
    """Compare different configurations"""
    print("⚙️ Configuration Comparison")
    print("=" * 50)
    
    configs = ["offline_only", "development", "privacy_focused"]
    text = "This is a test translation"
    
    for config in configs:
        try:
            translator = EnhancedTranslator(config_name=config)
            result = translator.translate(text, target_lang="es")
            print(f"Config '{config}':")
            print(f"  Translation: {result.translated_text}")
            print(f"  Service: {result.service_used}")
            print(f"  Time: {result.translation_time:.2f}s")
        except Exception as e:
            print(f"Config '{config}': ❌ {e}")
        print()


def main():
    """Run all examples"""
    print("🚀 TranslateCore Examples")
    print("=" * 70)
    print()
    
    try:
        example_basic_translation()
        example_offline_translation()
        example_language_detection()
        example_batch_translation()
        example_error_handling()
        example_configuration_comparison()
        
        print("✅ All examples completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
