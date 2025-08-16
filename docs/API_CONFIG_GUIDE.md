# 🔑 Руководство по Конфигурации API Ключей

Это руководство описывает, как настроить и использовать систему конфигурации API ключей для сервисов перевода.

## 🚀 Быстрый Старт

### 1. Создание Конфигурационного Файла

```bash
# Скопируйте template файл
cp translation_api_config.template.json translation_api_config.json

# Добавьте в .gitignore для безопасности  
echo 'translation_api_config.json' >> .gitignore
```

### 2. Добавление API Ключей

Отредактируйте `translation_api_config.json` и замените `YOUR_*_API_KEY_HERE` на реальные ключи:

```json
{
  "api_keys": {
    "deepl": {
      "key": "ваш_реальный_ключ_deepl"
    },
    "openai": {
      "key": "ваш_реальный_ключ_openai"
    }
  }
}
```

### 3. Проверка Конфигурации

```bash
# Просмотр всех конфигураций
python3 config_loader.py --list

# Проверка конкретной конфигурации
python3 config_loader.py --validate development
```

### 4. Использование в Коде

```python
from enhanced_translator import EnhancedTranslator

# Использование конфигурации
translator = EnhancedTranslator(
    source_lang='russian',
    target_lang='english',
    config_file='translation_api_config.json',
    service_config_name='development'  # или другая конфигурация
)

result = translator.translate("Привет мир!")
print(result.translated)  # "Hello World!"
```

## 📋 Доступные Конфигурации

### 🟢 `development` (Рекомендуется для старта)
**Описание:** Бесплатные сервисы для разработки и тестирования  
**Сервисы:** Google Translate, Linguee  
**API ключи:** Не требуются  
**Использование:**
```python
translator = EnhancedTranslator(
    source_lang='russian', target_lang='english',
    config_file='translation_api_config.json',
    service_config_name='development'
)
```

### 🟡 `production_basic` (Рекомендуется для продакшн)
**Описание:** Google + DeepL для надежности и качества  
**Сервисы:** Google Translate, DeepL  
**API ключи:** DeepL API ключ  
**Использование:**
```bash
# Получите DeepL API ключ на https://www.deepl.com/pro-api
# Добавьте в translation_api_config.json
```

### 🔴 `production_premium`
**Описание:** Все лучшие платные сервисы  
**Сервисы:** DeepL, Microsoft Translator, Google  
**API ключи:** DeepL, Microsoft  

### 🔒 `privacy_focused`
**Описание:** Только собственные или приватные сервисы  
**Сервисы:** LibreTranslate  
**API ключи:** LibreTranslate (опционально)  

### 🤖 `ai_powered`
**Описание:** ChatGPT для контекстного перевода  
**Сервисы:** OpenAI ChatGPT, Google  
**API ключи:** OpenAI API ключ  

### 🏢 `multilingual_enterprise`
**Описание:** Все доступные сервисы для максимальной надежности  
**Сервисы:** DeepL, Microsoft, Google, Yandex, LibreTranslate  
**API ключи:** DeepL, Microsoft, Yandex  

## 🔑 Получение API Ключей

### DeepL (Лучшее качество)
1. **Регистрация:** https://www.deepl.com/pro-api
2. **Бесплатный план:** 500,000 символов/месяц
3. **Стоимость:** От $6.99/месяц за безлимит
4. **Настройка:**
   ```json
   "deepl": {
     "key": "ваш_ключ_deepl"
   }
   ```

### OpenAI ChatGPT (Контекстный перевод)
1. **Регистрация:** https://platform.openai.com
2. **Бесплатный план:** $5 кредитов при регистрации
3. **Стоимость:** Pay-per-use (~$0.002/1K токенов)
4. **Настройка:**
   ```json
   "openai": {
     "key": "ваш_ключ_openai"
   }
   ```

### Microsoft Translator (Корпоративное решение)
1. **Регистрация:** https://azure.microsoft.com/services/cognitive-services/translator/
2. **Бесплатный план:** 2M символов/месяц
3. **Стоимость:** От $10/1M символов
4. **Настройка:**
   ```json
   "microsoft": {
     "key": "ваш_ключ_microsoft"
   }
   ```

