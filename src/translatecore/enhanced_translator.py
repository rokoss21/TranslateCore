#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный переводчик с поддержкой deep-translator
Поддерживает множество сервисов перевода и расширенную функциональность
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse
from dataclasses import dataclass

# Импортируем загрузчик конфигурации
try:
    from .config_loader import APIConfigLoader, ConfigurationError
    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    try:
        from config_loader import APIConfigLoader, ConfigurationError
        CONFIG_LOADER_AVAILABLE = True
    except ImportError:
        print("⚠️ config_loader не найден, используется базовая конфигурация")
        CONFIG_LOADER_AVAILABLE = False

# Импортируем оффлайн переводчик
try:
    from .offline_translator import OfflineTranslator, OfflineTranslationResult
    OFFLINE_TRANSLATOR_AVAILABLE = True
except ImportError:
    try:
        from offline_translator import OfflineTranslator, OfflineTranslationResult
        OFFLINE_TRANSLATOR_AVAILABLE = True
    except ImportError:
        print("⚠️ offline_translator не найден, оффлайн перевод недоступен")
        OFFLINE_TRANSLATOR_AVAILABLE = False

# Импортируем deep-translator
try:
    from deep_translator import (
        GoogleTranslator,
        MyMemoryTranslator,
        LibreTranslator,
        PonsTranslator,
        LingueeTranslator,
        MicrosoftTranslator,
        YandexTranslator,
        DeeplTranslator,
        ChatGptTranslator,
        PapagoTranslator
    )
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Ошибка импорта deep-translator: {e}")
    print("Установите библиотеку: pip install deep-translator")
    DEEP_TRANSLATOR_AVAILABLE = False


