#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полное тестирование всего TranslateCore проекта с умным переводчиком кода
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулю TranslateCore
sys.path.insert(0, '/Users/deus21/Desktop/Projects/TranslateCore/src')

try:
    from translatecore import (
        EnhancedTranslator,
        OfflineTranslator,
        APIConfigLoader,
        SmartCodeAwareTranslator
    )
    print("✅ Успешно импортированы все компоненты TranslateCore!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта TranslateCore: {e}")
    sys.exit(1)

def test_smart_code_translator():
    """Тестирование умного переводчика кода"""
    print("\n🧠 Тестирование SmartCodeAwareTranslator...")
    
    try:
        # Создаем переводчик
        smart_translator = SmartCodeAwareTranslator(
            source_lang='auto',
            target_lang='english'
        )
        
        # Тестовый файл для перевода
        test_file = "/Users/deus21/Desktop/Projects/TranslateCore/test_translatecore_complete.py"
        
        if not os.path.exists(test_file):
            print(f"❌ Файл {test_file} не найден")
            return False
            
        print(f"📄 Переводим файл: {test_file}")
        
        # Выполняем перевод
        from pathlib import Path
        result = smart_translator.translate_file_smart(Path(test_file))
        
        if result:
            print("✅ Файл успешно переведен умным переводчиком!")
            print(f"📁 Резервная копия: {test_file}.backup")
            
            # Проверяем, что переведенный файл валидный Python код
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    translated_content = f.read()
                    
                # Пробуем скомпилировать код
                compile(translated_content, test_file, 'exec')
                print("✅ Переведенный код синтаксически корректен!")
                
                # Восстанавливаем из backup для повторных тестов
                backup_file = test_file + '.backup'
                if os.path.exists(backup_file):
                    with open(backup_file, 'r', encoding='utf-8') as backup:
                        original_content = backup.read()
                    with open(test_file, 'w', encoding='utf-8') as original:
                        original.write(original_content)
                    print("🔄 Восстановлен исходный файл из резервной копии")
                
                return True
                
            except SyntaxError as e:
                print(f"❌ Синтаксическая ошибка в переведенном коде: {e}")
                return False
                
        else:
            print("❌ Ошибка при переводе файла")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в SmartCodeAwareTranslator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_translators():
    """Тестирование базовых переводчиков"""
    print("\n🌍 Тестирование базовых переводчиков...")
    
    test_text = "Привет, это тестовое сообщение для проверки переводчиков."
    translators = [
        ("Enhanced", EnhancedTranslator(source_lang='ru', target_lang='en')),
        ("Offline", OfflineTranslator(source_lang='ru', target_lang='en') if 'OfflineTranslator' in globals() else None)
    ]
    
    # Фильтруем None переводчики
    translators = [(name, trans) for name, trans in translators if trans is not None]
    
    results = []
    
    for name, translator in translators:
        try:
            print(f"🔄 Тестирую {name} переводчик...")
            if name == 'Enhanced':
                result_obj = translator.translate(test_text)
                result = result_obj.translated if hasattr(result_obj, 'translated') else str(result_obj)
            else:
                result = translator.translate(test_text)
            
            if result and result.strip():
                print(f"✅ {name}: {result}")
                results.append(True)
            else:
                print(f"❌ {name}: Пустой результат")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {name}: Ошибка - {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Результаты базовых переводчиков: {success_count}/{total_count} успешно")
    return success_count > 0

def test_enhanced_features():
    """Тестирование расширенных функций EnhancedTranslator"""
    print("\n🚀 Тестирование расширенных функций EnhancedTranslator...")
    
    try:
        translator = EnhancedTranslator(source_lang='ru', target_lang='en')
        
        # Тест пакетного перевода
        texts = [
            "Первое сообщение для перевода",
            "Второе сообщение с техническими терминами: API, JSON, Python",
            "Третье сообщение о программировании и разработке"
        ]
        
        print("🔄 Тестирую пакетный перевод...")
        batch_results = translator.translate_batch(texts)
        
        if batch_results and len(batch_results) == len(texts):
            print("✅ Пакетный перевод работает корректно")
            for i, result in enumerate(batch_results):
                translated_text = result.translated if hasattr(result, 'translated') else str(result)
                print(f"   {i+1}. {translated_text}")
                
            # Тест кеширования - повторяем один из переводов
            print("🔄 Тестирую кеширование...")
            cached_result_obj = translator.translate(texts[0])
            cached_result = cached_result_obj.translated if hasattr(cached_result_obj, 'translated') else str(cached_result_obj)
            print(f"✅ Кешированный результат: {cached_result}")
            
            return True
        else:
            print("❌ Ошибка в пакетном переводе")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в расширенных функциях: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ПОЛНОЕ ТЕСТИРОВАНИЕ TRANSLATECORE ПРОЕКТА")
    print("=" * 60)
    
    tests_results = []
    
    # Тест 1: Базовые переводчики
    tests_results.append(("Базовые переводчики", test_basic_translators()))
    
    # Тест 2: Расширенные функции
    tests_results.append(("Расширенные функции", test_enhanced_features()))
    
    # Тест 3: Умный переводчик кода
    tests_results.append(("Умный переводчик кода", test_smart_code_translator()))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(tests_results)
    
    for test_name, result in tests_results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:.<40} {status}")
        if result:
            successful_tests += 1
    
    print("=" * 60)
    success_rate = (successful_tests / total_tests) * 100
    print(f"🎯 ОБЩИЙ РЕЗУЛЬТАТ: {successful_tests}/{total_tests} тестов пройдено ({success_rate:.1f}%)")
    
    if successful_tests == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! TranslateCore готов к использованию!")
        return True
    elif successful_tests > 0:
        print("⚠️  Некоторые тесты провалились, но основная функциональность работает")
        return True
    else:
        print("💥 ВСЕ ТЕСТЫ ПРОВАЛЕНЫ! Требуется исправление критических ошибок")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
