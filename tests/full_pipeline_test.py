#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование полного цикла автоперевода с различными сервисами
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def load_translation_configs():
    """Загружает конфигурации переводчиков"""
    try:
        with open('translation_configs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигураций: {e}")
        return None

def backup_test_project():
    """Создает резервную копию тестового проекта"""
    backup_dir = Path("test_project_backup")
    test_dir = Path("test_project")
    
    if backup_dir.exists():
        print("📁 Резервная копия уже существует")
        return True
    
    try:
        subprocess.run(['cp', '-r', str(test_dir), str(backup_dir)], check=True)
        print("✅ Резервная копия создана")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return False

def restore_test_project():
    """Восстанавливает тестовый проект из резервной копии"""
    backup_dir = Path("test_project_backup")
    test_dir = Path("test_project")
    
    if not backup_dir.exists():
        print("❌ Резервная копия не найдена")
        return False
    
    try:
        # Удаляем текущий проект
        subprocess.run(['rm', '-rf', str(test_dir)], check=True)
        # Восстанавливаем из резервной копии
        subprocess.run(['cp', '-r', str(backup_dir), str(test_dir)], check=True)
        print("✅ Тестовый проект восстановлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка восстановления: {e}")
        return False

def test_translation_service(config_name, config_data):
    """Тестирует конкретный сервис перевода"""
    print(f"\n🧪 Тестирование: {config_data['name']}")
    print(f"📝 Описание: {config_data['description']}")
    print(f"🔧 Сервисы: {', '.join(config_data['services'])}")
    print("-" * 60)
    
    # Создаем временный конфигурационный файл для auto_extract_translate.py
    temp_config = {
        "service": "enhanced",  # Используем enhanced_translator
        "source_lang": "ru", 
        "target_lang": "en",
        "enhanced_services": config_data['services'],
        "api_keys": config_data['api_keys']
    }
    
    temp_config_file = f"temp_config_{config_name}.json"
    
    try:
        # Сохраняем временную конфигурацию
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            json.dump(temp_config, f, ensure_ascii=False, indent=2)
        
        # Запускаем полный цикл автоперевода
        cmd = [
            sys.executable, 
            'auto_extract_translate.py',
            '--source-dir', 'test_project',
            '--source-lang', 'ru',
            '--target-lang', 'en', 
            '--service', 'enhanced',
            '--config-file', temp_config_file
        ]
        
        print("🚀 Запуск автоперевода...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Автоперевод завершен успешно!")
            
            # Анализируем результаты
            output_lines = result.stdout.split('\n')
            stats = extract_stats_from_output(output_lines)
            
            print(f"📊 Статистика:")
            for key, value in stats.items():
                print(f"   • {key}: {value}")
            
            return {"success": True, "stats": stats, "output": result.stdout}
            
        else:
            print("❌ Ошибка автоперевода!")
            print(f"Код ошибки: {result.returncode}")
            print(f"Ошибки: {result.stderr}")
            
            return {"success": False, "error": result.stderr, "output": result.stdout}
    
    except subprocess.TimeoutExpired:
        print("❌ Превышено время ожидания (5 минут)")
        return {"success": False, "error": "Timeout"}
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return {"success": False, "error": str(e)}
        
    finally:
        # Удаляем временный файл конфигурации
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)

def extract_stats_from_output(output_lines):
    """Извлекает статистику из вывода программы"""
    stats = {}
    
    for line in output_lines:
        if "найдено текстов" in line.lower():
            # Извлекаем количество найденных текстов
            parts = line.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    stats["Найдено текстов"] = part
                    break
        
        elif "переведено" in line.lower() and "успешно" in line.lower():
            # Извлекаем количество переведенных текстов
            parts = line.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    stats["Переведено"] = part
                    break
        
        elif "создан файл перевода" in line.lower():
            stats["Файл переводов"] = "Создан"
            
        elif "замена завершена" in line.lower():
            stats["Замена в файлах"] = "Выполнена"
    
    return stats

def print_final_report(results):
    """Выводит итоговый отчет по всем тестам"""
    print("\n" + "="*80)
    print("📈 ИТОГОВЫЙ ОТЧЕТ ПО ВСЕМ КОНФИГУРАЦИЯМ")
    print("="*80)
    
    successful = []
    failed = []
    
    for config_name, result in results.items():
        if result["success"]:
            successful.append(config_name)
        else:
            failed.append(config_name)
    
    print(f"\n✅ Успешных конфигураций: {len(successful)}")
    for config in successful:
        print(f"   • {config}")
    
    print(f"\n❌ Неудачных конфигураций: {len(failed)}")
    for config in failed:
        print(f"   • {config}")
    
    if successful:
        print(f"\n🏆 Рекомендуемая конфигурация для использования: {successful[0]}")
    
    print(f"\n📊 Общая статистика:")
    print(f"   • Всего протестировано: {len(results)}")
    print(f"   • Успешность: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")

def main():
    """Основная функция тестирования"""
    print("🌐 ТЕСТИРОВАНИЕ РАЗЛИЧНЫХ СЕРВИСОВ ПЕРЕВОДА")
    print("="*80)
    
    # Загружаем конфигурации
    configs_data = load_translation_configs()
    if not configs_data:
        return
    
    configs = configs_data["configs"]
    
    # Создаем резервную копию тестового проекта
    if not backup_test_project():
        return
    
    # Выбираем конфигурации для тестирования (пропускаем те, что требуют API ключи)
    test_configs = {
        "google_only": configs["google_only"],
        "mixed_free": configs["mixed_free"]
    }
    
    # Если есть API ключи в переменных окружения, добавляем премиум сервисы
    if os.getenv('DEEPL_API_KEY'):
        test_configs["premium_services"] = configs["premium_services"] 
        test_configs["premium_services"]["api_keys"]["deepl"] = os.getenv('DEEPL_API_KEY')
    
    if os.getenv('OPENAI_API_KEY'):
        test_configs["ai_powered"] = configs["ai_powered"]
        test_configs["ai_powered"]["api_keys"]["openai"] = os.getenv('OPENAI_API_KEY')
    
    results = {}
    
    # Тестируем каждую конфигурацию
    for config_name, config_data in test_configs.items():
        try:
            # Восстанавливаем исходное состояние проекта
            restore_test_project()
            
            # Тестируем конфигурацию
            result = test_translation_service(config_name, config_data)
            results[config_name] = result
            
        except KeyboardInterrupt:
            print("\n⏹️ Тестирование прервано пользователем")
            break
        except Exception as e:
            print(f"❌ Критическая ошибка при тестировании {config_name}: {e}")
            results[config_name] = {"success": False, "error": str(e)}
    
    # Выводим итоговый отчет
    print_final_report(results)
    
    # Сохраняем результаты в файл
    with open('full_pipeline_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Подробные результаты сохранены в full_pipeline_test_results.json")
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    main()
