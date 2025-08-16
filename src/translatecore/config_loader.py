#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузчик конфигурации API ключей для сервисов перевода
Обеспечивает безопасную работу с API ключами и конфигурациями
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys


class ConfigurationError(Exception):
    """Ошибка конфигурации"""
    pass


class APIConfigLoader:
    """Загрузчик конфигурации API ключей"""
    
    def __init__(self, config_file: str = None):
        """
        Инициализация загрузчика конфигурации
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file or "translation_api_config.json"
        self.config_data = None
        self._load_config()
    
    def _load_config(self):
        """Загружает конфигурацию из файла"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            # Пытаемся найти template файл
            template_path = Path("translation_api_config.template.json")
            if template_path.exists():
                raise ConfigurationError(
                    f"❌ Файл конфигурации {self.config_file} не найден!\n"
                    f"💡 Найден template файл. Выполните:\n"
                    f"   cp translation_api_config.template.json {self.config_file}\n"
                    f"   # Затем отредактируйте {self.config_file} и добавьте ваши API ключи"
                )
            else:
                raise ConfigurationError(
                    f"❌ Файл конфигурации {self.config_file} не найден!\n"
                    f"💡 Создайте файл конфигурации с API ключами."
                )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
                
            # Проверяем, что это не template файл
            if self.config_data.get('template', False):
                raise ConfigurationError(
                    f"❌ Используется template файл конфигурации!\n"
                    f"💡 Замените YOUR_*_API_KEY_HERE на реальные API ключи в {self.config_file}"
                )
                
            print(f"✅ Конфигурация загружена из {self.config_file}")
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"❌ Ошибка парсинга JSON в {self.config_file}: {e}")
    
    def get_api_keys(self, service_config_name: str = None) -> Dict[str, Any]:
        """
        Получает API ключи для указанной конфигурации сервиса
        
        Args:
            service_config_name: Название конфигурации сервиса
            
        Returns:
            Словарь с API ключами
        """
        if not self.config_data:
            raise ConfigurationError("Конфигурация не загружена")
        
        api_keys = {}
        
        # Если указана конфигурация сервиса, проверяем требуемые ключи
        if service_config_name:
            service_config = self.get_service_config(service_config_name)
            required_keys = service_config.get('required_keys', [])
            
            # Проверяем наличие всех требуемых ключей
            missing_keys = []
            for key_name in required_keys:
                if key_name not in self.config_data['api_keys']:
                    missing_keys.append(key_name)
                    continue
                
                key_data = self.config_data['api_keys'][key_name]
                
                # Проверяем разные типы ключей
                if key_name == 'papago':
                    if not key_data.get('client_id') or not key_data.get('secret_key'):
                        missing_keys.append(f"{key_name} (client_id и secret_key)")
                elif key_name == 'libre':
                    # LibreTranslate может работать без ключа
                    pass
                else:
                    if not key_data.get('key') or key_data['key'].startswith('YOUR_'):
                        missing_keys.append(key_name)
            
            if missing_keys:
                raise ConfigurationError(
                    f"❌ Отсутствуют API ключи для конфигурации '{service_config_name}':\n"
                    f"   Недостающие ключи: {', '.join(missing_keys)}\n"
                    f"💡 Добавьте ключи в {self.config_file}"
                )
        
        # Собираем все валидные API ключи
        for service_name, key_data in self.config_data['api_keys'].items():
            if service_name == 'papago':
                if key_data.get('client_id') and key_data.get('secret_key'):
                    if not key_data['client_id'].startswith('YOUR_'):
                        api_keys['papago_client_id'] = key_data['client_id']
                        api_keys['papago_secret_key'] = key_data['secret_key']
            elif service_name == 'libre':
                if key_data.get('key') and not key_data['key'].startswith('YOUR_'):
                    api_keys['libre'] = key_data['key']
                if key_data.get('base_url'):
                    api_keys['libre_url'] = key_data['base_url']
            else:
                if key_data.get('key') and not key_data['key'].startswith('YOUR_'):
                    api_keys[service_name] = key_data['key']
        
        # Также проверяем переменные окружения
        env_keys = {
            'deepl': 'DEEPL_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'microsoft': 'MICROSOFT_API_KEY',
            'yandex': 'YANDEX_API_KEY',
            'libre': 'LIBRE_API_KEY'
        }
        
        for service, env_var in env_keys.items():
            env_value = os.getenv(env_var)
            if env_value and service not in api_keys:
                api_keys[service] = env_value
                print(f"🌍 Использован API ключ {service} из переменной окружения")
        
        return api_keys
    
    def get_service_config(self, config_name: str) -> Dict[str, Any]:
        """
        Получает конфигурацию сервиса по имени
        
        Args:
            config_name: Название конфигурации
            
        Returns:
            Словарь с конфигурацией сервиса
        """
        if not self.config_data:
            raise ConfigurationError("Конфигурация не загружена")
        
        service_configs = self.config_data.get('service_configurations', {})
        
        if config_name not in service_configs:
            available = ', '.join(service_configs.keys())
            raise ConfigurationError(
                f"❌ Конфигурация '{config_name}' не найдена!\n"
                f"💡 Доступные конфигурации: {available}"
            )
        
        return service_configs[config_name]
    
    def get_services_for_config(self, config_name: str) -> List[str]:
        """
        Получает список сервисов для указанной конфигурации
        
        Args:
            config_name: Название конфигурации
            
        Returns:
            Список названий сервисов
        """
        config = self.get_service_config(config_name)
        return config.get('services', [])
    
    def list_available_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает список всех доступных конфигураций
        
        Returns:
            Словарь с конфигурациями и их описаниями
        """
        if not self.config_data:
            raise ConfigurationError("Конфигурация не загружена")
        
        return self.config_data.get('service_configurations', {})
    
    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """
        Проверяет валидность конфигурации
        
        Args:
            config_name: Название конфигурации для проверки
            
        Returns:
            Словарь с результатами проверки
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_keys': [],
            'available_services': []
        }
        
        try:
            # Проверяем существование конфигурации
            service_config = self.get_service_config(config_name)
            services = service_config.get('services', [])
            required_keys = service_config.get('required_keys', [])
            
            # Проверяем API ключи
            try:
                api_keys = self.get_api_keys(config_name)
                result['available_services'] = list(api_keys.keys())
            except ConfigurationError as e:
                result['valid'] = False
                result['errors'].append(str(e))
                
                # Определяем недостающие ключи
                for key_name in required_keys:
                    if key_name not in self.config_data.get('api_keys', {}):
                        result['missing_keys'].append(key_name)
                    else:
                        key_data = self.config_data['api_keys'][key_name]
                        if isinstance(key_data.get('key', ''), str) and key_data['key'].startswith('YOUR_'):
                            result['missing_keys'].append(key_name)
            
            # Предупреждения
            if 'google' not in services and 'offline' not in services:
                result['warnings'].append("Рекомендуется включить Google Translate или offline как резервный сервис")
            
            if len(services) == 1 and services[0] not in ['google', 'offline']:
                result['warnings'].append("Рекомендуется добавить резервный сервис (Google или offline)")
            
            # Специальное предупреждение для оффлайн режима
            if 'offline' in services:
                result['warnings'].append("Оффлайн режим: убедитесь, что установлен Argos Translate или запущен LibreTranslate")
                
        except ConfigurationError as e:
            result['valid'] = False
            result['errors'].append(str(e))
        
        return result
    
    def print_config_status(self):
        """Выводит статус конфигурации"""
        print(f"\n📋 Статус конфигурации ({self.config_file}):")
        print("=" * 50)
        
        configs = self.list_available_configs()
        
        for config_name, config_data in configs.items():
            print(f"\n🔧 {config_name}: {config_data['name']}")
            print(f"   📝 {config_data['description']}")
            
            # Проверяем валидность
            validation = self.validate_config(config_name)
            
            if validation['valid']:
                print("   ✅ Готова к использованию")
                if validation['available_services']:
                    print(f"   🌐 Сервисы: {', '.join(validation['available_services'])}")
            else:
                print("   ❌ Требуется настройка")
                if validation['missing_keys']:
                    print(f"   🔑 Недостающие ключи: {', '.join(validation['missing_keys'])}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    print(f"   ⚠️ {warning}")
            
            if config_data.get('recommended'):
                print("   ⭐ Рекомендуется")


def create_example_config():
    """Создает пример конфигурации с API ключами"""
    config_file = "translation_api_config.json"
    
    if Path(config_file).exists():
        print(f"⚠️ Файл {config_file} уже существует")
        return False
    
    # Создаем базовую конфигурацию с пустыми ключами
    template_path = Path("translation_api_config.template.json")
    
    if template_path.exists():
        # Копируем из template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Удаляем template флаг и обновляем ключи на пустые
        template_data['template'] = False
        for service_name, service_data in template_data['api_keys'].items():
            if 'key' in service_data:
                service_data['key'] = ""
            if service_name == 'papago':
                service_data['client_id'] = ""
                service_data['secret_key'] = ""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Создан файл конфигурации: {config_file}")
        print(f"💡 Заполните API ключи в файле для использования платных сервисов")
        return True
    else:
        print("❌ Template файл не найден")
        return False


def main():
    """Основная функция для тестирования конфигурации"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление конфигурацией API ключей")
    parser.add_argument('--config-file', default='translation_api_config.json',
                       help='Путь к файлу конфигурации')
    parser.add_argument('--create-example', action='store_true',
                       help='Создать пример конфигурации')
    parser.add_argument('--validate', metavar='CONFIG_NAME',
                       help='Проверить конкретную конфигурацию')
    parser.add_argument('--list', action='store_true',
                       help='Показать все доступные конфигурации')
    
    args = parser.parse_args()
    
    if args.create_example:
        create_example_config()
        return
    
    try:
        loader = APIConfigLoader(args.config_file)
        
        if args.list:
            loader.print_config_status()
        elif args.validate:
            result = loader.validate_config(args.validate)
            print(f"\n🔍 Проверка конфигурации '{args.validate}':")
            
            if result['valid']:
                print("✅ Конфигурация валидна")
            else:
                print("❌ Конфигурация содержит ошибки:")
                for error in result['errors']:
                    print(f"   • {error}")
            
            if result['warnings']:
                print("⚠️ Предупреждения:")
                for warning in result['warnings']:
                    print(f"   • {warning}")
        else:
            loader.print_config_status()
            
    except ConfigurationError as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
