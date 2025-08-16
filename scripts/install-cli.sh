#!/bin/bash
# Скрипт установки TranslateCore CLI

set -e

echo "🌍 Установка TranslateCore CLI"
echo "============================="

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT="$SCRIPT_DIR/translate-cli.py"

# Проверяем наличие основного скрипта
if [ ! -f "$CLI_SCRIPT" ]; then
    echo "❌ Файл translate-cli.py не найден в $SCRIPT_DIR"
    exit 1
fi

echo "✅ Найден CLI скрипт: $CLI_SCRIPT"

# Делаем исполняемым
chmod +x "$CLI_SCRIPT"
echo "✅ Установлены права на выполнение"

# Определяем, какую оболочку использует пользователь
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
    # На macOS часто используется .bash_profile
    if [[ "$OSTYPE" == "darwin"* ]] && [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    fi
    SHELL_NAME="bash"
else
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_NAME="неизвестная"
fi

echo "🐚 Обнаружена оболочка: $SHELL_NAME"
echo "📝 Файл конфигурации: $SHELL_CONFIG"

# Создаем алиас
ALIAS_LINE="alias translate-cli='python3 \"$CLI_SCRIPT\"'"

# Проверяем, есть ли уже алиас
if grep -q "alias translate-cli=" "$SHELL_CONFIG" 2>/dev/null; then
    echo "⚠️ Алиас translate-cli уже существует в $SHELL_CONFIG"
    read -p "Обновить алиас? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Удаляем старый алиас
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' '/alias translate-cli=/d' "$SHELL_CONFIG"
        else
            # Linux
            sed -i '/alias translate-cli=/d' "$SHELL_CONFIG"
        fi
        echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
        echo "✅ Алиас обновлен"
    else
        echo "⏭️ Алиас не изменен"
    fi
else
    # Добавляем новый алиас
    echo "" >> "$SHELL_CONFIG"
    echo "# TranslateCore CLI" >> "$SHELL_CONFIG"
    echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
    echo "✅ Алиас добавлен в $SHELL_CONFIG"
fi

# Проверяем установку Python пакетов
echo ""
echo "🔍 Проверка зависимостей..."

python3 -c "
try:
    import argparse, json, os
    print('✅ Базовые Python пакеты доступны')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    exit(1)
"

# Проверяем Argos Translate
python3 -c "
try:
    import argostranslate
    print('✅ Argos Translate установлен')
except ImportError:
    print('⚠️ Argos Translate не установлен')
    print('💡 Рекомендуется установить: pip install argostranslate')
"

echo ""
echo "🎉 Установка завершена!"
echo "========================"
echo ""
echo "📋 Чтобы использовать CLI:"
echo "1. Перезапустите терминал или выполните:"
echo "   source $SHELL_CONFIG"
echo ""
echo "2. Используйте команды:"
echo "   translate-cli \"Привет мир!\""
echo "   translate-cli -i                    # интерактивный режим"
echo "   translate-cli --setup               # мастер настройки"
echo "   translate-cli --help                # справка"
echo ""
echo "🔧 Для первоначальной настройки:"
echo "   translate-cli --setup"
echo ""

# Предлагаем запустить мастер настройки
read -p "🎯 Запустить мастер настройки сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 "$CLI_SCRIPT" --setup
fi
