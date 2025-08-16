# 🌍 TranslateCore CLI - Руководство пользователя

## 🚀 Быстрый старт

### Установка
```bash
# 1. Автоматическая установка (рекомендуется)
./install-cli.sh

# 2. Ручная установка
chmod +x translate-cli.py
alias translate-cli='python3 /path/to/translate-cli.py'
```

### Первое использование
```bash
# Быстрый перевод
translate-cli "Привет мир!"

# Мастер настройки (рекомендуется для первого запуска)
translate-cli --setup
```

---

## 🎯 Основные команды

### Простой перевод
```bash
# Автоопределение языка
translate-cli "Привет мир!"
translate-cli "Hello world!"

# С указанием языков
translate-cli -s russian -t english "Как дела?"
translate-cli -s english -t russian "How are you?"
```

### Интерактивный режим
```bash
translate-cli -i

# В интерактивном режиме:
# • Просто вводите текст для перевода
# • 'help' - справка
# • 'settings' - настройки  
# • 'history' - история
# • 'stats' - статистика
# • 'quit' - выход
```

### Работа с файлами
```bash
# Перевод из файла
translate-cli -f my_text.txt

# Сохранение результата
translate-cli "Текст" > result.txt
```

---

## ⚙️ Конфигурации

### Доступные конфигурации
```bash
# Показать все конфигурации
translate-cli --configs

# Использовать конкретную конфигурацию
translate-cli -c offline_only "Текст"      # Только оффлайн
translate-cli -c development "Текст"       # Оффлайн + онлайн
translate-cli -c production_basic "Текст"  # Премиум качество
```

### Рекомендуемые конфигурации:
- **`development`** - 🥇 Лучший выбор (оффлайн + бесплатные онлайн)
- **`offline_only`** - 🔌 Полная автономность
- **`production_basic`** - 💼 Для бизнеса (требует API ключи)

---

## 🛠️ Режимы вывода

### Краткий вывод
```bash
# Только результат перевода
translate-cli -q "Привет мир!"
# > Hello, world!
```

### Подробный вывод  
```bash
# Полная информация + статистика
translate-cli -v "Привет мир!"
```

### Без цветов
```bash
# Для скриптов и логов
translate-cli --no-colors "Текст"
```

---

## 📚 Управление историей

### Просмотр истории
```bash
translate-cli --history
```

### Экспорт истории
```bash
translate-cli --export-history backup.json
```

### Очистка истории
```bash
translate-cli --clear-history
```

---

## 🔧 Настройки и диагностика

### Статистика системы
```bash
translate-cli --stats
```

### Поддерживаемые языки
```bash
translate-cli --languages
```

### Установка зависимостей
```bash
translate-cli --install-deps
```

---

## 💡 Примеры использования

### Базовые сценарии
```bash
# Перевод фразы
translate-cli "Как дела?"
translate-cli "How are things?"

# Технический текст
translate-cli "Система работает корректно"

# Длинный текст
translate-cli "Это длинный текст, который нужно перевести для понимания содержания документа"
```

### Продвинутые сценарии
```bash
# Пакетная обработка
for text in "Привет" "Пока" "Спасибо"; do
    translate-cli -q "$text"
done

# Перевод из stdin
echo "Привет мир!" | translate-cli -f -

# С сохранением в файл
translate-cli "Важный текст" > translation.txt
```

### Интеграция в скрипты
```bash
#!/bin/bash
# Скрипт автоперевода
INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.txt}_translated.txt"

translate-cli -f "$INPUT_FILE" -q > "$OUTPUT_FILE"
echo "Перевод сохранен в: $OUTPUT_FILE"
```

---

## ⚡ Горячие клавиши и алиасы

### Создание удобных алиасов
```bash
# Добавьте в ~/.zshrc или ~/.bashrc
alias t='translate-cli'                    # Короткая команда
alias ti='translate-cli -i'                # Интерактивный режим  
alias tq='translate-cli -q'                # Краткий вывод
alias tr-ru='translate-cli -t russian'     # В русский
alias tr-en='translate-cli -t english'     # В английский
```

### Использование алиасов
```bash
t "Привет!"                    # Быстрый перевод
ti                             # Интерактивный режим
tq "Hello" > result.txt        # Краткий вывод в файл
tr-ru "Hello world"            # Перевод в русский
```

---

## 🐛 Устранение неполадок

### Частые проблемы

**Ошибка: "Модули не найдены"**
```bash
# Убедитесь, что запускаете из правильной директории
cd /path/to/TranslateCore
python3 translate-cli.py --help
```

**Ошибка: "Нет доступных методов перевода"**
```bash
# Установите Argos Translate
pip install argostranslate

# Или используйте онлайн сервисы
translate-cli -c development "Текст"
```

**Медленная работа**
```bash
# Используйте оффлайн режим
translate-cli -c offline_only "Текст"

# Или краткий вывод
translate-cli -q "Текст"
```

### Диагностика
```bash
# Проверка системы
translate-cli --stats

# Проверка конфигураций  
translate-cli --configs

# Verbose режим для отладки
translate-cli -v "Текст"
```

---

## 🎨 Персонализация

### Настройка по умолчанию
```bash
# Запустите интерактивный режим
translate-cli -i

# Введите 'settings' для изменения:
# • Целевой язык по умолчанию
# • Конфигурация по умолчанию  
# • Показ статистики
# • Сохранение истории
```

### Файлы конфигурации
- **`~/.translate_settings.json`** - Пользовательские настройки
- **`~/.translate_history.json`** - История переводов
- **`translation_api_config.json`** - Конфигурация сервисов

---

## 🚀 Профессиональные советы

### Максимальная эффективность
```bash
# 1. Используйте алиасы для частых команд
alias eng='translate-cli -t english -q'

# 2. Настройте конфигурацию по умолчанию
translate-cli --setup

# 3. Используйте краткий режим для скриптов
eng "Текст" > output.txt

# 4. Интерактивный режим для серии переводов
translate-cli -i
```

### Интеграция в рабочий процесс
```bash
# Создайте функцию в ~/.zshrc
translate_file() {
    input="$1"
    output="${input%.txt}_translated.txt"
    translate-cli -f "$input" -q > "$output"
    echo "✅ $input → $output"
}

# Использование
translate_file document.txt
```

---

## 🔗 Дополнительные ресурсы

- **Полная документация**: `OFFLINE_TRANSLATION_GUIDE.md`
- **Конфигурации API**: `API_CONFIG_GUIDE.md`
- **Сравнение методов**: `ARGOS_VS_LIBRETRANSLATE.md`
- **Справка по CLI**: `translate-cli --help`

---

## 🆘 Получение помощи

```bash
# Справка по командам
translate-cli --help

# Интерактивная справка
translate-cli -i
# > help

# Статистика и диагностика
translate-cli --stats
```

**Наслаждайтесь удобным переводом с TranslateCore CLI! 🌍✨**
