# 🔌 Руководство по оффлайн переводу TranslateCore

## Обзор

Система оффлайн перевода позволяет переводить тексты без подключения к интернету и внешним API сервисам. Это обеспечивает приватность, независимость от внешних сервисов и возможность работать в изолированных средах.

## 🛠️ Архитектура системы

Оффлайн перевод в TranslateCore поддерживает несколько методов:

### 1. **Argos Translate** (Рекомендуется)
- 🏆 **Лучший выбор для оффлайн перевода**
- 📦 Локальная установка Python библиотеки
- 🚀 Высокая скорость работы
- 💾 Модульная система языковых пакетов

### 2. **LibreTranslate Server**
- 🌐 Собственный сервер перевода
- 🔒 Полный контроль и приватность
- 🐳 Легкий запуск через Docker

### 3. **LibreTranslate Docker**
- ⚡ Быстрый старт через контейнер
- 🔧 Автоматическое управление жизненным циклом

## 📋 Установка и настройка

### Вариант 1: Argos Translate (Рекомендуется)

```bash
# 1. Установка Argos Translate
pip install argostranslate

# 2. Установка языковых пакетов
python3 -c "
import argostranslate.package
# Пример: русский -> английский
package = argostranslate.package.install_from_path('translate-ru_en-1_9.argosmodel')
"

# 3. Тестирование
python3 offline_translator.py --method argos --text 'Привет мир!'
```

### Вариант 2: LibreTranslate Docker

```bash
# 1. Установка и запуск через Docker
docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate

# 2. Тестирование
python3 offline_translator.py --method libretranslate_docker --text 'Привет мир!'

# 3. Остановка
docker stop libretranslate
```

### Вариант 3: Собственный LibreTranslate сервер

```bash
# 1. Установка LibreTranslate
pip install libretranslate

# 2. Запуск сервера
libretranslate --host 0.0.0.0 --port 5000

# 3. Использование
python3 offline_translator.py --method libretranslate_local --text 'Привет мир!'
```

## 🎯 Использование в конфигурациях

### Конфигурация "offline_only"
Полностью автономный режим - только оффлайн перевод:

```json
{
  "offline_only": {
    "name": "Полностью автономный оффлайн",
    "description": "Оффлайн перевод без интернета и внешних API",
    "services": ["offline"],
    "required_keys": [],
    "recommended": true
  }
}
```

### Конфигурация "development"
Оффлайн + бесплатные онлайн сервисы:

```json
{
  "development": {
    "name": "Разработка и тестирование",
    "description": "Оффлайн + бесплатные онлайн сервисы",
    "services": ["offline", "google", "linguee"],
    "required_keys": [],
    "recommended": true
  }
}
```

## 💻 Примеры использования

### Базовое использование

```python
from enhanced_translator import EnhancedTranslator

# Создание переводчика с оффлайн приоритетом
translator = EnhancedTranslator(
    config_file='translation_api_config.json',
    service_config_name='offline_only'
)

# Перевод
result = translator.translate('Привет мир!', target_lang='en')
print(f"Перевод: {result.text}")  # Hello world!
print(f"Сервис: {result.service}")  # offline
```

### Пакетный перевод

```python
from offline_translator import OfflineTranslator

translator = OfflineTranslator()

texts = [
    "Привет мир!",
    "Как дела?",
    "Система работает"
]

# Пакетный перевод
results = translator.batch_translate(texts, 'ru', 'en')

for original, translation in zip(texts, results):
    print(f"'{original}' → '{translation.text}'")
```

### CLI использование

```bash
# Прямое использование оффлайн переводчика
python3 offline_translator.py --text "Привет мир!" --source-lang ru --target-lang en

# Через enhanced_translator с конфигурацией
python3 enhanced_translator.py \
    --config-file translation_api_config.json \
    --service-config offline_only \
    --text "Привет мир!"

# Пакетный перевод файла
python3 auto_extract_translate.py \
    --project ./my_project \
    --config-file translation_api_config.json \
    --service-config offline_only
```

## 🔧 Управление языковыми моделями

### Argos Translate - установка пакетов

```python
from offline_translator import OfflineTranslator

translator = OfflineTranslator()

# Установка языкового пакета
success = translator.install_argos_package('ru', 'en')
if success:
    print("Пакет установлен успешно!")

# Список доступных пакетов
available = translator.get_available_packages()
print("Доступные пакеты:", available)

# Список установленных пакетов
installed = translator.get_installed_packages()
print("Установленные пакеты:", installed)
```

### LibreTranslate - управление Docker контейнером

```python
from offline_translator import OfflineTranslator

translator = OfflineTranslator(method='libretranslate_docker')

# Запуск контейнера
if translator.start_libretranslate_docker():
    print("LibreTranslate контейнер запущен!")

# Проверка статуса
if translator.is_libretranslate_running():
    print("LibreTranslate работает")

# Остановка контейнера
translator.stop_libretranslate_docker()
```

