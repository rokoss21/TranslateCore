#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TranslateCore CLI - Продвинутая утилита командной строки для перевода
Максимальное удобство для пользователя
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import time
import subprocess
import signal
from datetime import datetime

# Импорты наших модулей
try:
    from .enhanced_translator import EnhancedTranslator
    from .offline_translator import OfflineTranslator
    from .config_loader import APIConfigLoader, ConfigurationError
except ImportError as e:
    # Fallback для запуска из корневой директории
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.translatecore.enhanced_translator import EnhancedTranslator
        from src.translatecore.offline_translator import OfflineTranslator
        from src.translatecore.config_loader import APIConfigLoader, ConfigurationError
    except ImportError:
        print(f"❌ Ошибка импорта модулей: {e}")
        print("💡 Убедитесь, что вы запускаете из правильной директории")
        sys.exit(1)

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored_print(text: str, color: str = Colors.ENDC, bold: bool = False):
    """Печать цветного текста"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.ENDC}")
    else:
        print(f"{color}{text}{Colors.ENDC}")

def print_banner():
    """Красивый баннер утилиты"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     🌍 TranslateCore CLI                     ║
║              Мощная утилита для перевода текстов             ║
║                   Оффлайн + Онлайн сервисы                   ║
╚══════════════════════════════════════════════════════════════╝
"""
    colored_print(banner, Colors.CYAN, bold=True)

def print_error(message: str):
    """Печать ошибки"""
    colored_print(f"❌ {message}", Colors.FAIL)

def print_success(message: str):
    """Печать успеха"""
    colored_print(f"✅ {message}", Colors.GREEN)

def print_warning(message: str):
    """Печать предупреждения"""
    colored_print(f"⚠️ {message}", Colors.WARNING)

def print_info(message: str):
    """Печать информации"""
    colored_print(f"💡 {message}", Colors.BLUE)

class TranslateCLI:
    """Основной класс CLI утилиты"""
    
    def __init__(self):
        self.config_file = "translation_api_config.json"
        self.translator = None
        self.history_file = Path.home() / ".translate_history.json"
        self.settings_file = Path.home() / ".translate_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Загружает настройки пользователя"""
        default_settings = {
            'default_source': 'auto',
            'default_target': 'english',
            'default_service_config': 'development',
            'show_stats': True,
            'save_history': True,
            'use_colors': True,
            'preferred_method': 'auto'
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    default_settings.update(user_settings)
            except Exception as e:
                print_warning(f"Ошибка загрузки настроек: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Сохраняет настройки пользователя"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print_warning(f"Ошибка сохранения настроек: {e}")
    
    def get_language_choices(self) -> List[str]:
        """Возвращает список доступных языков"""
        base_languages = ['auto', 'russian', 'english', 'chinese', 'japanese', 'korean', 
                         'german', 'french', 'spanish', 'italian', 'portuguese', 
                         'arabic', 'dutch', 'czech', 'ukrainian', 'polish']
        return base_languages
    
    def get_config_choices(self) -> List[str]:
        """Возвращает список доступных конфигураций"""
        try:
            if Path(self.config_file).exists():
                loader = APIConfigLoader(self.config_file)
                return list(loader.list_available_configs().keys())
        except:
            pass
        return ['offline_only', 'development', 'production_basic']
    
    def detect_language(self, text: str) -> str:
        """Простое определение языка"""
        # Проверяем на кириллицу
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        if cyrillic_chars / len(text) > 0.3:
            return 'russian'
        
        # Проверяем на китайские иероглифы
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > 0:
            return 'chinese'
        
        # По умолчанию английский
        return 'english'
    
    def smart_translate(self, text: str, source_lang: str = None, target_lang: str = None, 
                       service_config: str = None) -> Dict[str, Any]:
        """Умный перевод с автоопределением"""
        
        # Автоопределение исходного языка
        if not source_lang or source_lang == 'auto':
            source_lang = self.detect_language(text)
            print_info(f"Определен исходный язык: {source_lang}")
        
        # Целевой язык по умолчанию
        if not target_lang:
            target_lang = 'english' if source_lang != 'english' else 'russian'
            print_info(f"Целевой язык: {target_lang}")
        
        # Сервис по умолчанию
        service_config = service_config or self.settings['default_service_config']
        
        start_time = time.time()
        
        try:
            # Создаем переводчик
            translator = EnhancedTranslator(
                source_lang=source_lang,
                target_lang=target_lang,
                config_file=self.config_file,
                service_config_name=service_config
            )
            
            # Переводим
            result = translator.translate(text)
            
            processing_time = time.time() - start_time
            
            # Сохраняем в историю
            if self.settings['save_history']:
                self.save_to_history(text, result.translated, source_lang, target_lang, result.service)
            
            return {
                'success': True,
                'original': text,
                'translated': result.translated,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'service': result.service,
                'processing_time': processing_time,
                'stats': translator.get_stats() if hasattr(translator, 'get_stats') else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }
    
    def save_to_history(self, original: str, translated: str, source_lang: str, 
                       target_lang: str, service: str):
        """Сохраняет перевод в историю"""
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            history.append({
                'timestamp': datetime.now().isoformat(),
                'original': original,
                'translated': translated,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'service': service
            })
            
            # Оставляем только последние 100 записей
            history = history[-100:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print_warning(f"Ошибка сохранения истории: {e}")
    
    def show_history(self, limit: int = 10):
        """Показывает историю переводов"""
        if not self.history_file.exists():
            print_info("История переводов пуста")
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                print_info("История переводов пуста")
                return
            
            colored_print("\n📚 История переводов:", Colors.HEADER, bold=True)
            print("=" * 70)
            
            for i, entry in enumerate(reversed(history[-limit:]), 1):
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
                
                print(f"\n{i}. [{timestamp}] {entry['source_lang']} → {entry['target_lang']}")
                colored_print(f"   📝 {entry['original']}", Colors.CYAN)
                colored_print(f"   🔄 {entry['translated']}", Colors.GREEN)
                colored_print(f"   🔧 {entry['service']}", Colors.WARNING)
                
        except Exception as e:
            print_error(f"Ошибка загрузки истории: {e}")
    
    def interactive_mode(self):
        """Интерактивный режим работы"""
        print_banner()
        colored_print("🎯 Интерактивный режим перевода", Colors.HEADER, bold=True)
        print("Введите 'help' для справки, 'quit' для выхода\n")
        
        while True:
            try:
                # Получаем текст от пользователя
                colored_print("💬 Введите текст для перевода:", Colors.BLUE, bold=True)
                text = input("➤ ").strip()
                
                if not text:
                    continue
                
                if text.lower() in ['quit', 'exit', 'q']:
                    colored_print("👋 До свидания!", Colors.GREEN, bold=True)
                    break
                
                if text.lower() == 'help':
                    self.show_interactive_help()
                    continue
                
                if text.lower() == 'settings':
                    self.interactive_settings()
                    continue
                
                if text.lower() == 'history':
                    self.show_history()
                    continue
                
                if text.lower() == 'stats':
                    self.show_system_stats()
                    continue
                
                # Переводим
                result = self.smart_translate(text)
                
                if result['success']:
                    print("\n" + "─" * 50)
                    colored_print(f"📝 Оригинал:  {result['original']}", Colors.CYAN)
                    colored_print(f"🔄 Перевод:   {result['translated']}", Colors.GREEN, bold=True)
                    colored_print(f"🌐 Маршрут:   {result['source_lang']} → {result['target_lang']}", Colors.WARNING)
                    colored_print(f"🔧 Сервис:    {result['service']}", Colors.BLUE)
                    colored_print(f"⏱️ Время:     {result['processing_time']:.2f}с", Colors.WARNING)
                    
                    if result['stats'] and self.settings['show_stats']:
                        stats = result['stats']
                        colored_print(f"📊 Статистика: {stats['total_requests']} запросов", Colors.BLUE)
                else:
                    print_error(f"Ошибка перевода: {result['error']}")
                
                print("─" * 50 + "\n")
                
            except KeyboardInterrupt:
                colored_print("\n👋 До свидания!", Colors.GREEN, bold=True)
                break
            except Exception as e:
                print_error(f"Неожиданная ошибка: {e}")
    
    def show_interactive_help(self):
        """Показывает help для интерактивного режима"""
        help_text = """
🆘 Команды интерактивного режима:

📝 Основные команды:
   • Просто введите текст для перевода
   • help          - Показать эту справку
   • settings      - Настройки
   • history       - История переводов
   • stats         - Статистика системы
   • quit/exit/q   - Выход

⚙️ Настройки можно изменить командой 'settings'
📚 История сохраняется автоматически
🔄 Язык определяется автоматически
"""
        colored_print(help_text, Colors.BLUE)
    
    def interactive_settings(self):
        """Интерактивные настройки"""
        colored_print("\n⚙️ Настройки TranslateCore CLI", Colors.HEADER, bold=True)
        print("=" * 40)
        
        # Показываем текущие настройки
        print("\n📋 Текущие настройки:")
        for key, value in self.settings.items():
            colored_print(f"  • {key}: {value}", Colors.CYAN)
        
        print("\n💡 Доступные для изменения:")
        print("1. default_target - целевой язык по умолчанию")
        print("2. default_service_config - конфигурация по умолчанию") 
        print("3. show_stats - показывать статистику")
        print("4. save_history - сохранять историю")
        
        choice = input("\nВведите номер настройки (или Enter для пропуска): ").strip()
        
        if choice == "1":
            languages = self.get_language_choices()
            print(f"Доступные языки: {', '.join(languages)}")
            new_lang = input("Новый целевой язык: ").strip().lower()
            if new_lang in languages:
                self.settings['default_target'] = new_lang
                self.save_settings()
                print_success(f"Целевой язык изменен на: {new_lang}")
        
        elif choice == "2":
            configs = self.get_config_choices()
            print(f"Доступные конфигурации: {', '.join(configs)}")
            new_config = input("Новая конфигурация: ").strip()
            if new_config in configs:
                self.settings['default_service_config'] = new_config
                self.save_settings()
                print_success(f"Конфигурация изменена на: {new_config}")
        
        elif choice == "3":
            new_stats = input("Показывать статистику? (y/n): ").strip().lower()
            self.settings['show_stats'] = new_stats in ['y', 'yes', 'да']
            self.save_settings()
            print_success(f"Показ статистики: {self.settings['show_stats']}")
        
        elif choice == "4":
            new_history = input("Сохранять историю? (y/n): ").strip().lower()
            self.settings['save_history'] = new_history in ['y', 'yes', 'да']
            self.save_settings()
            print_success(f"Сохранение истории: {self.settings['save_history']}")
    
    def show_system_stats(self):
        """Показывает статистику системы"""
        colored_print("\n📊 Статистика системы TranslateCore", Colors.HEADER, bold=True)
        print("=" * 50)
        
        # Проверяем доступные методы
        try:
            from .offline_translator import OfflineTranslator
            offline = OfflineTranslator('russian', 'english')
            methods = offline.available_methods
            colored_print(f"🔧 Доступные оффлайн методы: {', '.join(methods)}", Colors.GREEN)
        except ImportError:
            try:
                from offline_translator import OfflineTranslator
                offline = OfflineTranslator('russian', 'english')
                methods = offline.available_methods
                colored_print(f"🔧 Доступные оффлайн методы: {', '.join(methods)}", Colors.GREEN)
            except Exception as e:
                colored_print(f"❌ Оффлайн методы: {e}", Colors.FAIL)
        
        # Проверяем конфигурации
        try:
            loader = APIConfigLoader(self.config_file)
            configs = loader.list_available_configs()
            colored_print(f"⚙️ Доступные конфигурации: {len(configs)}", Colors.BLUE)
            for name, config in configs.items():
                try:
                    validation = loader.validate_config(name)
                    status = "✅" if validation['valid'] else "❌"
                    print(f"   • {status} {name}: {config['name']}")
                except:
                    print(f"   • ❌ {name}: {config['name']}")
        except Exception as e:
            colored_print(f"❌ Конфигурации: {e}", Colors.FAIL)
        
        # История
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                colored_print(f"📚 Переводов в истории: {len(history)}", Colors.CYAN)
            except:
                colored_print("📚 История недоступна", Colors.WARNING)
        else:
            colored_print("📚 История пуста", Colors.WARNING)
    
    def setup_wizard(self):
        """Мастер первоначальной настройки"""
        print_banner()
        colored_print("🎯 Мастер настройки TranslateCore CLI", Colors.HEADER, bold=True)
        print("Давайте настроим систему для максимального удобства!\n")
        
        # Шаг 1: Проверка зависимостей
        colored_print("Шаг 1: Проверка зависимостей", Colors.BLUE, bold=True)
        
        try:
            import argostranslate
            print_success("Argos Translate установлен")
        except ImportError:
            print_warning("Argos Translate не установлен")
            install = input("Хотите установить Argos Translate? (y/n): ").strip().lower()
            if install in ['y', 'yes', 'да']:
                os.system("pip install argostranslate")
                print_success("Установка Argos Translate завершена")
        
        # Шаг 2: Выбор конфигурации по умолчанию
        colored_print("\nШаг 2: Выбор конфигурации по умолчанию", Colors.BLUE, bold=True)
        configs = self.get_config_choices()
        
        print("Доступные конфигурации:")
        for i, config in enumerate(configs, 1):
            print(f"  {i}. {config}")
        
        try:
            choice = int(input("Выберите номер (по умолчанию 2 - development): ") or "2")
            if 1 <= choice <= len(configs):
                self.settings['default_service_config'] = configs[choice - 1]
                print_success(f"Выбрана конфигурация: {configs[choice - 1]}")
        except:
            print_info("Используется конфигурация по умолчанию: development")
        
        # Шаг 3: Настройки интерфейса
        colored_print("\nШаг 3: Настройки интерфейса", Colors.BLUE, bold=True)
        
        stats_choice = input("Показывать статистику после перевода? (y/n, по умолчанию y): ").strip().lower()
        self.settings['show_stats'] = stats_choice != 'n'
        
        history_choice = input("Сохранять историю переводов? (y/n, по умолчанию y): ").strip().lower() 
        self.settings['save_history'] = history_choice != 'n'
        
        # Сохраняем настройки
        self.save_settings()
        
        colored_print("\n🎉 Настройка завершена!", Colors.GREEN, bold=True)
        print_info("Теперь вы можете использовать 'translate-cli' или 'translate-cli -i' для интерактивного режима")

def create_argument_parser(cli: TranslateCLI) -> argparse.ArgumentParser:
    """Создает парсер аргументов командной строки"""
    
    parser = argparse.ArgumentParser(
        prog='translate-cli',
        description='🌍 TranslateCore CLI - Мощная утилита для перевода текстов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  translate-cli "Привет мир!"                    # Быстрый перевод
  translate-cli -s russian -t english "Текст"   # С указанием языков
  translate-cli -i                               # Интерактивный режим
  translate-cli -c offline_only "Текст"         # Только оффлайн
  translate-cli --history                        # Показать историю
  translate-cli --setup                          # Мастер настройки
  
Конфигурации:
  offline_only      - Полностью автономный оффлайн
  development       - Оффлайн + бесплатные онлайн (рекомендуется)
  production_basic  - Оффлайн + премиум сервисы
        """
    )
    
    # Основные аргументы
    parser.add_argument('text', nargs='?', 
                       help='Текст для перевода')
    
    parser.add_argument('-s', '--source', 
                       choices=cli.get_language_choices(),
                       default='auto',
                       help='Исходный язык (по умолчанию: автоопределение)')
    
    parser.add_argument('-t', '--target',
                       choices=cli.get_language_choices(),
                       help='Целевой язык (по умолчанию: из настроек)')
    
    parser.add_argument('-c', '--config',
                       choices=cli.get_config_choices(),
                       help='Конфигурация сервисов (по умолчанию: из настроек)')
    
    parser.add_argument('-f', '--file',
                       type=str,
                       help='Файл с текстом для перевода')
    
    # Режимы работы
    parser.add_argument('-i', '--interactive',
                       action='store_true',
                       help='Интерактивный режим')
    
    parser.add_argument('--setup',
                       action='store_true', 
                       help='Мастер первоначальной настройки')
    
    # Информационные команды
    parser.add_argument('--history',
                       action='store_true',
                       help='Показать историю переводов')
    
    parser.add_argument('--stats',
                       action='store_true',
                       help='Показать статистику системы')
    
    parser.add_argument('--configs',
                       action='store_true',
                       help='Показать доступные конфигурации')
    
    parser.add_argument('--languages',
                       action='store_true',
                       help='Показать поддерживаемые языки')
    
    # Утилиты
    parser.add_argument('--install-deps',
                       action='store_true',
                       help='Установить зависимости')
    
    parser.add_argument('--clear-history',
                       action='store_true',
                       help='Очистить историю переводов')
    
    parser.add_argument('--export-history',
                       type=str,
                       metavar='FILE',
                       help='Экспортировать историю в файл')
    
    # Настройки вывода
    parser.add_argument('--no-colors',
                       action='store_true',
                       help='Отключить цветной вывод')
    
    parser.add_argument('--quiet', '-q',
                       action='store_true',
                       help='Краткий вывод (только результат)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Подробный вывод')
    
    parser.add_argument('--code-mode',
                       action='store_true',
                       help='Code-aware translation (preserves syntax)')
    
    parser.add_argument('--translate-strings',
                       action='store_true',
                       help='Also translate string literals in code mode')
    
    return parser

def main():
    """Основная функция CLI"""
    
    cli = TranslateCLI()
    parser = create_argument_parser(cli)
    args = parser.parse_args()
    
    # Отключаем цвета если нужно
    if args.no_colors:
        Colors.HEADER = Colors.BLUE = Colors.CYAN = Colors.GREEN = Colors.WARNING = Colors.FAIL = Colors.ENDC = Colors.BOLD = Colors.UNDERLINE = ''
    
    try:
        # Обработка специальных команд
        if args.setup:
            cli.setup_wizard()
            return
        
        if args.interactive:
            cli.interactive_mode()
            return
        
        if args.history:
            cli.show_history()
            return
        
        if args.stats:
            cli.show_system_stats()
            return
        
        if args.configs:
            try:
                loader = APIConfigLoader(cli.config_file)
                configs = loader.list_available_configs()
                colored_print("\n⚙️ Доступные конфигурации:", Colors.HEADER, bold=True)
                for name, config in configs.items():
                    try:
                        validation = loader.validate_config(name)
                        status = "✅" if validation['valid'] else "❌"
                        print(f"  {status} {name}: {config['name']}")
                        print(f"      {config['description']}")
                        
                        if not validation['valid'] and validation['errors']:
                            for error in validation['errors'][:1]:  # Показываем только первую ошибку
                                print(f"      ❌ {error}")
                        
                        if validation['warnings']:
                            for warning in validation['warnings'][:1]:  # Показываем только первое предупреждение
                                print(f"      ⚠️ {warning}")
                    except Exception as e:
                        print(f"  ❌ {name}: Ошибка валидации - {e}")
            except Exception as e:
                print_error(f"Ошибка загрузки конфигураций: {e}")
            return
        
        if args.languages:
            languages = cli.get_language_choices()
            colored_print("\n🌐 Поддерживаемые языки:", Colors.HEADER, bold=True)
            for lang in languages:
                print(f"  • {lang}")
            return
        
        if args.install_deps:
            os.system("pip install argostranslate")
            print_success("Зависимости установлены")
            return
        
        if args.clear_history:
            if cli.history_file.exists():
                cli.history_file.unlink()
                print_success("История очищена")
            else:
                print_info("История уже пуста")
            return
        
        if args.export_history:
            if cli.history_file.exists():
                import shutil
                shutil.copy(cli.history_file, args.export_history)
                print_success(f"История экспортирована в: {args.export_history}")
            else:
                print_error("История пуста, нечего экспортировать")
            return
        
        # Основная логика перевода
        text = None
        
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                print_info(f"Загружен файл: {args.file}")
            except Exception as e:
                print_error(f"Ошибка чтения файла: {e}")
                return
        elif args.text:
            text = args.text
        else:
            # Если нет аргументов, запускаем интерактивный режим
            cli.interactive_mode()
            return
        
        if not text:
            print_error("Не указан текст для перевода")
            return
        
        # Выполняем перевод
        if not args.quiet:
            print_banner()
        
        target_lang = args.target or cli.settings['default_target']
        service_config = args.config or cli.settings['default_service_config']
        
        result = cli.smart_translate(
            text=text,
            source_lang=args.source,
            target_lang=target_lang,
            service_config=service_config
        )
        
        if result['success']:
            if args.quiet:
                # Только результат
                print(result['translated'])
            else:
                # Полный вывод
                print("\n" + "═" * 60)
                colored_print(f"📝 Оригинал:  {result['original']}", Colors.CYAN)
                colored_print(f"🔄 Перевод:   {result['translated']}", Colors.GREEN, bold=True)
                colored_print(f"🌐 Маршрут:   {result['source_lang']} → {result['target_lang']}", Colors.WARNING)
                colored_print(f"🔧 Сервис:    {result['service']}", Colors.BLUE)
                colored_print(f"⏱️ Время:     {result['processing_time']:.2f}с", Colors.WARNING)
                
                if result['stats'] and cli.settings['show_stats'] and args.verbose:
                    stats = result['stats']
                    colored_print(f"📊 Статистика: {stats['total_requests']} запросов", Colors.BLUE)
                
                print("═" * 60)
        else:
            print_error(f"Ошибка перевода: {result['error']}")
            if args.verbose:
                print_info("Попробуйте другую конфигурацию или установите зависимости")
    
    except KeyboardInterrupt:
        colored_print("\n👋 Операция прервана пользователем", Colors.WARNING)
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
