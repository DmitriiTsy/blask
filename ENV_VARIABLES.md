# Переменные окружения - Полное руководство

## 📍 Где разместить переменные

Создайте файл `.env` в корневой директории проекта:

```bash
cd /Users/dmitrii/maincard/Blask
cp .env.example .env
nano .env  # или любой другой редактор
```

## ✅ Обязательные переменные

### Минимум одна из LLM провайдеров:

#### OpenAI (рекомендуется)
```env
OPENAI_API_KEY=sk-...
```
- Получить ключ: https://platform.openai.com/api-keys
- Нужна регистрация и пополнение баланса

#### ИЛИ Anthropic
```env
ANTHROPIC_API_KEY=sk-ant-...
```
- Получить ключ: https://console.anthropic.com/
- Альтернатива OpenAI

## 🔧 Опциональные переменные

### Поисковые API (для реального поиска)

#### SerpAPI (рекомендуется для поиска)
```env
SERPAPI_KEY=your_serpapi_key
```
- Получить: https://serpapi.com/
- Без этого будет использоваться mock поиск (для тестирования)

#### Google Custom Search
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_cse_id
```
- Получить: https://developers.google.com/custom-search
- Альтернатива SerpAPI

### LangSmith (для отладки и мониторинга)
```env
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=blask-project
```
- Получить: https://smith.langchain.com/
- Полезно для отладки и трейсинга запросов

### Настройки приложения
```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
ENVIRONMENT=development # development, production
```

## 📝 Минимальная конфигурация

Для быстрого старта достаточно:

```env
# .env файл
OPENAI_API_KEY=sk-your-key-here
```

## 🔒 Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитьте `.env` файл в git
- `.env` уже добавлен в `.gitignore`
- Не делитесь своими API ключами
- Используйте разные ключи для development и production

## 📋 Пример полного .env файла

```env
# LLM Provider (обязательно)
OPENAI_API_KEY=sk-proj-abc123...

# Поиск (опционально, но рекомендуется)
SERPAPI_KEY=abc123def456...

# Настройки
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 🚀 Проверка конфигурации

После создания `.env` файла, проверьте что переменные загружаются:

```python
from src.config import get_settings

settings = get_settings()
print(f"OpenAI key set: {settings.openai_api_key is not None}")
print(f"SerpAPI key set: {settings.serpapi_key is not None}")
```

## ❓ Что происходит без переменных?

- **Без LLM ключа**: Проект будет использовать mock режим (для тестирования)
- **Без поисковых API**: Будет использоваться mock поиск (для тестирования)
- **Без LangSmith**: Проект работает, но без трейсинга

## 🔗 Где получить ключи

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Anthropic**: https://console.anthropic.com/
3. **SerpAPI**: https://serpapi.com/
4. **Google Custom Search**: https://developers.google.com/custom-search
5. **LangSmith**: https://smith.langchain.com/