### Yandex Translate (Сильный в русском)
1. **Регистрация:** https://cloud.yandex.com/services/translate
2. **Бесплатный план:** Нет
3. **Стоимость:** От ₽1.20/1M символов
4. **Настройка:**
   ```json
   "yandex": {
     "key": "ваш_ключ_yandex"
   }
   ```

### LibreTranslate (Приватность)
1. **Собственный сервер:** https://github.com/LibreTranslate/LibreTranslate
2. **Облачный доступ:** https://libretranslate.com
3. **Стоимость:** От $10/месяц или бесплатно на своем сервере
4. **Настройка:**
   ```json
   "libre": {
     "key": "ваш_ключ_libre_или_пусто",
     "base_url": "https://ваш-сервер.com"
   }
   ```

## 🛠️ Использование Конфигурации

### Прямое Использование Enhanced Translator

```python
from enhanced_translator import EnhancedTranslator

# С конфигурационным файлом
translator = EnhancedTranslator(
    source_lang='russian',
    target_lang='english',
    config_file='translation_api_config.json',
    service_config_name='production_basic'
)

# Перевод одного текста
result = translator.translate("Привет мир!")
print(f"Перевод: {result.translated}")
print(f"Сервис: {result.service}")

# Батчевый перевод
texts = ["Привет", "Как дела?", "До свидания"]
results = translator.translate_batch(texts)
for result in results:
    print(f"'{result.original}' → '{result.translated}'")
```

### Использование в Auto Extract Translate

```bash
# Автоперевод проекта с конфигурацией
python3 auto_extract_translate.py \
  --project my_project \
  --config-file translation_api_config.json \
  --service-config development
```

### Загрузчик Конфигурации

```python
from config_loader import APIConfigLoader

# Загрузка и валидация
loader = APIConfigLoader('translation_api_config.json')

# Получение API ключей для конфигурации
api_keys = loader.get_api_keys('production_basic')

# Получение списка сервисов
services = loader.get_services_for_config('development')

# Валидация конфигурации
validation = loader.validate_config('ai_powered')
if not validation['valid']:
    print("Ошибки:", validation['errors'])
```

## 🔧 Управление Конфигурацией

### Командная Строка

```bash
# Создание пример файла конфигурации
python3 config_loader.py --create-example

# Просмотр всех конфигураций и их статуса
python3 config_loader.py --list

# Проверка конкретной конфигурации
python3 config_loader.py --validate production_basic

# Проверка с указанием файла
python3 config_loader.py --config-file my_config.json --list
```

### Программное Управление

```python
from config_loader import APIConfigLoader, ConfigurationError

try:
    loader = APIConfigLoader('translation_api_config.json')
    
    # Получение всех конфигураций
    configs = loader.list_available_configs()
    
    for name, config in configs.items():
        print(f"{name}: {config['description']}")
        
        # Проверка готовности
        validation = loader.validate_config(name)
        if validation['valid']:
            print(f"  ✅ Готова к использованию")
        else:
            print(f"  ❌ Требуется: {validation['missing_keys']}")
            
except ConfigurationError as e:
    print(f"Ошибка конфигурации: {e}")
```

## 🔒 Безопасность

### Важные Правила

1. **НЕ коммитьте** `translation_api_config.json` в публичные репозитории
2. **Используйте** `.gitignore` для исключения файлов с ключами
3. **Храните** резервные копии API ключей в безопасном месте
4. **Регулярно обновляйте** API ключи для безопасности

### Настройка .gitignore

```gitignore
# API ключи - НЕ ПУБЛИКОВАТЬ!
translation_api_config.json
*api_config*.json
*.api_keys

# Кеши и временные файлы
translation_cache_*.json
*_cache*.json
temp_config_*.json
```

### Переменные Окружения

Альтернативно, можно использовать переменные окружения:

