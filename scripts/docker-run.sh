#!/bin/bash
# 🐳 TranslateCore Docker Runner
# Удобный скрипт для запуска TranslateCore в Docker

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Логотип
echo -e "${GREEN}🌍 TranslateCore Docker Runner${NC}"
echo "=================================="

# Функция для отображения помощи
show_help() {
    echo "Использование: ./docker-run.sh [КОМАНДА] [ОПЦИИ]"
    echo ""
    echo "КОМАНДЫ:"
    echo "  build         - Собрать Docker образ"
    echo "  run          - Запустить интерактивный контейнер"
    echo "  translate    - Выполнить быстрый перевод"
    echo "  setup        - Запустить мастер настройки"
    echo "  demo         - Запустить демо оффлайн перевода"
    echo "  shell        - Запустить bash в контейнере"
    echo "  clean        - Очистить Docker ресурсы"
    echo "  logs         - Показать логи контейнера"
    echo "  stop         - Остановить контейнер"
    echo ""
    echo "ПРИМЕРЫ:"
    echo "  ./docker-run.sh build"
    echo "  ./docker-run.sh translate \"Привет мир!\""
    echo "  ./docker-run.sh run"
    echo "  ./docker-run.sh setup"
    echo ""
}

# Функция сборки
build_image() {
    echo -e "${YELLOW}📦 Building TranslateCore Docker image...${NC}"
    docker build -t translatecore:latest .
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
}

# Функция запуска интерактивного контейнера
run_interactive() {
    echo -e "${YELLOW}🚀 Starting TranslateCore container...${NC}"
    docker run -it --rm \
        --name translatecore_session \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/cache:/app/cache" \
        -v "$(pwd)/logs:/app/logs" \
        --env-file .env 2>/dev/null || true \
        translatecore:latest
}

# Функция быстрого перевода
quick_translate() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Error: Please provide text to translate${NC}"
        echo "Usage: ./docker-run.sh translate \"Your text here\""
        exit 1
    fi
    
    echo -e "${YELLOW}🔄 Translating: $1${NC}"
    
    # Проверяем наличие test образа
    if docker images | grep -q "translatecore:test"; then
        echo -e "${YELLOW}📦 Using test image (fast)...${NC}"
        docker run --rm \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/cache:/app/cache" \
            --env-file .env 2>/dev/null || true \
            translatecore:test \
            "translatecore '$1' ${@:2}"
    else
        echo -e "${YELLOW}📦 Auto-downloading language packages if needed...${NC}"
        docker run --rm \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/cache:/app/cache" \
            --env-file .env 2>/dev/null || true \
            translatecore:latest \
            "python3 translate-cli.py '$1'"
    fi
}

# Функция установки языкового пакета
install_language_package() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}❌ Error: Please provide source and target language codes${NC}"
        echo "Usage: ./docker-run.sh install-package en ru"
        exit 1
    fi
    
    echo -e "${YELLOW}📦 Installing language package: $1 → $2${NC}"
    docker run --rm \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/cache:/app/cache" \
        translatecore:latest \
        "python3 /app/auto_download_packages.py $1 $2"
}

# Функция настройки
run_setup() {
    echo -e "${YELLOW}⚙️ Starting TranslateCore setup wizard...${NC}"
    docker run -it --rm \
        --name translatecore_setup \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/cache:/app/cache" \
        --env-file .env 2>/dev/null || true \
        translatecore:latest \
        "python3 translate-cli.py --setup"
}

# Функция демо
run_demo() {
    echo -e "${YELLOW}🧪 Starting offline translation demo...${NC}"
    docker run -it --rm \
        --name translatecore_demo \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/cache:/app/cache" \
        translatecore:latest \
        "python3 demo_offline_only.py"
}

# Функция shell
run_shell() {
    echo -e "${YELLOW}🐚 Opening shell in TranslateCore container...${NC}"
    docker run -it --rm \
        --name translatecore_shell \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/cache:/app/cache" \
        -v "$(pwd)/logs:/app/logs" \
        --env-file .env 2>/dev/null || true \
        translatecore:latest \
        "/bin/bash"
}

# Функция очистки
clean_docker() {
    echo -e "${YELLOW}🧹 Cleaning Docker resources...${NC}"
    docker stop translatecore_session translatecore_setup translatecore_demo translatecore_shell 2>/dev/null || true
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
}

# Функция просмотра логов
show_logs() {
    if docker ps -q -f name=translatecore_session > /dev/null; then
        docker logs -f translatecore_session
    else
        echo -e "${RED}❌ No running TranslateCore container found${NC}"
    fi
}

# Функция остановки
stop_container() {
    echo -e "${YELLOW}🛑 Stopping TranslateCore containers...${NC}"
    docker stop translatecore_session translatecore_setup translatecore_demo translatecore_shell 2>/dev/null || true
    echo -e "${GREEN}✅ Containers stopped${NC}"
}

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден. Пожалуйста, установите Docker.${NC}"
    exit 1
fi

# Создание директорий если их нет
mkdir -p data cache logs

# Обработка аргументов командной строки
case "${1:-help}" in
    "build")
        build_image
        ;;
    "run")
        run_interactive
        ;;
    "translate")
        quick_translate "$2"
        ;;
    "setup")
        run_setup
        ;;
    "demo")
        run_demo
        ;;
    "shell")
        run_shell
        ;;
    "clean")
        clean_docker
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_container
        ;;
    "help"|*)
        show_help
        ;;
esac
