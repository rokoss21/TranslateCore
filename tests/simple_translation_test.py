#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для LibreTranslate и Google Translate
"""

from enhanced_translator import EnhancedTranslator

def test_simple_translation():
    """Простой тест перевода с разными сервисами"""
    
    test_phrases = [
        "Привет мир!",
        "Как дела?", 
        "Добро пожаловать в наше приложение"
    ]
    
    print("🧪 Тестирование Google Translate")
    print("-" * 40)
    
    # Тестируем Google Translate
    try:
        google_translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            preferred_services=['google'],
            cache_file='google_test_cache.json'
        )
        
        for phrase in test_phrases:
            result = google_translator.translate(phrase, use_cache=False)
            print(f"'{phrase}' → '{result.translated}' ({result.service})")
        
        print(f"✅ Google Translate статистика: {google_translator.get_stats()}")
        
    except Exception as e:
        print(f"❌ Ошибка Google Translate: {e}")
    
    print("\n🧪 Тестирование LibreTranslate")
    print("-" * 40)
    
    # Тестируем LibreTranslate с разными URL
    libre_configs = [
        {'base_url': 'https://libretranslate.de', 'name': 'libretranslate.de'},
        {'base_url': 'https://translate.argosopentech.com', 'name': 'argosopentech.com'},
        {'base_url': 'https://libretranslate.com', 'name': 'libretranslate.com'},
    ]
    
    for config in libre_configs:
        print(f"\n📡 Пробуем сервер: {config['name']}")
        
        try:
            libre_translator = EnhancedTranslator(
                source_lang='russian',
                target_lang='english',
                preferred_services=['libre'],
                cache_file=f"libre_{config['name']}_cache.json",
                api_keys={'libre_url': config['base_url']}
            )
            
            # Тестируем только одну фразу для проверки доступности
            test_phrase = "Привет мир!"
            result = libre_translator.translate(test_phrase, use_cache=False)
            
            if result.service == 'libre':
                print(f"✅ Сервер работает: '{test_phrase}' → '{result.translated}'")
                
                # Если сервер работает, тестируем остальные фразы
                for phrase in test_phrases[1:]:
                    result = libre_translator.translate(phrase, use_cache=False)
                    print(f"  '{phrase}' → '{result.translated}'")
                
                print(f"📊 Статистика: {libre_translator.get_stats()}")
                break  # Если нашли рабочий сервер, останавливаемся
                
            else:
                print(f"❌ Сервер недоступен: {result.service}")
                
        except Exception as e:
            print(f"❌ Ошибка с сервером {config['name']}: {e}")
    
    print("\n🧪 Комбинированный тест")
    print("-" * 40)
    
    # Тестируем комбинированную конфигурацию
    try:
        combined_translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            preferred_services=['google', 'libre'],  # Приоритет: сначала Google, потом LibreTranslate
            cache_file='combined_test_cache.json'
        )
        
        test_phrase = "Система автоматического перевода работает корректно"
        result = combined_translator.translate(test_phrase, use_cache=False)
        
        print(f"✅ Комбинированный результат:")
        print(f"  Оригинал: '{test_phrase}'")
        print(f"  Перевод: '{result.translated}'")
        print(f"  Сервис: {result.service}")
        print(f"  Статистика: {combined_translator.get_stats()}")
        
    except Exception as e:
        print(f"❌ Ошибка комбинированного теста: {e}")

if __name__ == "__main__":
    test_simple_translation()
    print("\n✅ Тестирование завершено!")
