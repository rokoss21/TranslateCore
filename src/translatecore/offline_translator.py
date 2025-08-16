#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полностью автономный оффлайн переводчик с LibreTranslate
Работает без интернета, без внешних API, полная приватность
"""

import json
import os
import time
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import requests
import threading
import signal

# Попытаемся импортировать argostranslate для прямого использования
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    print("⚠️ argostranslate не установлен, будем использовать LibreTranslate сервер")
    ARGOS_AVAILABLE = False


@dataclass
class OfflineTranslationResult:
    """Результат оффлайн перевода"""
    original: str
    translated: str
    source_lang: str
    target_lang: str
    method: str  # 'argos_direct', 'libretranslate_local', 'libretranslate_docker'
    confidence: float = 1.0
    processing_time: float = 0.0


class OfflineTranslator:
    """Полностью автономный переводчик"""
    
    LANGUAGE_CODES = {
        'russian': {'code': 'ru', 'name': 'Russian'},
        'english': {'code': 'en', 'name': 'English'},
        'chinese': {'code': 'zh', 'name': 'Chinese'},
        'japanese': {'code': 'ja', 'name': 'Japanese'},
        'korean': {'code': 'ko', 'name': 'Korean'},
        'german': {'code': 'de', 'name': 'German'},
        'french': {'code': 'fr', 'name': 'French'},
        'spanish': {'code': 'es', 'name': 'Spanish'},
        'italian': {'code': 'it', 'name': 'Italian'},
        'portuguese': {'code': 'pt', 'name': 'Portuguese'},
        'arabic': {'code': 'ar', 'name': 'Arabic'},
        'dutch': {'code': 'nl', 'name': 'Dutch'},
        'czech': {'code': 'cs', 'name': 'Czech'},
        'ukrainian': {'code': 'uk', 'name': 'Ukrainian'},
        'bulgarian': {'code': 'bg', 'name': 'Bulgarian'},
        'hungarian': {'code': 'hu', 'name': 'Hungarian'},
        'catalan': {'code': 'ca', 'name': 'Catalan'}
    }
    
    def __init__(self, source_lang: str, target_lang: str, 
                 cache_file: Optional[str] = None,
                 libretranslate_url: Optional[str] = None,
                 prefer_method: str = 'auto'):
        """
        Инициализация оффлайн переводчика
        
        Args:
            source_lang: Исходный язык
            target_lang: Целевой язык
            cache_file: Файл кеша переводов
            libretranslate_url: URL локального LibreTranslate сервера
            prefer_method: Предпочтительный метод ('auto', 'argos', 'libretranslate', 'docker')
        """
        self.source_lang = source_lang.lower()
        self.target_lang = target_lang.lower()
        self.libretranslate_url = libretranslate_url or "http://localhost:5000"
        self.prefer_method = prefer_method
        
        # Статистика
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'argos_translations': 0,
            'libretranslate_translations': 0,
            'docker_translations': 0,
            'errors': []
        }
        
        # Кеш переводов
        self.cache_file = cache_file or f"offline_cache_{self.source_lang}_{self.target_lang}.json"
        self.cache = self._load_cache()
        
        # Проверяем доступные методы
        self.available_methods = self._check_available_methods()
        
        if not self.available_methods:
            raise RuntimeError("❌ Нет доступных методов оффлайн перевода!")
        
        print(f"🔧 Доступные методы: {', '.join(self.available_methods)}")
        
        # Рекомендация пользователю
        if 'argos' in self.available_methods:
            print("💡 Рекомендация: Argos Translate - лучший выбор для персонального использования")
        elif 'libretranslate' in self.available_methods or 'docker' in self.available_methods:
            print("💡 Рекомендация: Установите Argos Translate для лучшей производительности: pip install argostranslate")
        
        # Инициализируем Argos если доступен
        if 'argos' in self.available_methods:
            self._init_argos()
    
    def _load_cache(self) -> Dict[str, str]:
        """Загружает кеш переводов"""
        if Path(self.cache_file).exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки кеша: {e}")
        return {}
    
    def _save_cache(self):
        """Сохраняет кеш переводов"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения кеша: {e}")
    
    def _check_available_methods(self) -> List[str]:
        """Проверяет доступные методы перевода"""
        methods = []
        
        # Проверяем прямой Argos
        if ARGOS_AVAILABLE:
            methods.append('argos')
            print("✅ Argos Translate доступен напрямую")
        
        # Проверяем локальный LibreTranslate сервер
        try:
            response = requests.get(f"{self.libretranslate_url}/languages", timeout=2)
            if response.status_code == 200:
                methods.append('libretranslate')
                print(f"✅ LibreTranslate сервер доступен: {self.libretranslate_url}")
        except:
            pass
        
        # Проверяем Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                methods.append('docker')
                print("✅ Docker доступен для запуска LibreTranslate")
        except:
            pass
        
        return methods
    
    def _ensure_language_package(self, from_code: str, to_code: str) -> bool:
        """Автоматически загружает языковой пакет если нужен"""
        try:
            # Обновляем индекс пакетов
            argostranslate.package.update_package_index()
            
            # Проверяем, установлен ли пакет
            installed_packages = argostranslate.package.get_installed_packages()
            is_installed = any(
                p.from_code == from_code and p.to_code == to_code 
                for p in installed_packages
            )
            
            if is_installed:
                return True
                
            # Ищем пакет для загрузки
            available_packages = argostranslate.package.get_available_packages()
            package = next(
                (pkg for pkg in available_packages 
                 if pkg.from_code == from_code and pkg.to_code == to_code), 
                None
            )
            
            if package:
                print(f"📦 Автоматически скачиваем языковой пакет: {from_code}→{to_code}...")
                print("   (это происходит только при первом использовании)")
                argostranslate.package.install_from_path(package.download())
                print(f"✅ Языковой пакет {from_code}→{to_code} успешно установлен")
                return True
            else:
                print(f"⚠️ Языковой пакет {from_code}→{to_code} недоступен в Argos")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки пакета {from_code}→{to_code}: {e}")
            return False
    
    def _init_argos(self):
        """Инициализирует Argos Translate с автоматической загрузкой пакетов"""
        if not ARGOS_AVAILABLE:
            return
        
        try:
            source_code = self.LANGUAGE_CODES[self.source_lang]['code']
            target_code = self.LANGUAGE_CODES[self.target_lang]['code']
            
            # Проверяем и загружаем пакет автоматически
            if self._ensure_language_package(source_code, target_code):
                print(f"✅ Argos Translate готов для {self.source_lang} → {self.target_lang}")
            else:
                print(f"❌ Не удалось подготовить пакет {self.source_lang} → {self.target_lang}")
                self.available_methods = [m for m in self.available_methods if m != 'argos']
                
        except Exception as e:
            print(f"❌ Ошибка инициализации Argos: {e}")
            self.available_methods = [m for m in self.available_methods if m != 'argos']
    
    def translate_with_argos(self, text: str) -> OfflineTranslationResult:
        """Переводит текст через Argos Translate напрямую"""
        if not ARGOS_AVAILABLE or 'argos' not in self.available_methods:
            raise RuntimeError("Argos Translate недоступен")
        
        start_time = time.time()
        
        try:
            source_code = self.LANGUAGE_CODES[self.source_lang]['code']
            target_code = self.LANGUAGE_CODES[self.target_lang]['code']
            
            translated = argostranslate.translate.translate(text, source_code, target_code)
            processing_time = time.time() - start_time
            
            self.stats['argos_translations'] += 1
            
            return OfflineTranslationResult(
                original=text,
                translated=translated,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                method='argos_direct',
                processing_time=processing_time
            )
            
        except Exception as e:
            raise RuntimeError(f"Ошибка Argos перевода: {e}")
    
    def translate_with_libretranslate(self, text: str) -> OfflineTranslationResult:
        """Переводит текст через локальный LibreTranslate сервер"""
        if 'libretranslate' not in self.available_methods:
            raise RuntimeError("LibreTranslate сервер недоступен")
        
        start_time = time.time()
        
        try:
            source_code = self.LANGUAGE_CODES[self.source_lang]['code']
            target_code = self.LANGUAGE_CODES[self.target_lang]['code']
            
            response = requests.post(
                f"{self.libretranslate_url}/translate",
                json={
                    'q': text,
                    'source': source_code,
                    'target': target_code
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result['translatedText']
                processing_time = time.time() - start_time
                
                self.stats['libretranslate_translations'] += 1
                
                return OfflineTranslationResult(
                    original=text,
                    translated=translated,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                    method='libretranslate_local',
                    processing_time=processing_time
                )
            else:
                raise RuntimeError(f"LibreTranslate ошибка: {response.status_code}")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка LibreTranslate: {e}")
    
    def start_docker_libretranslate(self) -> bool:
        """Запускает LibreTranslate в Docker контейнере"""
        if 'docker' not in self.available_methods:
            return False
        
        try:
            print("🐳 Запускаем LibreTranslate в Docker...")
            
            # Проверяем, не запущен ли уже контейнер
            check_cmd = ['docker', 'ps', '--filter', 'name=libretranslate-offline', '--format', '{{.Names}}']
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if 'libretranslate-offline' in result.stdout:
                print("✅ LibreTranslate контейнер уже запущен")
                return True
            
            # Запускаем контейнер
            docker_cmd = [
                'docker', 'run', '-d',
                '--name', 'libretranslate-offline',
                '-p', '5000:5000',
                'libretranslate/libretranslate:latest'
            ]
            
            subprocess.run(docker_cmd, check=True, timeout=60)
            
            # Ждем запуска сервиса
            print("⏳ Ждем запуска сервиса...")
            for i in range(30):  # Ждем до 30 секунд
                try:
                    response = requests.get("http://localhost:5000/languages", timeout=2)
                    if response.status_code == 200:
                        print("✅ LibreTranslate запущен в Docker")
                        self.libretranslate_url = "http://localhost:5000"
                        if 'libretranslate' not in self.available_methods:
                            self.available_methods.append('libretranslate')
                        return True
                except:
                    pass
                time.sleep(1)
            
            print("❌ Не удалось дождаться запуска LibreTranslate")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка запуска Docker: {e}")
            return False
    
    def stop_docker_libretranslate(self):
        """Останавливает Docker контейнер LibreTranslate"""
        try:
            subprocess.run(['docker', 'stop', 'libretranslate-offline'], 
                         capture_output=True, timeout=10)
            subprocess.run(['docker', 'rm', 'libretranslate-offline'], 
                         capture_output=True, timeout=10)
            print("🐳 Docker контейнер остановлен")
        except:
            pass
    
    def translate(self, text: str, use_cache: bool = True) -> OfflineTranslationResult:
        """
        Главный метод перевода
        
        Args:
            text: Текст для перевода
            use_cache: Использовать кеш
            
        Returns:
            OfflineTranslationResult: Результат перевода
        """
        self.stats['total_requests'] += 1
        
        # Проверяем кеш
        cache_key = f"{text}|{self.source_lang}|{self.target_lang}"
        if use_cache and cache_key in self.cache:
            self.stats['cache_hits'] += 1
            cached = self.cache[cache_key]
            return OfflineTranslationResult(
                original=text,
                translated=cached,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                method='cache',
                processing_time=0.0
            )
        
        # Выбираем метод перевода
        method_order = self._get_method_order()
        
        for method in method_order:
            try:
                if method == 'argos':
                    result = self.translate_with_argos(text)
                elif method == 'libretranslate':
                    result = self.translate_with_libretranslate(text)
                elif method == 'docker':
                    if self.start_docker_libretranslate():
                        result = self.translate_with_libretranslate(text)
                        result.method = 'libretranslate_docker'
                        self.stats['docker_translations'] += 1
                    else:
                        continue
                else:
                    continue
                
                # Сохраняем в кеш
                if use_cache:
                    self.cache[cache_key] = result.translated
                    self._save_cache()
                
                print(f"✅ Переведено через {result.method} за {result.processing_time:.2f}с")
                return result
                
            except Exception as e:
                error_msg = f"{method}: {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                continue
        
        # Если все методы не сработали
        raise RuntimeError("❌ Все методы оффлайн перевода недоступны")
    
    def _get_method_order(self) -> List[str]:
        """Определяет порядок использования методов"""
        if self.prefer_method == 'auto':
            # Автоматический порядок: Argos → LibreTranslate → Docker
            order = ['argos', 'libretranslate', 'docker']
        elif self.prefer_method in self.available_methods:
            # Предпочтительный метод первым
            order = [self.prefer_method] + [m for m in self.available_methods if m != self.prefer_method]
        else:
            order = self.available_methods
        
        return [m for m in order if m in self.available_methods]
    
    def translate_batch(self, texts: List[str], show_progress: bool = True) -> List[OfflineTranslationResult]:
        """Переводит список текстов"""
        results = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            if show_progress and i % 5 == 0:
                progress = (i / total) * 100
                print(f"📊 Прогресс: {i}/{total} ({progress:.1f}%)")
            
            try:
                result = self.translate(text)
                results.append(result)
            except Exception as e:
                print(f"❌ Ошибка перевода '{text}': {e}")
                # Возвращаем оригинальный текст при ошибке
                results.append(OfflineTranslationResult(
                    original=text,
                    translated=text,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                    method='error'
                ))
        
        if show_progress:
            print(f"📊 Прогресс: {total}/{total} (100.0%)")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования"""
        return {
            'total_requests': self.stats['total_requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': (self.stats['cache_hits'] / max(1, self.stats['total_requests'])) * 100,
            'cache_size': len(self.cache),
            'methods_used': {
                'argos': self.stats['argos_translations'],
                'libretranslate': self.stats['libretranslate_translations'], 
                'docker': self.stats['docker_translations']
            },
            'available_methods': self.available_methods,
            'errors_count': len(self.stats['errors']),
            'errors': self.stats['errors'][-3:] if self.stats['errors'] else []
        }
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Возвращает поддерживаемые языки"""
        return self.LANGUAGE_CODES
    
    def install_language_package(self, source_lang: str, target_lang: str) -> bool:
        """Устанавливает языковой пакет для Argos"""
        if not ARGOS_AVAILABLE:
            print("❌ Argos Translate не установлен")
            return False
        
        try:
            source_code = self.LANGUAGE_CODES[source_lang]['code']
            target_code = self.LANGUAGE_CODES[target_lang]['code']
            
            # Обновляем индекс
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # Ищем пакет
            for package in available_packages:
                if (package.from_code == source_code and 
                    package.to_code == target_code):
                    print(f"📦 Скачиваем пакет {source_lang}→{target_lang}...")
                    argostranslate.package.install_from_path(package.download())
                    print("✅ Пакет установлен")
                    return True
            
            print(f"❌ Пакет {source_lang}→{target_lang} не найден")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка установки пакета: {e}")
            return False
    
    def __del__(self):
        """Очистка при удалении объекта"""
        if hasattr(self, 'prefer_method') and self.prefer_method == 'docker':
            self.stop_docker_libretranslate()


def install_offline_requirements():
    """Устанавливает зависимости для оффлайн перевода"""
    print("📦 Установка зависимостей для оффлайн перевода:")
    print()
    
    requirements = [
        {
            'name': 'Argos Translate (прямой доступ)',
            'command': 'pip install argostranslate',
            'description': 'Самый быстрый метод, прямая интеграция'
        },
        {
            'name': 'LibreTranslate сервер',
            'command': 'pip install libretranslate',
            'description': 'Локальный HTTP сервер'
        },
        {
            'name': 'Docker (для контейнера)',
            'command': 'docker pull libretranslate/libretranslate:latest',
            'description': 'Изолированный контейнер'
        }
    ]
    
    for req in requirements:
        print(f"\n🔧 {req['name']}")
        print(f"   Команда: {req['command']}")
        print(f"   Описание: {req['description']}")
    
    print(f"\n💡 Рекомендации:")
    print(f"   • Начните с установки argostranslate")
    print(f"   • Docker - самый простой способ запуска")
    print(f"   • LibreTranslate сервер - для продвинутого использования")


def main():
    """Основная функция для тестирования оффлайн переводчика"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Автономный оффлайн переводчик")
    
    parser.add_argument('--source', '-s', default='russian',
                       choices=list(OfflineTranslator.LANGUAGE_CODES.keys()),
                       help='Исходный язык')
    
    parser.add_argument('--target', '-t', default='english',
                       choices=list(OfflineTranslator.LANGUAGE_CODES.keys()),
                       help='Целевой язык')
    
    parser.add_argument('--text', 
                       help='Текст для перевода')
    
    parser.add_argument('--file',
                       help='Файл с текстом для перевода')
    
    parser.add_argument('--method', choices=['auto', 'argos', 'libretranslate', 'docker'],
                       default='auto', help='Предпочтительный метод')
    
    parser.add_argument('--install-deps', action='store_true',
                       help='Показать команды установки зависимостей')
    
    parser.add_argument('--install-package', nargs=2, metavar=('SOURCE', 'TARGET'),
                       help='Установить языковой пакет для Argos')
    
    parser.add_argument('--list-languages', action='store_true',
                       help='Показать поддерживаемые языки')
    
    parser.add_argument('--start-docker', action='store_true',
                       help='Запустить LibreTranslate в Docker')
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_offline_requirements()
        return
    
    if args.list_languages:
        print("🌐 Поддерживаемые языки:")
        for key, value in OfflineTranslator.LANGUAGE_CODES.items():
            print(f"  {key}: {value['name']} ({value['code']})")
        return
    
    if args.install_package:
        translator = OfflineTranslator('russian', 'english')  # Временный
        success = translator.install_language_package(args.install_package[0], args.install_package[1])
        return
    
    if args.start_docker:
        translator = OfflineTranslator('russian', 'english', prefer_method='docker')
        if translator.start_docker_libretranslate():
            print("✅ LibreTranslate запущен в Docker на http://localhost:5000")
            
            # Регистрируем обработчик для остановки при Ctrl+C
            def signal_handler(sig, frame):
                print("\n🛑 Останавливаем Docker контейнер...")
                translator.stop_docker_libretranslate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            print("Нажмите Ctrl+C для остановки")
            while True:
                time.sleep(1)
        return
    
    if not args.text and not args.file:
        parser.print_help()
        return
    
    try:
        # Создаем переводчик
        translator = OfflineTranslator(
            source_lang=args.source,
            target_lang=args.target,
            prefer_method=args.method
        )
        
        # Получаем текст для перевода
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        else:
            text = args.text
        
        print(f"🌐 Оффлайн перевод: {args.source} → {args.target}")
        print(f"📝 Исходный текст: {text}")
        print("-" * 50)
        
        # Переводим
        result = translator.translate(text)
        
        print(f"✅ Переведенный текст: {result.translated}")
        print(f"🔧 Метод: {result.method}")
        print(f"⏱️ Время: {result.processing_time:.2f}с")
        
        # Статистика
        stats = translator.get_stats()
        print(f"\n📊 Статистика:")
        print(f"  Всего запросов: {stats['total_requests']}")
        print(f"  Попаданий в кеш: {stats['cache_hits']} ({stats['cache_hit_rate']:.1f}%)")
        print(f"  Методы: {stats['methods_used']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Попробуйте:")
        print("  python3 offline_translator.py --install-deps")
        print("  python3 offline_translator.py --start-docker")


if __name__ == "__main__":
    main()
