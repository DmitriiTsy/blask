# Полное руководство по API ключам

## 🔑 Обязательные ключи

### 1. LLM провайдер (минимум один)

#### OpenAI (рекомендуется)
```env
OPENAI_API_KEY=sk-...
```
- **Для чего**: Анализ запросов, принятие решений, форматирование ответов
- **Где получить**: https://platform.openai.com/api-keys
- **Стоимость**: Платно, но есть бесплатный кредит при регистрации
- **Обязательно**: Да (или Anthropic)

#### ИЛИ Anthropic
```env
ANTHROPIC_API_KEY=sk-ant-...
```
- **Для чего**: Альтернатива OpenAI для LLM
- **Где получить**: https://console.anthropic.com/
- **Стоимость**: Платно
- **Обязательно**: Да (или OpenAI)

---

## 🔍 Ключи для поиска и трендов

### 2. SerpAPI (РЕКОМЕНДУЕТСЯ для Google Trends и поиска)

```env
SERPAPI_KEY=your_serpapi_key
```

**Для чего:**
- ✅ **Google Trends** - получение данных о трендах через [Google Trends API от SerpAPI](https://serpapi.com/google-trends-api)
- ✅ **Поиск по ключевым словам** - обычный Google поиск
- ✅ **Анализ конкурентов** - поиск конкурентов

**Где получить**: https://serpapi.com/users/sign_in

**Стоимость**: 
- Бесплатный план: 100 запросов/месяц
- Платные планы от $50/месяц

**Важно**: 
- SerpAPI предоставляет **специальный Google Trends API**, который дает:
  - Interest over time (интерес по времени)
  - Related queries (связанные запросы)
  - Regional interest (региональный интерес)
  - См. документацию: https://docs.langchain.com/oss/javascript/integrations/tools/google_trends

**Текущая реализация**: 
- Сейчас используется `SearchBasedTrendAnalyzer`, который делает обычный поиск
- Можно улучшить, добавив прямой Google Trends API через SerpAPI

---

### 3. Google Custom Search (альтернатива SerpAPI)

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_cse_id
```

**Для чего:**
- Поиск по ключевым словам
- НО: **НЕ дает Google Trends данные** (только обычный поиск)

**Где получить**: 
1. API ключ: https://console.cloud.google.com/apis/credentials
2. CSE ID: https://programmablesearchengine.google.com/

**Стоимость**: 
- 100 бесплатных запросов/день
- Потом платно

**Ограничения**: 
- ❌ Нет доступа к Google Trends API
- Только обычный поиск

---

## 📊 Сравнение для Google Trends

| API | Google Trends | Поиск | Стоимость |
|-----|--------------|-------|-----------|
| **SerpAPI** | ✅ Да (специальный API) | ✅ Да | От $50/мес |
| **Google Custom Search** | ❌ Нет | ✅ Да | 100 бесплатно/день |

**Вывод**: Для **Google Trends** нужен именно **SerpAPI**, так как Google Custom Search не предоставляет Trends API.

---

## 🛠️ Опциональные ключи

### 4. LangSmith (для отладки)

```env
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=blask-project
```

**Для чего**: 
- Трейсинг запросов
- Мониторинг производительности
- Отладка

**Где получить**: https://smith.langchain.com/
**Обязательно**: Нет

---

## 📋 Минимальная конфигурация

### Для базовой работы (без реального поиска):
```env
OPENAI_API_KEY=sk-...
```

### Для работы с Google Trends и поиском:
```env
OPENAI_API_KEY=sk-...
SERPAPI_KEY=your_serpapi_key
```

---

## 🎯 Что нужно для вашего случая

### Для получения Google Trends данных:

**Обязательно:**
1. `OPENAI_API_KEY` - для LLM
2. `SERPAPI_KEY` - для Google Trends API

**Почему SerpAPI:**
- Google Trends API от SerpAPI дает специальные данные о трендах
- Включает interest over time, related queries, regional data
- Google Custom Search НЕ предоставляет Trends API

### Текущая проблема:

Сейчас в коде используется `SearchBasedTrendAnalyzer`, который делает обычный поиск вместо использования специального Google Trends API. 

**Решение**: Можно улучшить, добавив прямой вызов Google Trends API через SerpAPI (как в документации LangChain).

---

## 🔧 Рекомендации

1. **Минимум для работы**: `OPENAI_API_KEY`
2. **Для реального поиска**: `SERPAPI_KEY` 
3. **Для Google Trends**: `SERPAPI_KEY` (обязательно!)
4. **Google Custom Search**: Только если нужен обычный поиск без Trends

---

## 💡 План улучшения

Чтобы использовать настоящий Google Trends API:

1. Добавить `SerpAPIGoogleTrendsTool` (как в LangChain docs)
2. Использовать его вместо `SearchBasedTrendAnalyzer`
3. Это даст реальные данные о трендах, а не просто результаты поиска