```bash
# Установка API ключей через переменные окружения
export DEEPL_API_KEY="ваш_ключ_deepl"
export OPENAI_API_KEY="ваш_ключ_openai"
export MICROSOFT_API_KEY="ваш_ключ_microsoft"

# Система автоматически их подхватит
python3 enhanced_translator.py --text "Привет мир!"
```

### Для CI/CD

```yaml
# В GitHub Actions или других CI/CD системах
env:
  DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 🧪 Тестирование

### Проверка Конфигураций

```bash
# Полное тестирование всех конфигураций
python3 test_config_demo.py

# Быстрый тест рабочей конфигурации
python3 enhanced_translator.py \
  --config-file translation_api_config.json \
  --service-config development \
  --text "Тест конфигурации"
```

### Отладка Проблем

```python
from config_loader import APIConfigLoader

# Подробная диагностика
loader = APIConfigLoader('translation_api_config.json')
validation = loader.validate_config('production_basic')

print("Статус:", "✅ OK" if validation['valid'] else "❌ Ошибки")
print("Доступные сервисы:", validation['available_services'])
print("Недостающие ключи:", validation['missing_keys'])
print("Предупреждения:", validation['warnings'])
```

## 💡 Рекомендации

### Для Разработки
- Используйте `development` конфигурацию
- Google Translate покрывает 95% потребностей
- Не тратьте деньги на платные API во время разработки

### Для Продакшн
- Используйте `production_basic` с DeepL + Google
- Настройте мониторинг квот API
- Имейте резервный план при превышении лимитов

### Для Корпоративных Проектов
- `multilingual_enterprise` для максимальной надежности
- Собственный LibreTranslate сервер для приватности
- Мониторинг использования и затрат

### Экономия Средств
- Используйте кеширование (включено по умолчанию)
- Батчевая обработка вместо поодиночки  
- Начинайте с бесплатных планов сервисов
- Оптимизируйте тексты перед переводом

## 📚 Примеры Использования

### Базовый Пример

```python
translator = EnhancedTranslator(
    source_lang='russian',
    target_lang='english',
    config_file='translation_api_config.json',
    service_config_name='development'
)

result = translator.translate("Добро пожаловать!")
print(result.translated)  # "Welcome!"
```

### Продвинутый Пример

```python
# Загрузка конфигурации и создание переводчика
from config_loader import APIConfigLoader
from enhanced_translator import EnhancedTranslator

loader = APIConfigLoader('translation_api_config.json')

# Проверяем доступность конфигурации
if loader.validate_config('production_basic')['valid']:
    translator = EnhancedTranslator(
        source_lang='russian',
        target_lang='english',
        config_file='translation_api_config.json',
        service_config_name='production_basic'
    )
else:
    # Fallback на development
    translator = EnhancedTranslator(
        source_lang='russian',
        target_lang='english',
        config_file='translation_api_config.json',
        service_config_name='development'
    )

# Массовый перевод с прогрессом
texts = ["Привет", "Как дела?", "До свидания", "Спасибо"]
results = translator.translate_batch(texts, show_progress=True)

# Статистика
stats = translator.get_stats()
print(f"Обработано запросов: {stats['total_requests']}")
print(f"Использованы сервисы: {stats['service_usage']}")
```

## ❓ Часто Задаваемые Вопросы

**Q: Как получить бесплатный API ключ DeepL?**
A: Зарегистрируйтесь на https://www.deepl.com/pro-api и получите 500K символов/месяц бесплатно.

**Q: Можно ли использовать систему без API ключей?**
A: Да, конфигурация `development` работает только с бесплатными сервисами.

**Q: Как добавить собственный сервис перевода?**
A: Расширьте класс `EnhancedTranslator` и добавьте новый сервис в `AVAILABLE_SERVICES`.

**Q: Безопасно ли хранить API ключи в файле?**
A: Да, если файл добавлен в `.gitignore` и не публикуется. Для CI/CD используйте переменные окружения.

**Q: Что делать при превышении квоты API?**
A: Система автоматически переключится на следующий доступный сервис в конфигурации.

---

Для получения помощи и дополнительной информации обращайтесь к документации проекта TranslateCore.
