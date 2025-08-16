#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование различных сервисов перевода
Демонстрирует работу с LibreTranslate и другими источниками
"""

import json
import time
from pathlib import Path
from enhanced_translator import EnhancedTranslator, TranslationResult

def test_translation_services():
    """Тестируем различные сервисы перевода"""
    
    print("🧪 Тестирование различных сервисов перевода")
    print("=" * 60)
    
    # Тестовые фразы на русском
    test_phrases = [
        "Привет мир!",
        "Как дела?", 
        "Добро пожаловать в наше приложение",
        "Ошибка сети",
        "Данные сохранены успешно",
        "Пользователь не найден"
    ]
    
    # Различные конфигурации сервисов для тестирования
    service_configs = [
        {
            'name': 'Google Translate',
            'services': ['google'],
            'api_keys': {}
        },
        {
            'name': 'LibreTranslate (бесплатный)',
            'services': ['libre'],
            'api_keys': {}
        },
        {
            'name': 'MyMemory',
            'services': ['mymemory'],
            'api_keys': {}
        },
        {
            'name': 'Смешанная конфигурация',
            'services': ['libre', 'google', 'mymemory'],
            'api_keys': {}
        },
        {
            'name': 'Только словарные переводчики',
            'services': ['pons', 'linguee'],
            'api_keys': {}
        }
    ]
    
    results = {}
    
    for config in service_configs:
        print(f"\n🔧 Тестируем конфигурацию: {config['name']}")
        print(f"📋 Сервисы: {', '.join(config['services'])}")
        print("-" * 40)
        
        try:
            # Создаем переводчик для этой конфигурации
            translator = EnhancedTranslator(
                source_lang='russian',
                target_lang='english',
                preferred_services=config['services'],
                cache_file=f"cache_{config['name'].lower().replace(' ', '_')}.json",
                api_keys=config['api_keys']
            )
            
            config_results = []
            
            # Переводим каждую фразу
            for phrase in test_phrases:
                print(f"  • '{phrase}'", end=' → ')
                
                try:
                    result = translator.translate(phrase, use_cache=False)  # Без кеша для чистого теста
                    print(f"'{result.translated}' ({result.service})")
                    
                    config_results.append({
                        'original': phrase,
                        'translated': result.translated,
                        'service': result.service,
                        'success': True
                    })
                    
                    # Небольшая пауза между запросами
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    config_results.append({
                        'original': phrase,
                        'translated': phrase,
                        'service': 'error',
                        'success': False,
                        'error': str(e)
                    })
            
            # Сохраняем результаты
            results[config['name']] = {
                'results': config_results,
                'stats': translator.get_stats()
            }
            
            # Показываем статистику для этой конфигурации
            stats = translator.get_stats()
            print(f"\n📊 Статистика:")
            print(f"   • Всего запросов: {stats['total_requests']}")
            print(f"   • Попаданий в кеш: {stats['cache_hits']}")
            print(f"   • Использование сервисов: {stats['service_usage']}")
            if stats['errors']:
                print(f"   • Ошибки: {len(stats['errors'])}")
                for error in stats['errors'][:3]:  # Показываем первые 3 ошибки
                    print(f"     - {error}")
            
        except Exception as e:
            print(f"❌ Критическая ошибка конфигурации: {e}")
            results[config['name']] = {'error': str(e)}
    
    # Сохраняем общие результаты
    save_test_results(results)
    
    # Показываем сводку
    print_summary(results)

def save_test_results(results):
    """Сохраняет результаты тестирования в файл"""
    results_file = Path('translation_services_test_results.json')
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в {results_file}")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения результатов: {e}")

def print_summary(results):
    """Выводит общую сводку по всем тестам"""
    print("\n" + "=" * 60)
    print("📈 СВОДКА ПО ВСЕМ ТЕСТАМ")
    print("=" * 60)
    
    for config_name, config_data in results.items():
        if 'error' in config_data:
            print(f"❌ {config_name}: Критическая ошибка")
            continue
        
        results_list = config_data.get('results', [])
        stats = config_data.get('stats', {})
        
        successful = len([r for r in results_list if r.get('success', False)])
        total = len(results_list)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"\n📊 {config_name}:")
        print(f"   • Успешность: {successful}/{total} ({success_rate:.1f}%)")
        
        # Показываем используемые сервисы
        services_used = {}
        for result in results_list:
            service = result.get('service', 'unknown')
            services_used[service] = services_used.get(service, 0) + 1
        
        if services_used:
            print(f"   • Сервисы: {dict(services_used)}")
        
        # Показываем время выполнения если есть
        if 'total_requests' in stats:
            print(f"   • Запросов: {stats['total_requests']}")

def test_libre_translate_specifically():
    """Специальный тест LibreTranslate с различными настройками"""
    print("\n" + "=" * 60)
    print("🔍 СПЕЦИАЛЬНОЕ ТЕСТИРОВАНИЕ LIBRETRANSLATE")
    print("=" * 60)
    
    # Тестируем LibreTranslate с разными настройками
    libre_configs = [
        {
            'name': 'LibreTranslate (публичный сервер)',
            'api_keys': {}
        },
        {
            'name': 'LibreTranslate с API ключом',
            'api_keys': {'libre': 'your_api_key_here'}  # Замените на реальный ключ если есть
        }
    ]
    
    test_text = "Добро пожаловать в наше приложение для автоматического перевода!"
    
    for config in libre_configs:
        print(f"\n🧪 Тест: {config['name']}")
        print(f"📝 Тестовый текст: '{test_text}'")
        
        try:
            translator = EnhancedTranslator(
                source_lang='russian',
                target_lang='english',
                preferred_services=['libre'],
                cache_file='libre_test_cache.json',
                api_keys=config['api_keys']
            )
            
            result = translator.translate(test_text)
            
            print(f"✅ Результат: '{result.translated}'")
            print(f"🔧 Сервис: {result.service}")
            print(f"📊 Уверенность: {result.confidence}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    # Запускаем основные тесты
    test_translation_services()
    
    # Запускаем специальные тесты LibreTranslate
    test_libre_translate_specifically()
    
    print("\n✅ Тестирование завершено!")
