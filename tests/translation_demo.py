#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация различных сервисов перевода
Показывает качество и особенности каждого сервиса
"""

from enhanced_translator import EnhancedTranslator
import time

def compare_translation_services():
    """Сравнивает качество перевода различных сервисов"""
    
    # Тестовые фразы разной сложности
    test_phrases = [
        {
            "text": "Привет мир!",
            "type": "Простая фраза",
            "expected_quality": "high"
        },
        {
            "text": "Система автоматического перевода работает корректно",
            "type": "Техническая фраза", 
            "expected_quality": "medium"
        },
        {
            "text": "Пользователь не найден в базе данных",
            "type": "Сообщение об ошибке",
            "expected_quality": "high"
        },
        {
            "text": "Добро пожаловать в наше приложение для управления проектами",
            "type": "Приветственное сообщение",
            "expected_quality": "high"
        },
        {
            "text": "Произошла непредвиденная ошибка сервера",
            "type": "Техническая ошибка",
            "expected_quality": "medium"
        }
    ]
    
    # Конфигурации сервисов для тестирования  
    services_configs = [
        {
            "name": "Google Translate",
            "services": ["google"],
            "api_keys": {},
            "expected_availability": True
        },
        {
            "name": "Google + Linguee (комбо)",
            "services": ["google", "linguee"],
            "api_keys": {},
            "expected_availability": True
        }
        # Другие сервисы можно добавить при наличии API ключей
    ]
    
    print("🌐 СРАВНЕНИЕ КАЧЕСТВА ПЕРЕВОДОВ РАЗЛИЧНЫХ СЕРВИСОВ")
    print("=" * 80)
    
    # Заголовок таблицы
    print(f"{'Фраза':<50} {'Сервис':<25} {'Перевод':<30}")
    print("-" * 105)
    
    results = {}
    
    for phrase_data in test_phrases:
        phrase = phrase_data["text"]
        phrase_type = phrase_data["type"]
        
        print(f"\n📝 {phrase_type}: '{phrase}'")
        print("-" * 80)
        
        phrase_results = {}
        
        for service_config in services_configs:
            service_name = service_config["name"]
            
            try:
                # Создаем переводчик
                translator = EnhancedTranslator(
                    source_lang='russian',
                    target_lang='english',
                    preferred_services=service_config['services'],
                    cache_file=f"demo_cache_{service_name.lower().replace(' ', '_')}.json",
                    api_keys=service_config['api_keys']
                )
                
                # Выполняем перевод
                result = translator.translate(phrase, use_cache=False)
                
                # Сохраняем результат
                phrase_results[service_name] = {
                    "translated": result.translated,
                    "service_used": result.service,
                    "confidence": result.confidence,
                    "success": True
                }
                
                # Выводим результат с форматированием
                print(f"✅ {service_name:<25} → '{result.translated}'")
                if result.service != service_config['services'][0]:
                    print(f"   (использован fallback: {result.service})")
                
                time.sleep(0.5)  # Пауза между запросами
                
            except Exception as e:
                phrase_results[service_name] = {
                    "error": str(e),
                    "success": False
                }
                print(f"❌ {service_name:<25} → Ошибка: {e}")
        
        results[phrase] = phrase_results
    
    # Выводим итоговую сводку
    print_comparison_summary(results)
    
    return results

def print_comparison_summary(results):
    """Выводит сводку сравнения сервисов"""
    print("\n" + "=" * 80)
    print("📊 СВОДКА СРАВНЕНИЯ СЕРВИСОВ")
    print("=" * 80)
    
    # Считаем успешность каждого сервиса
    service_stats = {}
    
    for phrase, phrase_results in results.items():
        for service_name, result in phrase_results.items():
            if service_name not in service_stats:
                service_stats[service_name] = {"success": 0, "total": 0, "translations": []}
            
            service_stats[service_name]["total"] += 1
            
            if result.get("success", False):
                service_stats[service_name]["success"] += 1
                service_stats[service_name]["translations"].append(result["translated"])
    
    # Выводим статистику
    for service_name, stats in service_stats.items():
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        print(f"\n🔧 {service_name}")
        print(f"   • Успешность: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        if stats["translations"]:
            print(f"   • Примеры переводов:")
            for i, translation in enumerate(stats["translations"][:3], 1):
                print(f"     {i}. '{translation}'")

def demonstrate_service_features():
    """Демонстрирует специальные возможности сервисов"""
    print("\n" + "=" * 80)
    print("🎯 ДЕМОНСТРАЦИЯ ОСОБЕННОСТЕЙ СЕРВИСОВ")
    print("=" * 80)
    
    print("\n1️⃣ Google Translate - Массовый перевод")
    print("-" * 40)
    
    try:
        google_translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            preferred_services=['google']
        )
        
        batch_phrases = [
            "Загрузка данных...",
            "Сохранение файла",
            "Подключение к серверу",
            "Обновление завершено"
        ]
        
        print("📦 Батчевый перевод:")
        batch_results = google_translator.translate_batch(batch_phrases, show_progress=True)
        
        for i, result in enumerate(batch_results):
            print(f"   {i+1}. '{result.original}' → '{result.translated}'")
        
        # Статистика
        stats = google_translator.get_stats()
        print(f"\n📊 Статистика Google Translate:")
        print(f"   • Запросов: {stats['total_requests']}")
        print(f"   • Попаданий в кеш: {stats['cache_hits']} ({stats['cache_hit_rate']:.1f}%)")
        print(f"   • Размер кеша: {stats['cache_size']} переводов")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации Google Translate: {e}")
    
    print("\n2️⃣ Комбинированный переводчик")
    print("-" * 40)
    
    try:
        combo_translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            preferred_services=['google', 'linguee'],  # Приоритет: Google, затем Linguee
        )
        
        test_phrase = "Выберите файл для загрузки"
        result = combo_translator.translate(test_phrase)
        
        print(f"📝 Тест: '{test_phrase}'")
        print(f"✅ Результат: '{result.translated}' (сервис: {result.service})")
        
    except Exception as e:
        print(f"❌ Ошибка комбинированного переводчика: {e}")

def show_service_recommendations():
    """Показывает рекомендации по выбору сервисов"""
    print("\n" + "=" * 80)
    print("💡 РЕКОМЕНДАЦИИ ПО ВЫБОРУ СЕРВИСОВ")
    print("=" * 80)
    
    recommendations = [
        {
            "scenario": "Разработка и тестирование",
            "service": "Google Translate",
            "reason": "Быстрый, надежный, бесплатный, высокое качество",
            "config": ["google"]
        },
        {
            "scenario": "Продакшн проекты",
            "service": "Комбинированный (Google + DeepL)",
            "reason": "Резервирование + максимальное качество", 
            "config": ["google", "deepl"]
        },
        {
            "scenario": "Конфиденциальные данные",
            "service": "Локальный LibreTranslate",
            "reason": "Полная приватность, собственный сервер",
            "config": ["libre"]
        },
        {
            "scenario": "Словарные переводы",
            "service": "Linguee + PONS",
            "reason": "Точные словарные определения с примерами",
            "config": ["linguee", "pons"]
        },
        {
            "scenario": "Максимальное качество",
            "service": "DeepL Pro",
            "reason": "Лучшее качество перевода, особенно для европейских языков",
            "config": ["deepl"]
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}️⃣ {rec['scenario']}")
        print(f"   🎯 Рекомендация: {rec['service']}")
        print(f"   💡 Причина: {rec['reason']}")
        print(f"   ⚙️ Конфигурация: {rec['config']}")

def main():
    """Основная функция демонстрации"""
    try:
        # Запускаем сравнение сервисов
        results = compare_translation_services()
        
        # Демонстрируем особенности
        demonstrate_service_features()
        
        # Показываем рекомендации
        show_service_recommendations()
        
        print("\n" + "=" * 80)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 80)
        print("\nДля использования различных сервисов:")
        print("1. Установите API ключи в переменные окружения")
        print("2. Используйте auto_extract_translate.py с параметром --service")
        print("3. Настройте enhanced_translator для ваших нужд")
        
    except KeyboardInterrupt:
        print("\n⏹️ Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
