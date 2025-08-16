# 🐳 TranslateCore Docker Guide

**Полное руководство по использованию TranslateCore в Docker контейнерах**

## 🚀 **Быстрый старт**

### 1. Сборка и запуск
```bash
# Сборка образа
./docker-run.sh build

# Интерактивный запуск
./docker-run.sh run

# Быстрый перевод
./docker-run.sh translate "Привет мир!"
```

### 2. Настройка API ключей (опционально)
```bash
# Скопируйте шаблон
cp .env.example .env

# Отредактируйте .env файл с вашими API ключами
nano .env
```

---

## 📋 **Доступные команды**

| Команда | Описание | Пример |
|---------|----------|---------|
| `build` | 📦 Собрать Docker образ | `./docker-run.sh build` |
| `run` | 🚀 Интерактивный контейнер | `./docker-run.sh run` |
| `translate` | ⚡ Быстрый перевод | `./docker-run.sh translate "текст"` |
| `setup` | ⚙️ Мастер настройки | `./docker-run.sh setup` |
| `demo` | 🧪 Оффлайн демо | `./docker-run.sh demo` |
| `shell` | 🐚 Bash в контейнере | `./docker-run.sh shell` |
| `clean` | 🧹 Очистить ресурсы | `./docker-run.sh clean` |
| `logs` | 📋 Логи контейнера | `./docker-run.sh logs` |
| `stop` | 🛑 Остановить контейнеры | `./docker-run.sh stop` |

---

## 🎯 **Сценарии использования**

### 📱 **Персональное использование**
```bash
# 1. Сборка и первый запуск
./docker-run.sh build
./docker-run.sh setup

# 2. Интерактивная работа
./docker-run.sh run
# Внутри контейнера:
python3 translate-cli.py -i
```

### 💼 **Корпоративное развертывание**
```bash
# 1. Создание .env с API ключами
cp .env.example .env
# Заполните DeepL, OpenAI и другие ключи

# 2. Запуск с Docker Compose
docker-compose up -d

# 3. Подключение к контейнеру
docker exec -it translatecore /bin/bash
```

### 🔧 **CI/CD интеграция**
```bash
# Автоматический перевод в пайплайне
docker run --rm -v $(pwd):/workspace \
  translatecore:latest \
  "python3 translate-cli.py -f /workspace/content.txt"
```

---

## 🛠️ **Docker Compose**

### Обычный запуск
```bash
docker-compose up -d translatecore
```

### С LibreTranslate сервером
```bash
# Полная автономность с локальным сервером перевода
docker-compose --profile with-libretranslate up -d
```

### Конфигурация через переменные
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  translatecore:
    environment:
      - DEEPL_API_KEY=your_key_here
      - TRANSLATE_DEFAULT_CONFIG=production_basic
```

---

## 📂 **Persistent данные**

### Локальные директории
```bash
# Автоматически создаются при первом запуске
TranslateCore/
├── data/          # Пользовательские данные и настройки
├── cache/         # Кэш переводов
└── logs/          # Логи работы системы
```

### Docker volumes
```bash
# Просмотр volumes
docker volume ls | grep translatecore

# Очистка volumes
docker volume prune
```

---

## 🎛️ **Продвинутые настройки**

### Кастомные конфигурации
```bash
# Создайте директорию для пользовательских конфигов
mkdir -p custom_configs

# Создайте свой конфиг
cat > custom_configs/my_config.json << EOF
{
  "name": "my_custom_config",
  "services": ["argos", "google"],
  "fallback_enabled": true
}
EOF

# Запуск с кастомными конфигами
./docker-run.sh run
```

### Resource limits
```yaml
# docker-compose.yml
services:
  translatecore:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

### Healthcheck мониторинг
```bash
# Проверка состояния контейнера
docker inspect --format='{{json .State.Health}}' translatecore
```

---

## 🐛 **Troubleshooting**

### Проблема: Контейнер не запускается
```bash
# Проверка логов
docker logs translatecore

# Проверка образа
docker images | grep translatecore

# Пересборка
./docker-run.sh clean
./docker-run.sh build
```

### Проблема: Не работают API ключи
```bash
# Проверка переменных окружения
docker exec translatecore env | grep API

# Проверка .env файла
cat .env
```

### Проблема: Медленная работа
```bash
# Увеличение memory limits
docker-compose down
# Отредактируйте docker-compose.yml
docker-compose up -d
```

### Проблема: Языковые пакеты не установлены
```bash
# Переустановка языковых пакетов
./docker-run.sh shell
python3 -c "
import argostranslate.package
argostranslate.package.update_package_index()
# Установите нужные пакеты
"
```

---

## 📊 **Мониторинг и логи**

### Просмотр логов
```bash
# Логи в реальном времени
./docker-run.sh logs

# Логи Docker Compose
docker-compose logs -f translatecore
```

### Метрики контейнера
```bash
# Использование ресурсов
docker stats translatecore

# Детальная информация
docker inspect translatecore
```

---

## 🔄 **Обновление**

### Обновление образа
```bash
# Остановка текущих контейнеров
./docker-run.sh stop

# Сборка нового образа
git pull origin main
./docker-run.sh build

# Запуск с новой версией
./docker-run.sh run
```

### Бэкап пользовательских данных
```bash
# Создание backup
docker run --rm -v translatecore_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/translatecore_backup.tar.gz -C /data .

# Восстановление backup
docker run --rm -v translatecore_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/translatecore_backup.tar.gz -C /data
```

---

## 🌟 **Преимущества Docker версии**

### ✅ **Изоляция и безопасность**
- Изолированная среда выполнения
- Контролируемые ресурсы
- Безопасность пользовательских данных

### ✅ **Простота развертывания**
- Одна команда для запуска
- Автоматическая установка зависимостей
- Кроссплатформенность

### ✅ **Масштабируемость**
- Легко добавить новые экземпляры
- CI/CD интеграция
- Микросервисная архитектура

### ✅ **Сохранность данных**
- Persistent volumes для данных
- Автоматический бэкап настроек
- Легкое восстановление

---

## 📞 **Поддержка Docker**

- 🐳 **Docker Issues**: Проблемы с контейнерами
- 📋 **Logs**: `./docker-run.sh logs` 
- 🔍 **Debug**: `./docker-run.sh shell`
- 🧹 **Clean**: `./docker-run.sh clean`

**Наслаждайтесь изолированным и простым TranslateCore в Docker! 🐳✨**
