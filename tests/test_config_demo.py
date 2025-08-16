#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация использования конфигурационного файла API ключей
"""

from enhanced_translator import EnhancedTranslator
from config_loader import APIConfigLoader, ConfigurationError

def test_development_config():
    """Тест конфигурации для разработки (бесплатные сервисы)"""
    print("🧪 Тест конфигурации 'development'")
    print("-" * 40)
    
    try:
        # Используем конфигурацию development
        translator = EnhancedTranslator(
            source_lang='russian',
            target_lang='english',
            config_file='translation_api_config.json',
            service_config_name='development'
        )
        
        # Тестовые фразы
        test_phrases = [
            "Привет мир!",
            "Система работает корректно",
            "Пользователь не найден"
        ]
        
        print("\n📝 Переводы:")
        for phrase in test_phrases:
            result = translator.translate(phrase, use_cache=False)
            print(f"  '{phrase}' → '{result.translated}' ({result.service})")
        
        # Статистика
        stats = translator.get_stats()
        print(f"\n📊 Статистика:")
        print(f"  • Запросов: {stats['total_requests']}")
        print(f"  • Активные сервисы: {', '.join(stats['active_services'])}")
        print(f"  • Использование сервисов: {stats['service_usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_config_validation():
    """Тестирование валидации конфигураций"""
    print("\n🔍 Проверка всех конфигураций")
    print("=" * 50)
    
    try:
        loader = APIConfigLoader('translation_api_config.json')
        configs = loader.list_available_configs()
        
        for config_name, config_data in configs.items():
            print(f"\n🔧 {config_name}: {config_data['name']}")
            
            # Валидация
            validation = loader.validate_config(config_name)
            
            if validation['valid']:
                print("   ✅ Готова к использованию")
                if validation['available_services']:
                    print(f"   🌐 Доступные сервисы: {len(validation['available_services'])}")
            else:
                print("   ❌ Требует настройки API ключей")
                if validation['missing_keys']:
                    print(f"   🔑 Недостающие: {', '.join(validation['missing_keys'])}")
            
            # Предупреждения
            for warning in validation['warnings']:
                print(f"   ⚠️ {warning}")
                
    except ConfigurationError as e:
        print(f"❌ Ошибка конфигурации: {e}")

def show_setup_instructions():
    """Показывает инструкции по настройке"""
    print("\n" + "=" * 60)
    print("📖 ИНСТРУКЦИИ ПО НАСТРОЙКЕ API КЛЮЧЕЙ")
    print("=" * 60)
    
    instructions = [
        {
            "service": "DeepL (рекомендуется)",
            "steps": [
                "1. Перейдите на https://www.deepl.com/pro-api",
                "2. Создайте бесплатный аккаунт (500K символов/месяц)",
                "3. Получите API ключ в разделе 'Account'",
                "4. Вставьте в translation_api_config.json в поле deepl.key"
            ]
        },
        {
            "service": "OpenAI ChatGPT",
            "steps": [
                "1. Перейдите на https://platform.openai.com",
                "2. Создайте аккаунт ($5 кредитов при регистрации)",
                "3. Получите API ключ в разделе 'API Keys'",
                "4. Вставьте в translation_api_config.json в поле openai.key"
            ]
        },
        {
            "service": "Microsoft Translator",
            "steps": [
                "1. Перейдите на https://azure.microsoft.com",
                "2. Создайте аккаунт (2M символов/месяц бесплатно)",
                "3. Создайте ресурс 'Translator' в Azure",
                "4. Скопируйте ключ в translation_api_config.json"
            ]
        }
    ]
    
    for instruction in instructions:
        print(f"\n🔑 {instruction['service']}")
        for step in instruction['steps']:
            print(f"   {step}")
    
    print(f"\n💡 После настройки API ключей:")
    print(f"   • Используйте 'production_basic' для надежности")
    print(f"   • Используйте 'ai_powered' для ChatGPT переводов")
    print(f"   • Используйте 'multilingual_enterprise' для максимальной надежности")

def demo_different_configs():
    """Демонстрирует различные конфигурации"""
    print("\n" + "=" * 60)
    print("🎯 ДЕМОНСТРАЦИЯ РАЗЛИЧНЫХ КОНФИГУРАЦИЙ")
    print("=" * 60)
    
    # Конфигурации для демонстрации
    demo_configs = [
        {
            'name': 'offline_only',
            'description': 'Полностью автономный оффлайн перевод'
        },
        {
            'name': 'development',
            'description': 'Оффлайн + бесплатные онлайн сервисы'
        }
        # Другие можно добавить при наличии API ключей
    ]
    
    test_phrase = "Добро пожаловать в систему автоперевода!"
    
    for config in demo_configs:
        config_name = config['name']
        print(f"\n📋 Конфигурация: {config_name}")
        print(f"📝 {config['description']}")
        
        try:
            translator = EnhancedTranslator(
                source_lang='russian',
                target_lang='english',
                config_file='translation_api_config.json',
                service_config_name=config_name
            )
            
            result = translator.translate(test_phrase, use_cache=False)
            
            print(f"✅ Результат: '{result.translated}'")
            print(f"🔧 Сервис: {result.service}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    """Основная демонстрация"""
    print("🌐 ДЕМОНСТРАЦИЯ СИСТЕМЫ КОНФИГУРАЦИИ API КЛЮЧЕЙ")
    print("=" * 70)
    
    # Тест валидации конфигураций
    test_config_validation()
    
    # Тест рабочей конфигурации
    if test_development_config():
        print("\n✅ Конфигурация 'development' работает!")
    
    # Демонстрация различных конфигураций
    demo_different_configs()
    
    # Инструкции по настройке
    show_setup_instructions()
    
    print("\n" + "=" * 70)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 70)
    
    print("\n📚 Полезные команды:")
    print("• python3 config_loader.py --list                    # Статус всех конфигураций")
    print("• python3 config_loader.py --validate development    # Проверка конкретной конфигурации")
    print("• python3 enhanced_translator.py \\")
    print("    --config-file translation_api_config.json \\")
    print("    --service-config development \\")
    print("    --text 'Привет мир!'                             # Прямое использование")

if __name__ == "__main__":
    main()
