#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки замены переводов
"""

import shutil
from pathlib import Path

# Импортируем функции из основного скрипта
from replace_russian_text import load_translations, load_detailed_data, process_replacement, create_backup

def main():
    """
    Тестовая функция
    """
    # Используем демо файл с переводами
    demo_file = "demo_translations.txt"
    data_file = "russian_text_data.txt"
    
    if not Path(demo_file).exists():
        print(f"Демо файл {demo_file} не найден!")
        return
    
    if not Path(data_file).exists():
        print(f"Файл с данными {data_file} не найден!")
        return
    
    # Загружаем переводы
    print("Загружаем демо переводы...")
    translations = load_translations(demo_file)
    
    if not translations:
        print("Переводы не найдены!")
        return
    
    print(f"Загружено {len(translations)} переводов:")
    for hash_key, (original, translated) in translations.items():
        print(f"  {hash_key[:8]}: '{original}' -> '{translated}'")
    
    # Загружаем детальные данные
    print("\nЗагружаем детальные данные...")
    detailed_data = load_detailed_data(data_file)
    
    # Находим данные для наших переводов
    demo_replacements = {}
    for text_hash, text_type, file_path, line_num, original_text in detailed_data:
        if text_hash in translations:
            original, replacement = translations[text_hash]
            
            if file_path not in demo_replacements:
                demo_replacements[file_path] = []
            
            demo_replacements[file_path].append((line_num, text_type, original, replacement))
            print(f"  Найдена замена в {file_path}:{line_num}")
    
    if not demo_replacements:
        print("Нет данных для демо замены!")
        return
    
    print(f"\nБудет выполнено демо замен в {len(demo_replacements)} файлах")
    
    # Запрашиваем подтверждение
    response = input("Продолжить демо замену? (y/N): ")
    if response.lower() != 'y':
        print("Операция отменена")
        return
    
    # Создаем каталог для резервных копий
    backup_dir = Path("demo_backup")
    backup_dir.mkdir(exist_ok=True)
    
    # Выполняем замены
    for file_path_str, replacements in demo_replacements.items():
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"Файл {file_path} не найден, пропускается")
            continue
        
        print(f"\nОбрабатывается: {file_path}")
        
        # Создаем резервную копию
        backup_file = create_backup(file_path, backup_dir)
        print(f"  Создана резервная копия: {backup_file}")
        
        # Выполняем замены
        if process_replacement(file_path, replacements):
            print(f"  Выполнено {len(replacements)} замен:")
            for line_num, text_type, original, replacement in replacements:
                print(f"    Строка {line_num} ({text_type}): '{original}' -> '{replacement}'")
        else:
            print(f"  Замены не выполнены")
    
    print("\nДемо замена завершена!")
    print("Проверьте результаты и при необходимости восстановите файлы из demo_backup/")

if __name__ == "__main__":
    main()