@dataclass
class TranslationResult:
    """Результат перевода"""
    original: str
    translated: str
    source_lang: str
    target_lang: str
    service: str
    confidence: float = 0.0
    alternatives: List[str] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class EnhancedTranslator:
    """Улучшенный переводчик с множественными сервисами"""
    
    # Маппинг языков для разных сервисов
    LANGUAGE_MAPPINGS = {
        'russian': {'google': 'ru', 'libre': 'ru', 'mymemory': 'ru-RU'},
        'english': {'google': 'en', 'libre': 'en', 'mymemory': 'en-US'},
        'chinese': {'google': 'zh-cn', 'libre': 'zh', 'mymemory': 'zh'},
        'japanese': {'google': 'ja', 'libre': 'ja', 'mymemory': 'ja'},
        'korean': {'google': 'ko', 'libre': 'ko', 'mymemory': 'ko'},
        'german': {'google': 'de', 'libre': 'de', 'mymemory': 'de'},
        'french': {'google': 'fr', 'libre': 'fr', 'mymemory': 'fr'},
        'spanish': {'google': 'es', 'libre': 'es', 'mymemory': 'es'},
        'italian': {'google': 'it', 'libre': 'it', 'mymemory': 'it'},
        'portuguese': {'google': 'pt', 'libre': 'pt', 'mymemory': 'pt'},
        'arabic': {'google': 'ar', 'libre': 'ar', 'mymemory': 'ar'},
        'hebrew': {'google': 'he', 'libre': 'he', 'mymemory': 'he'},
        'thai': {'google': 'th', 'libre': 'th', 'mymemory': 'th'},
        'greek': {'google': 'el', 'libre': 'el', 'mymemory': 'el'}
    }
    
    # Доступные сервисы и их приоритеты
    AVAILABLE_SERVICES = {
        'offline': {'class': None, 'priority': 0, 'free': True},  # Оффлайн переводчик - высший приоритет
        'google': {'class': GoogleTranslator, 'priority': 1, 'free': True},
        'libre': {'class': LibreTranslator, 'priority': 2, 'free': True},
        'mymemory': {'class': MyMemoryTranslator, 'priority': 3, 'free': True},
        'pons': {'class': PonsTranslator, 'priority': 4, 'free': True},
        'linguee': {'class': LingueeTranslator, 'priority': 5, 'free': True},
        'microsoft': {'class': MicrosoftTranslator, 'priority': 6, 'free': False},
        'yandex': {'class': YandexTranslator, 'priority': 7, 'free': False},
        'deepl': {'class': DeeplTranslator, 'priority': 8, 'free': False},
        'chatgpt': {'class': ChatGptTranslator, 'priority': 9, 'free': False},
        'papago': {'class': PapagoTranslator, 'priority': 10, 'free': False}
    }
    
    def __init__(self, source_lang: str, target_lang: str, 
                 preferred_services: List[str] = None,
                 cache_file: Optional[str] = None,
                 api_keys: Dict[str, str] = None,
                 config_file: Optional[str] = None,
                 service_config_name: Optional[str] = None):
        """
        Инициализация переводчика
        
        Args:
            source_lang: Исходный язык
            target_lang: Целевой язык
            preferred_services: Предпочтительные сервисы в порядке приоритета
            cache_file: Файл кеша переводов
            api_keys: API ключи для платных сервисов
            config_file: Путь к файлу конфигурации API ключей
            service_config_name: Название конфигурации сервиса из файла
        """
        if not DEEP_TRANSLATOR_AVAILABLE:
            raise ImportError("deep-translator не установлен")
        
        self.source_lang = source_lang.lower()
        self.target_lang = target_lang.lower()
        
        # Загружаем API ключи из конфигурационного файла, если указан
        if config_file and CONFIG_LOADER_AVAILABLE:
            try:
                config_loader = APIConfigLoader(config_file)
                if service_config_name:
                    # Загружаем конфигурацию сервисов и API ключи
                    self.preferred_services = config_loader.get_services_for_config(service_config_name)
                    loaded_api_keys = config_loader.get_api_keys(service_config_name)
                    print(f"📋 Загружена конфигурация '{service_config_name}'")
                    print(f"🔧 Сервисы: {', '.join(self.preferred_services)}")
                else:
                    loaded_api_keys = config_loader.get_api_keys()
                
                # Объединяем загруженные ключи с переданными
                self.api_keys = {**loaded_api_keys, **(api_keys or {})}
                
            except ConfigurationError as e:
                print(f"❌ Ошибка загрузки конфигурации: {e}")
                self.api_keys = api_keys or {}
        else:
            self.api_keys = api_keys or {}
        
        # Устанавливаем предпочтительные сервисы
        if preferred_services:
            self.preferred_services = [s.lower() for s in preferred_services]
        else:
            # По умолчанию используем оффлайн + бесплатные сервисы
            if OFFLINE_TRANSLATOR_AVAILABLE:
                self.preferred_services = ['offline', 'google', 'libre', 'mymemory', 'pons']
            else:
                self.preferred_services = ['google', 'libre', 'mymemory', 'pons']
        
        # Статистика (инициализируем раньше)
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'service_usage': {},
            'errors': []
        }
        
        # Инициализируем кеш
        self.cache_file = cache_file or f"translation_cache_{self.source_lang}_{self.target_lang}.json"
        self.cache = self._load_cache()
        
        # Инициализируем переводчики
        self.translators = {}
        self._init_translators()
    
    def _load_cache(self) -> Dict[str, TranslationResult]:
        """Загружает кеш переводов"""
        cache_path = Path(self.cache_file)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Конвертируем словари обратно в TranslationResult
                    cache = {}
                    for key, value in data.items():
                        if isinstance(value, dict) and 'original' in value:
                            cache[key] = TranslationResult(**value)
                        else:
                            # Старый формат кеша
                            cache[key] = TranslationResult(
                                original=key,
                                translated=value,
                                source_lang=self.source_lang,
                                target_lang=self.target_lang,
                                service='unknown'
                            )
                    return cache
            except Exception as e:
                print(f"Ошибка загрузки кеша: {e}")
        
        return {}
    
    def _save_cache(self):
        """Сохраняет кеш переводов"""
        try:
            # Конвертируем TranslationResult в словари для JSON
            cache_data = {}
            for key, result in self.cache.items():
                if isinstance(result, TranslationResult):
                    cache_data[key] = {
                        'original': result.original,
                        'translated': result.translated,
                        'source_lang': result.source_lang,
                        'target_lang': result.target_lang,
                        'service': result.service,
                        'confidence': result.confidence,
                        'alternatives': result.alternatives
                    }
                else:
                    cache_data[key] = result
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения кеша: {e}")
    
    def _get_lang_code(self, lang: str, service: str) -> str:
        """Получает код языка для конкретного сервиса"""
        if lang in self.LANGUAGE_MAPPINGS:
            mapping = self.LANGUAGE_MAPPINGS[lang]
            return mapping.get(service, mapping.get('google', lang))
        return lang
    
    def _init_translators(self):
        """Инициализирует доступные переводчики"""
        for service_name in self.preferred_services:
            if service_name not in self.AVAILABLE_SERVICES:
                print(f"⚠️ Неизвестный сервис: {service_name}")
                continue
            
            service_info = self.AVAILABLE_SERVICES[service_name]
            translator_class = service_info['class']
            
            try:
                # Получаем коды языков для этого сервиса
                source_code = self._get_lang_code(self.source_lang, service_name)
                target_code = self._get_lang_code(self.target_lang, service_name)
                
                # Инициализируем переводчик в зависимости от типа
                if service_name == 'google':
                    translator = translator_class(source=source_code, target=target_code)
                
                elif service_name == 'libre':
                    # LibreTranslator может требовать API ключ, попробуем бесплатный сервер
                    api_key = self.api_keys.get('libre')
                    base_url = self.api_keys.get('libre_url', 'https://libretranslate.de')
                    if api_key:
                        translator = translator_class(source=source_code, target=target_code, api_key=api_key, base_url=base_url)
                    else:
                        # Используем публичный сервер без ключа
                        translator = translator_class(source=source_code, target=target_code, base_url=base_url)
                
                elif service_name == 'mymemory':
                    translator = translator_class(source=source_code, target=target_code)
                
                elif service_name in ['pons', 'linguee']:
                    # Для словарных переводчиков используем полные названия языков
                    source_name = self.source_lang
                    target_name = self.target_lang
                    translator = translator_class(source=source_name, target=target_name)
                
                elif service_name == 'microsoft':
                    api_key = self.api_keys.get('microsoft')
                    if not api_key:
                        print(f"⚠️ Microsoft Translator требует API ключ")
                        continue
                    translator = translator_class(api_key=api_key, target=target_code)
                
                elif service_name == 'yandex':
                    api_key = self.api_keys.get('yandex')
                    if not api_key:
                        print(f"⚠️ Yandex Translator требует API ключ")
                        continue
                    translator = translator_class(api_key=api_key)
                
                elif service_name == 'deepl':
                    api_key = self.api_keys.get('deepl')
                    if not api_key:
                        print(f"⚠️ DeepL требует API ключ")
                        continue
                    translator = translator_class(api_key=api_key, source=source_code, target=target_code)
                
                elif service_name == 'chatgpt':
                    api_key = self.api_keys.get('openai') or os.getenv('OPENAI_API_KEY')
                    if not api_key:
                        print(f"⚠️ ChatGPT требует API ключ")
                        continue
                    translator = translator_class(api_key=api_key, target=target_code)
                
                elif service_name == 'papago':
                    client_id = self.api_keys.get('papago_client_id')
                    secret_key = self.api_keys.get('papago_secret_key')
                    if not client_id or not secret_key:
                        print(f"⚠️ Papago требует client_id и secret_key")
                        continue
                    translator = translator_class(client_id=client_id, secret_key=secret_key, 
                                                source=source_code, target=target_code)
                
                elif service_name == 'offline':
                    # Оффлайн переводчик
                    if OFFLINE_TRANSLATOR_AVAILABLE:
                        translator = OfflineTranslator(
                            source_lang=self.source_lang,
                            target_lang=self.target_lang,
                            cache_file=f"offline_cache_{self.source_lang}_{self.target_lang}.json"
                        )
                    else:
                        print(f"⚠️ Оффлайн переводчик недоступен")
                        continue
                
                else:
                    print(f"⚠️ Переводчик {service_name} не реализован")
                    continue
                
                self.translators[service_name] = translator
                print(f"✅ Инициализирован переводчик: {service_name}")
                
            except Exception as e:
                print(f"❌ Ошибка инициализации {service_name}: {e}")
                self.stats['errors'].append(f"{service_name}: {str(e)}")
    
    def translate(self, text: str, use_cache: bool = True) -> TranslationResult:
        """
        Переводит текст используя доступные сервисы
        
        Args:
            text: Текст для перевода
            use_cache: Использовать кеш
            
        Returns:
            TranslationResult: Результат перевода
        """
        self.stats['total_requests'] += 1
        
        # Проверяем кеш
        cache_key = f"{text}|{self.source_lang}|{self.target_lang}"
        if use_cache and cache_key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        # Пробуем переводчики по порядку приоритета
        for service_name in self.preferred_services:
            # Специальная обработка для оффлайн переводчика
            if service_name == 'offline' and OFFLINE_TRANSLATOR_AVAILABLE:
                try:
                    print(f"🔒 Переводим оффлайн...")
                    
                    offline_translator = OfflineTranslator(
                        source_lang=self.source_lang,
                        target_lang=self.target_lang,
                        cache_file=f"offline_cache_{self.source_lang}_{self.target_lang}.json"
                    )
                    
                    offline_result = offline_translator.translate(text, use_cache)
                    
                    # Конвертируем результат в наш формат
                    result = TranslationResult(
                        original=offline_result.original,
                        translated=offline_result.translated,
                        source_lang=offline_result.source_lang,
                        target_lang=offline_result.target_lang,
                        service=f"offline_{offline_result.method}",
                        confidence=offline_result.confidence
                    )
                    
                    # Сохраняем в кеш
                    if use_cache:
                        self.cache[cache_key] = result
                        self._save_cache()
                    
                    # Обновляем статистику
                    service_key = f"offline_{offline_result.method}"
                    if service_key not in self.stats['service_usage']:
                        self.stats['service_usage'][service_key] = 0
                    self.stats['service_usage'][service_key] += 1
                    
                    print(f"✅ Переведено оффлайн через {offline_result.method} за {offline_result.processing_time:.2f}с")
                    return result
                    
                except Exception as e:
                    error_msg = f"offline: {str(e)}"
                    print(f"❌ {error_msg}")
                    self.stats['errors'].append(error_msg)
                    continue
            
            # Обычные онлайн переводчики
            if service_name not in self.translators:
                continue
            
            translator = self.translators[service_name]
            
            try:
                print(f"🌐 Переводим через {service_name}...")
                
                # Выполняем перевод
                if service_name in ['pons', 'linguee']:
                    # Словарные переводчики возвращают список результатов
                    translated = translator.translate(text, return_all=False)
                else:
                    translated = translator.translate(text)
                
                if not translated or translated == text:
                    print(f"⚠️ {service_name}: Пустой или неизмененный результат")
                    continue
                
                # Создаем результат
                result = TranslationResult(
                    original=text,
                    translated=translated,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                    service=service_name,
                    confidence=1.0
                )
                
                # Сохраняем в кеш
                if use_cache:
                    self.cache[cache_key] = result
                    self._save_cache()
                
                # Обновляем статистику
                if service_name not in self.stats['service_usage']:
                    self.stats['service_usage'][service_name] = 0
                self.stats['service_usage'][service_name] += 1
                
                print(f"✅ Переведено через {service_name}")
                return result
                
            except Exception as e:
                error_msg = f"{service_name}: {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                continue
        
        # Если все сервисы не сработали, возвращаем оригинальный текст
        print(f"⚠️ Все переводчики недоступны, возвращаем оригинальный текст")
        return TranslationResult(
            original=text,
            translated=text,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            service='fallback',
            confidence=0.0
        )
    
    def translate_batch(self, texts: List[str], show_progress: bool = True) -> List[TranslationResult]:
        """
        Переводит список текстов
        
        Args:
            texts: Список текстов
            show_progress: Показывать прогресс
            
        Returns:
            List[TranslationResult]: Список результатов перевода
        """
        results = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            if show_progress and i % 10 == 0:
                progress = (i / total) * 100
                print(f"Прогресс: {i}/{total} ({progress:.1f}%)")
            
            result = self.translate(text)
            results.append(result)
            
            # Небольшая пауза между запросами
            if i < total - 1:  # Не делаем паузу после последнего элемента
                time.sleep(0.1)
        
        if show_progress:
            print(f"Прогресс: {total}/{total} (100.0%)")
        
        return results
    
    def get_available_languages(self, service: str = 'google') -> List[str]:
        """Получает список поддерживаемых языков для сервиса"""
        if service not in self.translators:
            return []
        
        try:
            translator = self.translators[service]
            return translator.get_supported_languages()
        except Exception as e:
            print(f"Ошибка получения языков для {service}: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования"""
        return {
            'total_requests': self.stats['total_requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': (self.stats['cache_hits'] / max(1, self.stats['total_requests'])) * 100,
            'cache_size': len(self.cache),
            'service_usage': self.stats['service_usage'],
            'active_services': list(self.translators.keys()),
            'errors_count': len(self.stats['errors']),
            'errors': self.stats['errors'][-5:] if self.stats['errors'] else []  # Показываем только последние 5 ошибок
        }
    
    def clear_cache(self):
        """Очищает кеш переводов"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print(f"✅ Кеш очищен")


def get_available_services() -> List[str]:
    """Возвращает список доступных сервисов"""
    if not DEEP_TRANSLATOR_AVAILABLE:
        return []
    return list(EnhancedTranslator.AVAILABLE_SERVICES.keys())


def install_requirements():
    """Показывает инструкции по установке зависимостей"""
    print("📦 Установка зависимостей:")
    print()
    print("Основная библиотека:")
    print("  pip install deep-translator")
    print()
    print("Дополнительные возможности:")
    print("  pip install deep-translator[ai]     # Поддержка ChatGPT")
    print("  pip install deep-translator[pdf]    # Перевод PDF файлов") 
    print("  pip install deep-translator[docx]   # Перевод DOCX файлов")
    print()
    print("Все сразу:")
    print("  pip install 'deep-translator[ai,pdf,docx]'")


def main():
    """Основная функция для тестирования"""
    parser = argparse.ArgumentParser(
        description="Улучшенный переводчик с поддержкой множественных сервисов"
    )
    
    parser.add_argument('--source', '-s', default='russian',
                       help='Исходный язык')
    
    parser.add_argument('--target', '-t', default='english',
                       help='Целевой язык')
    
    parser.add_argument('--text', required=True,
                       help='Текст для перевода')
    
    parser.add_argument('--services', nargs='+', 
                       default=['google', 'libre', 'mymemory'],
                       help='Предпочтительные сервисы')
    
    parser.add_argument('--show-alternatives', action='store_true',
                       help='Показать альтернативные переводы')
    
    parser.add_argument('--install-deps', action='store_true',
                       help='Показать команды установки зависимостей')
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_requirements()
        return
    
    if not DEEP_TRANSLATOR_AVAILABLE:
        print("❌ deep-translator не установлен!")
        install_requirements()
        return
    
    # Создаем переводчик
    translator = EnhancedTranslator(
        source_lang=args.source,
        target_lang=args.target,
        preferred_services=args.services
    )
    
    # Переводим текст
    print(f"🌐 Перевод: {args.source} → {args.target}")
    print(f"📝 Исходный текст: {args.text}")
    print("-" * 50)
    
    result = translator.translate(args.text)
    
    print(f"✅ Переведенный текст: {result.translated}")
    print(f"🔧 Сервис: {result.service}")
    print(f"🎯 Уверенность: {result.confidence:.1%}")
    
    if args.show_alternatives and result.alternatives:
        print(f"🔄 Альтернативы: {', '.join(result.alternatives)}")
    
    # Показываем статистику
    stats = translator.get_stats()
    print(f"\n📊 Статистика:")
    print(f"  Запросов: {stats['total_requests']}")
    print(f"  Попаданий в кеш: {stats['cache_hits']}")
    print(f"  Активных сервисов: {len(stats['active_services'])}")


if __name__ == "__main__":
    main()
