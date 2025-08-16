# 📦 Автоматическая загрузка языковых пакетов

**Руководство по автоматической загрузке языковых моделей для оффлайн перевода**

## 🚀 **Как это работает**

TranslateCore **автоматически** скачивает нужные языковые пакеты при первом использовании. Вам не нужно заранее устанавливать языковые модели!

### ✨ **Преимущества автозагрузки**
- 🎯 **Умная загрузка** - только нужные языки
- ⚡ **Быстрый старт** - работает из коробки
- 💾 **Экономия места** - не скачивает лишние модели
- 🔄 **Прозрачность** - видно что происходит

---

## 📋 **Как происходит автозагрузка**

### 1. **При первом переводе**
```bash
translate-cli "Привет мир!"

# Вывод:
📦 Автоматически скачиваем языковой пакет: ru→en...
   (это происходит только при первом использовании)
✅ Языковой пакет ru→en успешно установлен
✅ Переведено через argos_direct за 0.85с
Перевод: Hello world!
```

### 2. **При последующих переводах**
```bash
translate-cli "Как дела?"

# Вывод (без загрузки):
✅ Переведено через argos_direct за 0.12с  
Перевод: How are you?
```

---

## 🐳 **Docker и автозагрузка**

### **Предустановленные пакеты**
Docker контейнер уже содержит популярные языковые пары:
- 🇺🇸🇷🇺 **English ↔ Russian**
- 🇺🇸🇪🇸 **English ↔ Spanish**  
- 🇺🇸🇫🇷 **English ↔ French**
- 🇺🇸🇩🇪 **English ↔ German**
- 🇺🇸🇨🇳 **English ↔ Chinese**
- 🇺🇸🇯🇵 **English ↔ Japanese**
- 🇺🇸🇰🇷 **English ↔ Korean**
- 🇺🇸🇮🇹 **English ↔ Italian**
- 🇺🇸🇵🇹 **English ↔ Portuguese**

### **Автозагрузка новых пакетов в Docker**
```bash
# Если нужная пара не предустановлена, она загрузится автоматически
./docker-run.sh translate "Hola mundo"  # Spanish → English

# Или принудительно установить пакет
./docker-run.sh install-package es en
```

---

## ⚙️ **Настройка автозагрузки**

### **Отключение автозагрузки**
Если хотите контролировать загрузку вручную:

```python
# В enhanced_translator.py
offline_translator = OfflineTranslator(
    source_lang="russian",
    target_lang="english", 
    auto_download=False  # Отключить автозагрузку
)
```

### **Предзагрузка пакетов**
```bash
# Установить пакеты заранее
python3 -c "
import argostranslate.package
argostranslate.package.update_package_index()
available = argostranslate.package.get_available_packages()
for pkg in available:
    if pkg.from_code == 'ru' and pkg.to_code == 'en':
        argostranslate.package.install_from_path(pkg.download())
        break
"
```

---

## 🔍 **Диагностика загрузки**

### **Проверка установленных пакетов**
```bash
python3 -c "
import argostranslate.package
installed = argostranslate.package.get_installed_packages()
for pkg in installed:
    print(f'✅ {pkg.from_code} → {pkg.to_code}: {pkg.name}')
"
```

### **Список доступных пакетов**
```bash
python3 -c "
import argostranslate.package  
argostranslate.package.update_package_index()
available = argostranslate.package.get_available_packages()
for pkg in available:
    print(f'📦 {pkg.from_code} → {pkg.to_code}: {pkg.name}')
"
```

### **Статистика в CLI**
```bash
translate-cli --stats

# Показывает:
# - Доступные оффлайн методы
# - Установленные пакеты  
# - Статистику загрузок
```

---

## 🌍 **Поддерживаемые языки для автозагрузки**

### **Полностью поддерживаемые** (автозагрузка работает):
- **Европейские**: English, German, French, Spanish, Italian, Portuguese, Dutch, Czech
- **Славянские**: Russian, Ukrainian, Bulgarian  
- **Азиатские**: Chinese, Japanese, Korean
- **Другие**: Arabic, Catalan, Hungarian

### **Проверка доступности языка**
```bash
translate-cli --list-languages

# Или через Python
python3 -c "
from offline_translator import OfflineTranslator
langs = OfflineTranslator.get_supported_languages()
for key, info in langs.items():
    print(f'{key}: {info[\"name\"]} ({info[\"code\"]})')
"
```

---

## 📊 **Размеры языковых пакетов**

| Языковая пара | Размер | Время загрузки |
|---------------|--------|----------------|
| EN ↔ RU | ~50MB | ~15-30 сек |
| EN ↔ ES | ~45MB | ~15-25 сек |
| EN ↔ FR | ~45MB | ~15-25 сек |
| EN ↔ DE | ~45MB | ~15-25 сек |
| EN ↔ ZH | ~55MB | ~20-35 сек |
| EN ↔ JA | ~55MB | ~20-35 сек |

*Время зависит от скорости интернета при первой загрузке*

---

## 🚨 **Troubleshooting автозагрузки**

### **Проблема: Загрузка не работает**
```bash
# Проверьте интернет-подключение
ping google.com

# Обновите индекс пакетов вручную
python3 -c "
import argostranslate.package
argostranslate.package.update_package_index()
"
```

### **Проблема: Пакет не найден**
```bash
# Проверьте доступные пакеты
python3 offline_translator.py --list-languages

# Попробуйте другое направление перевода
translate-cli -s english -t russian "Hello"
```

### **Проблема: Недостаточно места**
```bash
# Размер папки с пакетами
du -sh ~/.local/share/argos-translate/packages/

# Удаление неиспользуемых пакетов
python3 -c "
import argostranslate.package
import os
installed = argostranslate.package.get_installed_packages()
for pkg in installed:
    print(f'rm -rf {pkg.path}')  # Команды для удаления
"
```

### **Проблема: Docker не может загрузить пакеты**
```bash
# Проверьте доступ к интернету в контейнере
./docker-run.sh shell
curl -I google.com

# Пересоберите образ с новыми пакетами
./docker-run.sh clean
./docker-run.sh build
```

---

## 🎯 **Лучшие практики**

### ✅ **Рекомендуется**
- Дайте системе автоматически загружать пакеты при необходимости
- Используйте Docker для изолированности
- Проверяйте статистику через `--stats`
- Предустанавливайте популярные пары в Docker

### ❌ **Не рекомендуется**  
- Загружать все доступные пакеты сразу
- Отключать автозагрузку без необходимости
- Удалять папки пакетов вручную
- Прерывать процесс загрузки

---

## 🔮 **Планы развития**

### **Ближайшие обновления**
- 🚀 **Фоновая загрузка** - пакеты загружаются в фоне
- 📊 **Умная предзагрузка** - на основе истории использования  
- 🎯 **Приоритетные пакеты** - важные языки загружаются первыми
- 💾 **Сжатие пакетов** - уменьшенные размеры моделей

### **Долгосрочные планы**
- 🌐 **P2P загрузка** - от других пользователей
- 🎨 **Кастомные модели** - собственные обученные модели
- ⚡ **Быстрые модели** - оптимизированные для скорости
- 🎯 **Специализированные модели** - для конкретных доменов

---

**🎉 Наслаждайтесь автоматической загрузкой языковых пакетов в TranslateCore!**

*Система сама позаботится о загрузке нужных моделей - вам остается только переводить! 🚀*
