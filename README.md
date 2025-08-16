# 🌍 TranslateCore

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![Offline](https://img.shields.io/badge/offline-supported-green.svg)](#offline-translation)

**TranslateCore** is a powerful, multilingual translation library that seamlessly combines offline and online translation capabilities. Built for production use, it offers automatic service fallback, intelligent caching, and support for multiple translation providers.

## ✨ Key Features

### 🔌 **Offline Translation**
- **Argos Translate Integration**: High-quality neural machine translation without internet
- **Automatic Package Management**: Downloads language pairs on-demand
- **Privacy First**: Your data never leaves your system
- **No API Limits**: Translate unlimited text for free

### 🌐 **Online Translation Services**
- **Google Translate**: Free tier with high accuracy
- **DeepL**: Premium quality translations
- **Microsoft Translator**: Enterprise-grade service
- **MyMemory**: Community-driven translations
- **PONS Dictionary**: Professional dictionary lookups
- **LibreTranslate**: Open-source translation API

### 🚀 **Smart Features**
- **Automatic Fallback**: Seamlessly switch between services
- **Intelligent Caching**: Speed up repeated translations
- **Language Detection**: Automatic source language identification
- **Batch Processing**: Translate multiple texts efficiently
- **Configuration Management**: Flexible service configurations

### 🛠️ **Developer Friendly**
- **CLI Interface**: Easy command-line usage
- **Python API**: Simple programmatic access
- **Docker Support**: Containerized deployment
- **Type Hints**: Full type annotation support
- **Comprehensive Tests**: Reliable and tested codebase

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/yourusername/translatecore.git
cd translatecore
pip install -r requirements.txt

# Make CLI available globally
chmod +x translate-cli.py
ln -s $(pwd)/translate-cli.py /usr/local/bin/translatecore
```

### Basic Usage

```python
from src.translatecore import EnhancedTranslator

# Initialize with default configuration
translator = EnhancedTranslator()

# Simple translation
result = translator.translate("Hello, world!", target_lang="es")
print(result.translated_text)  # ¡Hola, mundo!

# With source language specified
result = translator.translate("Bonjour", source_lang="fr", target_lang="en")
print(result.translated_text)  # Hello
```

### CLI Usage

```bash
# Basic translation
./translate-cli.py "Hello, world!" -t spanish

# Offline-only mode
./translate-cli.py "Private text" -c offline_only -t german

# Batch translation from file
./translate-cli.py -f input.txt -t french > output.txt

# Interactive mode
./translate-cli.py -i
```

## 📖 Configuration

TranslateCore uses a flexible configuration system with pre-built profiles:

### Available Configurations

| Configuration | Description | API Keys Required |
|---------------|-------------|-------------------|
| `offline_only` | Pure offline translation | None |
| `development` | Offline + free online services | None |
| `privacy_focused` | Privacy-first with minimal online | None |
| `production_basic` | Basic production with DeepL | DeepL |
| `production_premium` | Premium services | DeepL, Microsoft |
| `ai_powered` | AI-enhanced translations | OpenAI |
| `enterprise` | Full enterprise setup | Multiple |

### Custom Configuration

```json
{
  "services": ["offline", "google", "deepl"],
  "fallback_enabled": true,
  "cache_translations": true,
  "timeout": 10,
  "retry_attempts": 3
}
```

## 🔌 Offline Translation

TranslateCore's offline capabilities are powered by Argos Translate:

```python
from src.translatecore import OfflineTranslator

# Pure offline translator
offline = OfflineTranslator()

# Automatically downloads language packages on first use
result = offline.translate("Hello", source_lang="en", target_lang="es")
print(result)  # "Hola"

# Check available languages
print(offline.get_available_languages())
```

### Supported Language Pairs

Offline translation supports 40+ languages including:
- **European**: English, Spanish, French, German, Italian, Portuguese, Russian, Polish, Czech, Dutch
- **Asian**: Chinese, Japanese, Korean, Arabic, Hindi
- **Others**: Ukrainian, Turkish, Swedish, Norwegian, and more

## 🐳 Docker Support

### Quick Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use the convenience script
./scripts/docker-run.sh build
./scripts/docker-run.sh run "Hello, world!" --target es
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  translatecore:
    build: .
    environment:
      - DEEPL_API_KEY=${DEEPL_API_KEY}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
```

## 📊 Performance & Benchmarks

### Offline Translation Performance
- **Speed**: ~40-50 characters/second
- **Memory**: ~200MB per language pair
- **Accuracy**: 85-95% depending on language pair
- **Startup**: 2-3 seconds first run, instant thereafter

### Online Services Comparison

| Service | Speed | Accuracy | Free Tier | Rate Limits |
|---------|-------|----------|-----------|-------------|
| Google | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 100,000 chars/month |
| DeepL | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 500,000 chars/month |
| Offline | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Unlimited | None |

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_offline/ -v
python -m pytest tests/test_online/ -v

# Run offline demo
python tests/test_offline_demo.py

# Performance benchmarks
python tests/benchmark.py
```

## 📚 API Reference

### EnhancedTranslator

The main translator class with full online/offline capabilities.

```python
class EnhancedTranslator:
    def __init__(self, config_name: str = "development")
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "english") -> TranslationResult
    def detect_language(self, text: str) -> str
    def get_supported_languages(self) -> List[str]
    def get_translation_history(self) -> List[TranslationResult]
```

### OfflineTranslator

Offline-only translator using Argos Translate.

```python
class OfflineTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str
    def install_language_pair(self, source: str, target: str) -> bool
    def get_available_languages(self) -> List[str]
    def get_installed_packages(self) -> List[dict]
```

### TranslationResult

```python
@dataclass
class TranslationResult:
    translated_text: str
    source_language: str
    target_language: str
    service_used: str
    translation_time: float
    confidence_score: Optional[float] = None
```

## 🔧 Advanced Usage

### Custom Service Configuration

```python
# Create custom translator with specific services
translator = EnhancedTranslator()
translator.configure_services({
    "services": ["offline", "google"],
    "fallback_chain": ["offline", "google"],
    "timeout": 15,
    "cache_enabled": True
})
```

### Batch Translation

```python
texts = ["Hello", "World", "How are you?"]
results = translator.batch_translate(texts, target_lang="es")
for result in results:
    print(f"{result.source_text} -> {result.translated_text}")
```

### Error Handling

```python
try:
    result = translator.translate("Hello", target_lang="invalid")
except TranslationError as e:
    print(f"Translation failed: {e}")
except ServiceUnavailableError as e:
    print(f"Service error: {e}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/translatecore.git
cd translatecore

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Argos Translate** for excellent offline translation capabilities
- **translate** library for online service integrations
- All contributors and testers who helped improve this project

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Test Reports**: [docs/test-report.md](docs/test-report.md)
- **Docker Hub**: *Coming soon*
- **PyPI**: *Coming soon*

---

<div align="center">

**Built with ❤️ for the developer community**

[⭐ Star this repo](https://github.com/yourusername/translatecore) | [🐛 Report Bug](https://github.com/yourusername/translatecore/issues) | [💡 Request Feature](https://github.com/yourusername/translatecore/issues)

</div>
