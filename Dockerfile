# 🐳 TranslateCore Docker Container
# Универсальный контейнер с полной поддержкой оффлайн и онлайн переводов

FROM python:3.11-slim

# Метаданные
LABEL maintainer="TranslateCore Team"
LABEL description="Advanced translation system with offline support and CLI interface"
LABEL version="1.0.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd -m -u 1000 translator && \
    mkdir -p /app && \
    chown -R translator:translator /app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов requirements (если есть) или установка зависимостей напрямую
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Установка основных зависимостей TranslateCore
RUN pip install --no-cache-dir \
    deep-translator==1.11.4 \
    requests>=2.28.0 \
    argostranslate>=1.8.0 \
    openai>=1.0.0 \
    colorama>=0.4.6 \
    typing-extensions>=4.0.0

# Копирование исходного кода
COPY --chown=translator:translator . .

# Создание директорий для пользовательских данных
RUN mkdir -p /app/data /app/cache /app/logs && \
    chown -R translator:translator /app/data /app/cache /app/logs

# Установка прав на выполнение для скриптов
RUN chmod +x translate-cli.py scripts/*.sh examples/*.py || true

# Переключение на пользователя translator
USER translator

# Создание скрипта автоматической загрузки языковых пакетов
RUN cat > /app/auto_download_packages.py << 'EOF'
#!/usr/bin/env python3
import argostranslate.package
import argostranslate.translate
import sys
import os

def ensure_language_package(from_code, to_code):
    """Автоматически скачивает языковой пакет если нужен"""
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
            print(f'📦 Auto-downloading language package: {from_code} → {to_code}')
            argostranslate.package.install_from_path(package.download())
            print(f'✅ Package installed successfully: {from_code} → {to_code}')
            return True
        else:
            print(f'⚠️ Language package not available: {from_code} → {to_code}')
            return False
            
    except Exception as e:
        print(f'❌ Error downloading package {from_code}→{to_code}: {e}')
        return False

if __name__ == '__main__':
    # Предустанавливаем популярные пары
    popular_pairs = [
        ('en', 'ru'), ('ru', 'en'),
        ('en', 'es'), ('es', 'en'),  
        ('en', 'fr'), ('fr', 'en'),
        ('en', 'de'), ('de', 'en'),
        ('en', 'zh'), ('zh', 'en'),
        ('en', 'ja'), ('ja', 'en'),
        ('en', 'ko'), ('ko', 'en'),
        ('en', 'it'), ('it', 'en'),
        ('en', 'pt'), ('pt', 'en'),
    ]
    
    print('🌍 Pre-installing popular language packages...')
    success_count = 0
    
    for from_lang, to_lang in popular_pairs:
        if ensure_language_package(from_lang, to_lang):
            success_count += 1
    
    print(f'🎉 Installed {success_count}/{len(popular_pairs)} language packages')
    
    # Если переданы аргументы, скачиваем конкретную пару
    if len(sys.argv) == 3:
        from_code, to_code = sys.argv[1], sys.argv[2]
        ensure_language_package(from_code, to_code)
EOF

# Предварительная загрузка популярных пакетов
RUN python3 /app/auto_download_packages.py || echo "⚠️ Some language packages installation failed, but container will still work"

# Создание алиаса для удобства
RUN echo 'alias translate-cli="python3 /app/translate-cli.py"' >> ~/.bashrc

# Открытие портов (если понадобится веб-интерфейс в будущем)
EXPOSE 8080

# Переменные окружения
ENV PYTHONPATH=/app
ENV TRANSLATE_DATA_DIR=/app/data
ENV TRANSLATE_CACHE_DIR=/app/cache
ENV TRANSLATE_LOG_DIR=/app/logs

# Volumes для персистентных данных
VOLUME ["/app/data", "/app/cache", "/app/logs"]

# Точка входа по умолчанию - интерактивная оболочка с TranslateCore
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["echo '🌍 Welcome to TranslateCore Docker Container!' && echo 'Usage examples:' && echo '  python3 translate-cli.py \"Hello World!\"' && echo '  python3 translate-cli.py -i' && echo '  python3 translate-cli.py --setup' && echo '' && exec /bin/bash"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.path.append('/app/src'); from translatecore import OfflineTranslator; print('✅ Container healthy')" || exit 1