## 📊 Производительность и ограничения

### Argos Translate
- **Качество**: ⭐⭐⭐⭐ (очень хорошо)
- **Скорость**: ⚡⚡⚡⭐ (быстро)
- **Размер моделей**: 20-50 MB на языковую пару
- **Языки**: 30+ поддерживаемых языков
- **RAM**: ~200-500 MB на модель

### LibreTranslate
- **Качество**: ⭐⭐⭐⭐⭐ (отлично)
- **Скорость**: ⚡⚡⭐⭐ (средне)
- **Размер**: ~2-5 GB (полная установка)
- **Языки**: 30+ поддерживаемых языков
- **RAM**: ~1-2 GB

## 🎛️ Конфигурация и настройки

### Настройка offline_translator.py

```python
# Конфигурация методов по приоритету
TRANSLATION_METHODS = [
    'argos',                    # Приоритет 1
    'libretranslate_local',     # Приоритет 2
    'libretranslate_docker'     # Приоритет 3
]

# Настройка Docker контейнера
DOCKER_CONFIG = {
    'image': 'libretranslate/libretranslate',
    'port': 5000,
    'container_name': 'libretranslate_offline'
}
```

### Кэширование переводов

Система автоматически кэширует переводы для повышения производительности:

```python
# Кэш автоматически используется
result1 = translator.translate("Привет!", 'ru', 'en')  # Выполняется перевод
result2 = translator.translate("Привет!", 'ru', 'en')  # Берется из кэша

# Очистка кэша
translator.clear_cache()

# Отключение кэша
result = translator.translate("Привет!", 'ru', 'en', use_cache=False)
```

## 🚨 Устранение неполадок

### Проблема: Argos Translate не работает
```bash
# Проверка установки
python3 -c "import argostranslate; print('OK')"

# Переустановка
pip uninstall argostranslate
pip install argostranslate

# Проверка пакетов
python3 -c "
import argostranslate.package
print(argostranslate.package.get_installed_packages())
"
```

### Проблема: LibreTranslate не запускается в Docker
```bash
# Проверка Docker
docker --version

# Загрузка образа
docker pull libretranslate/libretranslate

# Проверка запущенных контейнеров
docker ps

# Логи контейнера
docker logs libretranslate
```

### Проблема: Медленный перевод
- **Для Argos**: Убедитесь, что установлены только нужные языковые пакеты
- **Для LibreTranslate**: Выделите больше RAM контейнеру
- Используйте кэширование для повторных переводов

## 🔄 Интеграция с TranslateCore

### Автоматическое использование в enhanced_translator

```python
# Оффлайн переводчик автоматически добавляется в список сервисов
# если доступен любой из методов (Argos или LibreTranslate)

from enhanced_translator import EnhancedTranslator

# При создании переводчика оффлайн сервис получает высший приоритет
translator = EnhancedTranslator()  # offline будет использоваться первым

# Проверка доступности
if 'offline' in translator.available_services:
    print("Оффлайн перевод доступен!")
```

### Использование в проектах

```bash
# В реальных проектах рекомендуется конфигурация 'development'
# которая включает оффлайн + онлайн сервисы как резерв

python3 auto_extract_translate.py \
    --project ./my_app \
    --target-languages en,de,fr \
    --config-file translation_api_config.json \
    --service-config development  # offline + google + linguee
```

## 🌟 Лучшие практики

1. **Выбор метода**:
   - Для разработки: Argos Translate
   - Для продакшна: LibreTranslate сервер
   - Для тестирования: LibreTranslate Docker

2. **Управление ресурсами**:
   - Установите только нужные языковые пары
   - Используйте кэширование для частых переводов
   - Мониторьте использование RAM

3. **Качество переводов**:
   - Комбинируйте с онлайн сервисами для критичных переводов
   - Тестируйте качество на вашем домене
   - Используйте постобработку текста

4. **Безопасность**:
   - Оффлайн перевод гарантирует приватность данных
   - Нет передачи текстов третьим сторонам
   - Полный контроль над процессом перевода

## 📚 Дополнительные ресурсы

- [Argos Translate GitHub](https://github.com/argosopentech/argos-translate)
- [LibreTranslate GitHub](https://github.com/LibreTranslate/LibreTranslate)  
- [Docker Hub LibreTranslate](https://hub.docker.com/r/libretranslate/libretranslate)
- [Документация TranslateCore](./API_CONFIG_GUIDE.md)

---

💡 **Совет**: Начните с конфигурации `offline_only` для тестирования, затем переходите на `development` для получения наилучших результатов с резервными онлайн сервисами.
