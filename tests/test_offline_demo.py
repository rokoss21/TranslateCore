#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация полностью автономного оффлайн перевода
"""

from enhanced_translator import EnhancedTranslator
from config_loader import APIConfigLoader, ConfigurationError
import time

def demo_offline_only():
    """Демонстрация конфигурации offline_only"""
    print("🔌 ДЕМОНСТРАЦИЯ ПОЛНОСТЬЮ АВТОНОМНОГО ОФФЛАЙН ПЕРЕВОДА")
    print("=" * 65)
    
    try:
        # Загружаем конфигурацию offline_only
        loader = APIConfigLoader('translation_api_config.json')
        
        print("📋 Проверка конфигурации 'offline_only':")
        validation = loader.validate_config('offline_only')
        
        if validation['valid']:
            print("   ✅ Конфигурация готова к использованию")
        else:
            print("   ❌ Конфигурация содержит ошибки")
            for error in validation['errors']:
                print(f"      • {error}")
            return False
        
        for warning in validation['warnings']:
            print(f"   ⚠️ {warning}")
        
        print("\n🚀 Создание оффлайн переводчика...")
        
        # Создаем переводчик с оффлайн конфигурацией
        translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            config_file='translation_api_config.json',
            service_config_name='offline_only'
        )
        
        # Тестовые фразы на разные темы
        test_phrases = [
            "Привет, мир!",
            "Как дела?",
            "Система работает автономно",
            "Перевод без интернета",
            "Конфиденциальность данных",
            "Оффлайн переводчик работает отлично!",
            "Мы можем переводить тексты даже без подключения к сети",
            "Искусственный интеллект помогает в переводе"
        ]
        
        print(f"\n📝 Тестирование оффлайн перевода ({len(test_phrases)} фраз):")
        print("-" * 65)
        
        total_time = 0
        successful_translations = 0
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n{i}. Исходный текст: '{phrase}'")
            
            start_time = time.time()
            
            try:
                # Выполняем перевод без использования кэша для точности измерений
                result = translator.translate(phrase, use_cache=False)
                
                end_time = time.time()
                translation_time = end_time - start_time
                total_time += translation_time
                
                if hasattr(result, 'success'):
                    # Новый формат TranslationResult
                    if result.success:
                        print(f"   ✅ Перевод: '{result.translated}'")
                        print(f"   🔧 Сервис: {result.service}")
                        print(f"   ⏱️ Время: {translation_time:.2f}с")
                        successful_translations += 1
                        
                        if 'offline' in result.service:
                            print("⚡ ✅ ПОЛНОСТЬЮ АВТОНОМНЫЙ ПЕРЕВОД!")
                    else:
                        print(f"   ❌ Ошибка: {result.error}")
                else:
                    # Старый формат - если есть translated, значит успешно
                    if hasattr(result, 'translated') and result.translated:
                        print(f"   ✅ Перевод: '{result.translated}'")
                        print(f"   🔧 Сервис: {result.service}")
                        print(f"   ⏱️ Время: {translation_time:.2f}с")
                        successful_translations += 1
                        
                        if 'offline' in result.service:
                            print("⚙️ ✅ ПОЛНОСТЬЮ АВТОНОМНЫЙ ПЕРЕВОД!")
                    else:
                        print(f"   ❌ Ошибка: Не удалось получить перевод")
                    
            except Exception as e:
                print(f"   ❌ Исключение: {e}")
        
        # Статистика
        print("\n" + "=" * 65)
        print("📊 СТАТИСТИКА ОФФЛАЙН ПЕРЕВОДА")
        print("=" * 65)
        
        stats = translator.get_stats()
        print(f"📈 Всего запросов: {stats['total_requests']}")
        print(f"✅ Успешных переводов: {successful_translations}")
        print(f"📉 Неудачных переводов: {len(test_phrases) - successful_translations}")
        print(f"⏱️ Общее время: {total_time:.2f}с")
        print(f"🚀 Среднее время на перевод: {total_time/len(test_phrases):.2f}с")
        print(f"🔧 Активные сервисы: {', '.join(stats['active_services'])}")
        print(f"📊 Использование сервисов: {stats['service_usage']}")
        
        # Информация о кэше (если доступна)
        try:
            cache_stats = translator.get_cache_stats()
            print(f"💾 Записей в кэше: {cache_stats['total_entries']}")
            print(f"💾 Размер кэша: {cache_stats['cache_size_mb']:.2f} MB")
        except AttributeError:
            print("💾 Кэш не доступен в данной версии")
        
        print("\n🎯 ПРЕИМУЩЕСТВА ОФФЛАЙН ПЕРЕВОДА:")
        print("  ✅ Полная приватность - данные не покидают устройство")
        print("  ✅ Работает без интернета")
        print("  ✅ Отсутствие лимитов API")
        print("  ✅ Высокая скорость после первого запуска")
        print("  ✅ Отсутствие зависимости от внешних сервисов")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("  • Для лучшего качества установите дополнительные языковые пары Argos")
        print("  • Для продакшн среды используйте конфигурацию 'development' с резервными онлайн сервисами")
        print("  • Регулярно обновляйте языковые модели")
        
        return True
        
    except ConfigurationError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

def show_available_offline_methods():
    """Показывает доступные методы оффлайн перевода"""
    print("\n🔍 ПРОВЕРКА ДОСТУПНЫХ МЕТОДОВ ОФФЛАЙН ПЕРЕВОДА")
    print("=" * 55)
    
    try:
        from offline_translator import OfflineTranslator
        
        translator = OfflineTranslator('russian', 'english')
        
        print("📦 Проверка Argos Translate:")
        try:
            import argostranslate
            print("   ✅ Argos Translate установлен")
            
            # Проверяем установленные пакеты
            installed = argostranslate.package.get_installed_packages()
            print(f"   📋 Установленных языковых пакетов: {len(installed)}")
            
            for package in installed:
                print(f"      • {package.from_code} → {package.to_code}")
                
        except ImportError:
            print("   ❌ Argos Translate не установлен")
        
        print("\n🐳 Проверка LibreTranslate Docker:")
        try:
            if hasattr(translator, 'is_libretranslate_running') and translator.is_libretranslate_running():
                print("   ✅ LibreTranslate контейнер запущен")
            else:
                print("   ❌ LibreTranslate контейнер не запущен")
        except Exception:
            print("   ❌ LibreTranslate контейнер не запущен")
        
        print("\n🌐 Проверка LibreTranslate сервера:")
        try:
            import requests
            response = requests.get("http://localhost:5000", timeout=2)
            print("   ✅ LibreTranslate сервер доступен")
        except:
            print("   ❌ LibreTranslate сервер недоступен")
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

def main():
    """Основная функция демонстрации"""
    show_available_offline_methods()
    
    print("\n" + "=" * 65)
    
    success = demo_offline_only()
    
    print("\n" + "=" * 65)
    if success:
        print("🎉 ДЕМОНСТРАЦИЯ АВТОНОМНОГО ОФФЛАЙН ПЕРЕВОДА ЗАВЕРШЕНА!")
        print("💡 Система готова к полностью автономной работе!")
    else:
        print("❌ Демонстрация завершена с ошибками")
        print("💡 Проверьте установку Argos Translate или запуск LibreTranslate")
    
    print("=" * 65)
    
    print("\n📚 ПОЛЕЗНЫЕ КОМАНДЫ:")
    print("python3 offline_translator.py --list-languages     # Доступные языки")
    print("python3 offline_translator.py --install-deps       # Установка зависимостей")
    print("python3 config_loader.py --validate offline_only   # Проверка конфигурации")

if __name__ == "__main__":
    main()
