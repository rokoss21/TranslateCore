#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для полного цикла автоматического перевода
Проверяет все компоненты системы локализации
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Импортируем наши модули
from config import ProjectConfig, LanguageConfig, create_config_from_preset
from universal_extract import UniversalTextExtractor
from universal_replace import UniversalTextReplacer
from auto_translate import AutoTranslator
from auto_extract_translate import AutoTranslationPipeline


class TestTranslationPipeline(unittest.TestCase):
    """Тесты для полного цикла перевода"""
    
    def setUp(self):
        """Подготовка к тестам"""
        # Создаем временную директорию для тестов
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Создаем тестовый проект
        self.create_test_project()
        
        # Создаем конфигурацию
        self.config = ProjectConfig(
            project_path=str(self.test_dir),
            target_directories=['.'],
            file_patterns=['*.py', '*.js', '*.html', '*.json'],
            exclude_patterns=['*.log', '*.tmp'],
            target_language='russian'
        )
    
    def tearDown(self):
        """Очистка после тестов"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_project(self):
        """Создает тестовый проект с русским текстом"""
        # Python файл
        python_code = '''
def test_function():
    print("Тестовая функция")
    return "Успешно выполнено"

ERROR_MSG = "Произошла ошибка"
SUCCESS_MSG = "Операция завершена"
'''
        (self.test_dir / 'test.py').write_text(python_code, encoding='utf-8')
        
        # JavaScript файл
        js_code = '''
console.log("Инициализация приложения");
const MESSAGES = {
    error: "Ошибка выполнения",
    success: "Задача выполнена"
};
'''
        (self.test_dir / 'app.js').write_text(js_code, encoding='utf-8')
        
        # HTML файл
        html_code = '''
<html>
<head><title>Тестовая страница</title></head>
<body>
    <h1>Добро пожаловать</h1>
    <p>Это тестовое приложение</p>
    <button>Нажмите здесь</button>
</body>
</html>
'''
        (self.test_dir / 'index.html').write_text(html_code, encoding='utf-8')
        
        # JSON файл
        json_data = {
            "title": "Тестовое приложение",
            "description": "Описание для тестирования",
            "messages": {
                "error": "Ошибка системы",
                "info": "Информационное сообщение"
            }
        }
        (self.test_dir / 'config.json').write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2), 
            encoding='utf-8'
        )
    
    def test_text_extraction(self):
        """Тест извлечения русского текста"""
        extractor = UniversalTextExtractor(self.config)
        
        # Извлекаем текст
        extractions, unique_texts = extractor.extract_all()
        
        # Проверяем результаты
        self.assertGreater(len(extractions), 0, "Должны быть найдены русские строки")
        self.assertGreater(len(unique_texts), 0, "Должны быть уникальные тексты")
        
        # Проверяем наличие конкретных строк
        expected_texts = [
            "Тестовая функция",
            "Произошла ошибка", 
            "Инициализация приложения",
            "Добро пожаловать",
            "Тестовое приложение"
        ]
        
        found_texts = set(unique_texts)
        for expected in expected_texts:
            self.assertIn(expected, found_texts, 
                         f"Текст '{expected}' должен быть найден")
        
        print(f"✓ Извлечено {len(extractions)} вхождений, {len(unique_texts)} уникальных")
    
    def test_save_extraction_results(self):
        """Тест сохранения результатов извлечения"""
        extractor = UniversalTextExtractor(self.config)
        extractions, unique_texts = extractor.extract_all()
        
        # Сохраняем результаты
        extractor.save_results(extractions, unique_texts)
        
        # Проверяем созданные файлы
        output_files = self.config.get_output_files()
        
        self.assertTrue(Path(output_files['data']).exists(), 
                       "Файл с данными должен быть создан")
        self.assertTrue(Path(output_files['simple']).exists(), 
                       "Простой файл должен быть создан")
        
        # Проверяем содержимое файлов
        with open(output_files['simple'], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Тестовая функция", content)
            self.assertIn("|", content)  # Разделители должны быть
        
        print("✓ Результаты извлечения сохранены корректно")
    
    @patch('auto_translate.AutoTranslator')
    def test_translation_process(self, mock_translator_class):
        """Тест процесса перевода"""
        # Настраиваем mock переводчика
        mock_translator = MagicMock()
        mock_translator.translate_batch.return_value = [
            "Test function",
            "An error occurred", 
            "Application initialization",
            "Welcome",
            "Test application"
        ]
        mock_translator.get_stats.return_value = {
            'service': 'mock',
            'requests_made': 1,
            'cache_size': 0
        }
        mock_translator_class.return_value = mock_translator
        
        # Создаем тестовые переводы
        test_texts = [
            "Тестовая функция",
            "Произошла ошибка", 
            "Инициализация приложения",
            "Добро пожаловать",
            "Тестовое приложение"
        ]
        
        # Инициализируем переводчик
        translator = AutoTranslator('russian', 'english', service='dictionary')
        translations = translator.translate_batch(test_texts)
        
        # Проверяем результаты
        self.assertEqual(len(translations), len(test_texts))
        self.assertIn("Test function", translations)
        self.assertIn("Welcome", translations)
        
        print("✓ Процесс перевода работает корректно")
    
    def test_text_replacement(self):
        """Тест замены текста переводами"""
        # Сначала извлекаем текст
        extractor = UniversalTextExtractor(self.config)
        extractions, unique_texts = extractor.extract_all()
        extractor.save_results(extractions, unique_texts)
        
        # Создаем файл переводов
        output_files = self.config.get_output_files()
        translations_file = output_files['simple']
        
        # Модифицируем файл переводов (добавляем переводы)
        with open(translations_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_lines = []
        for line in lines:
            if line.startswith('#') or not line.strip():
                translated_lines.append(line)
                continue
            
            parts = line.strip().split('|')
            if len(parts) == 3:
                hash_val, original, _ = parts
                # Простая замена для тестирования
                if "Тестовая функция" in original:
                    translation = "Test function"
                elif "ошибка" in original.lower():
                    translation = "Error occurred"
                elif "Добро пожаловать" in original:
                    translation = "Welcome"
                else:
                    translation = f"EN_{original}"
                
                translated_lines.append(f"{hash_val}|{original}|{translation}\n")
            else:
                translated_lines.append(line)
        
        # Записываем переводы
        with open(translations_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
        
        # Выполняем замену
        replacer = UniversalTextReplacer(self.config)
        success = replacer.replace_all(translations_file, output_files['data'])
        
        self.assertTrue(success, "Замена должна быть успешной")
        
        # Проверяем результаты замены
        translated_py = self.test_dir / 'test.py'
        with open(translated_py, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Test function", content)
            self.assertNotIn("Тестовая функция", content)
        
        print("✓ Замена текста выполнена корректно")
    
    @patch('auto_translate.AutoTranslator')
    def test_full_pipeline(self, mock_translator_class):
        """Тест полного цикла автоматического перевода"""
        # Настраиваем mock
        mock_translator = MagicMock()
        mock_translator.translate_batch.return_value = [
            "Test function", "Error occurred", "Successfully completed",
            "Application initialization", "Execution error", "Task completed",
            "Welcome", "This is test application", "Click here",
            "Test application", "Description for testing", "System error", 
            "Information message"
        ]
        mock_translator.get_stats.return_value = {
            'service': 'mock',
            'requests_made': 1,
            'cache_size': 13
        }
        mock_translator_class.return_value = mock_translator
        
        # Создаем pipeline
        pipeline = AutoTranslationPipeline(
            config=self.config,
            target_language='english',
            translation_service='mock'
        )
        
        # Запускаем полный цикл (без интерактивных элементов)
        success = pipeline.run_full_pipeline(
            review_translations=False,
            auto_replace=True
        )
        
        self.assertTrue(success, "Pipeline должен завершиться успешно")
        
        # Проверяем результаты
        output_files = self.config.get_output_files()
        self.assertTrue(Path(output_files['simple']).exists())
        
        # Проверяем переведенные файлы
        translated_py = self.test_dir / 'test.py'
        with open(translated_py, 'r', encoding='utf-8') as f:
            content = f.read()
            # Должны остаться английские переводы
            self.assertIn("Test function", content)
            
        print("✓ Полный pipeline выполнен успешно")
    
    def test_config_validation(self):
        """Тест валидации конфигурации"""
        # Проверяем корректную конфигурацию
        self.assertTrue(self.config.project_path.exists())
        self.assertIn('russian', LanguageConfig.get_available_languages())
        
        # Проверяем получение файлов вывода
        output_files = self.config.get_output_files()
        self.assertIn('data', output_files)
        self.assertIn('simple', output_files)
        self.assertIn('backup', output_files)
        
        print("✓ Конфигурация валидна")
    
    def test_preset_configs(self):
        """Тест предустановленных конфигураций"""
        # Тестируем создание конфигурации из preset
        config = create_config_from_preset(
            'python_project',
            project_path=str(self.test_dir)
        )
        
        self.assertIsNotNone(config)
        self.assertEqual(str(config.project_path), str(self.test_dir))
        self.assertIn('*.py', config.file_patterns)
        
        print("✓ Preset конфигурации работают корректно")


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев и ошибок"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_empty_project(self):
        """Тест на пустом проекте"""
        config = ProjectConfig(
            project_path=str(self.test_dir),
            target_directories=['.'],
            file_patterns=['*.py'],
            target_language='russian'
        )
        
        extractor = UniversalTextExtractor(config)
        extractions, unique_texts = extractor.extract_all()
        
        self.assertEqual(len(extractions), 0)
        self.assertEqual(len(unique_texts), 0)
        
        print("✓ Пустой проект обработан корректно")
    
    def test_invalid_file_patterns(self):
        """Тест с некорректными паттернами файлов"""
        # Создаем файл без русского текста
        (self.test_dir / 'empty.py').write_text('# Empty file\npass\n')
        
        config = ProjectConfig(
            project_path=str(self.test_dir),
            target_directories=['.'],
            file_patterns=['*.py'],
            target_language='russian'
        )
        
        extractor = UniversalTextExtractor(config)
        extractions, unique_texts = extractor.extract_all()
        
        self.assertEqual(len(extractions), 0)
        
        print("✓ Файлы без русского текста обработаны корректно")
    
    def test_malformed_translation_file(self):
        """Тест с некорректным файлом переводов"""
        config = ProjectConfig(
            project_path=str(self.test_dir),
            target_directories=['.'],
            file_patterns=['*.py'],
            target_language='russian'
        )
        
        # Создаем некорректный файл переводов
        bad_translation_file = self.test_dir / 'bad_translations.txt'
        bad_translation_file.write_text('invalid|format|missing|parts\n')
        
        replacer = UniversalTextReplacer(config)
        
        # Создаем пустой файл данных
        data_file = self.test_dir / 'data.json'
        data_file.write_text('[]')
        
        # Это должно обработаться без ошибок
        success = replacer.replace_all(str(bad_translation_file), str(data_file))
        
        # Может быть False из-за отсутствия замен, но не должно падать
        print("✓ Некорректный файл переводов обработан")


def run_all_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов системы автоматического перевода")
    print("=" * 60)
    
    # Создаем test suite
    suite = unittest.TestSuite()
    
    # Добавляем тесты основного функционала
    suite.addTest(TestTranslationPipeline('test_config_validation'))
    suite.addTest(TestTranslationPipeline('test_preset_configs'))
    suite.addTest(TestTranslationPipeline('test_text_extraction'))
    suite.addTest(TestTranslationPipeline('test_save_extraction_results'))
    suite.addTest(TestTranslationPipeline('test_translation_process'))
    suite.addTest(TestTranslationPipeline('test_text_replacement'))
    suite.addTest(TestTranslationPipeline('test_full_pipeline'))
    
    # Добавляем тесты граничных случаев
    suite.addTest(TestEdgeCases('test_empty_project'))
    suite.addTest(TestEdgeCases('test_invalid_file_patterns'))
    suite.addTest(TestEdgeCases('test_malformed_translation_file'))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результаты
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Все тесты прошли успешно!")
        print(f"Выполнено тестов: {result.testsRun}")
    else:
        print(f"❌ Тесты завершились с ошибками:")
        print(f"Выполнено: {result.testsRun}")
        print(f"Ошибки: {len(result.errors)}")
        print(f"Неудачи: {len(result.failures)}")
        
        # Показываем подробности ошибок
        for test, error in result.errors:
            print(f"\n❌ Ошибка в {test}: {error}")
        
        for test, failure in result.failures:
            print(f"\n❌ Неудача в {test}: {failure}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
