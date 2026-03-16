# Текущий статус интеграции с Google Trends

## ❌ Что НЕТ (ограничения)

### Нет настоящего Google Trends API

**Текущая реализация:**
- Используется `SearchBasedTrendAnalyzer`
- Делает **обычный поиск** через SerpAPI: `"{topic} trends {timeframe} latest"`
- Получает результаты обычного Google поиска, а не специальные данные Google Trends

**Что отсутствует:**
- ❌ **Interest over time** - график интереса по времени
- ❌ **Related queries** - связанные запросы
- ❌ **Rising queries** - растущие запросы
- ❌ **Regional interest** - региональный интерес
- ❌ **Comparison** - сравнение нескольких трендов
- ❌ **Category data** - данные по категориям

---

## ✅ Что ЕСТЬ (текущий функционал)

### 1. SerpAPI интеграция (частичная)

**Есть:**
- ✅ `SerpAPISearchTool` - для обычного Google поиска
- ✅ Использует `google-search-results` библиотеку
- ✅ Работает с `SERPAPI_KEY`

**Ограничения:**
- ❌ Использует только `engine="google"` (обычный поиск)
- ❌ НЕ использует `engine="google_trends"` (специальный Trends API)

### 2. Текущий Trend Analyzer

**Реализация:**
```python
# src/tools/trend_tools.py
class SearchBasedTrendAnalyzer(TrendAnalyzer):
    def get_trends(self, topic: str, timeframe: str = "30d"):
        # Делает обычный поиск
        search_query = f"{topic} trends {timeframe} latest"
        results = self.search_tool.search(search_query)  # Обычный поиск!
        
        # Возвращает результаты поиска, а не Trends данные
        return {
            "topic": topic,
            "timeframe": timeframe,
            "trends": trends,  # Просто результаты поиска
            "count": len(trends),
        }
```

**Что это дает:**
- ✅ Находит статьи о трендах
- ✅ Получает информацию из поиска
- ❌ НЕ дает структурированные данные Google Trends
- ❌ НЕ дает графики interest over time
- ❌ НЕ дает related queries

---

## 🔍 Детальное сравнение

### Текущая реализация (ограниченная):

```python
# Что происходит сейчас:
1. Запрос: "AI trends"
2. SearchBasedTrendAnalyzer делает: search("AI trends 30d latest")
3. Получает: обычные результаты поиска Google
4. Возвращает: список статей о трендах
```

**Результат:**
- Список статей/ссылок о трендах
- Нет структурированных данных
- Нет графиков
- Нет метрик интереса

### Настоящий Google Trends API (чего не хватает):

```python
# Что должно быть:
1. Запрос: "AI trends"
2. GoogleTrendsAPI делает: engine="google_trends", q="AI"
3. Получает:
   - interest_over_time: [{date, value}, ...]
   - related_queries: {rising: [...], top: [...]}
   - regional_interest: [{region, value}, ...]
4. Возвращает: структурированные данные о трендах
```

**Результат:**
- График interest over time
- Список связанных запросов
- Региональные данные
- Метрики интереса

---

## 📊 Что нужно добавить

### 1. Новый GoogleTrendsAnalyzer

Создать класс, который использует специальный Google Trends API через SerpAPI:

```python
class SerpAPIGoogleTrendsAnalyzer(TrendAnalyzer):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_trends(self, topic: str, timeframe: str = "30d"):
        # Использовать engine="google_trends" вместо "google"
        search = GoogleSearch({
            "engine": "google_trends",  # Специальный API!
            "q": topic,
            "api_key": self.api_key,
            "data_type": "TIMESERIES"  # или "RELATED_QUERIES"
        })
        
        results = search.get_dict()
        
        # Получить структурированные данные
        return {
            "interest_over_time": results.get("interest_over_time", []),
            "related_queries": results.get("related_queries", {}),
            "regional_interest": results.get("regional_interest", []),
            # и т.д.
        }
```

### 2. Обновить Search Node

Использовать новый `SerpAPIGoogleTrendsAnalyzer` вместо `SearchBasedTrendAnalyzer`.

---

## ✅ Итог

**Текущий статус:**
- ❌ **НЕТ** настоящего Google Trends API
- ✅ **ЕСТЬ** SerpAPI для обычного поиска
- ✅ **ЕСТЬ** базовая функциональность трендов (через поиск)
- ❌ **ОГРАНИЧЕНО** - только результаты поиска, не структурированные Trends данные

**Что нужно:**
- Добавить использование `engine="google_trends"` в SerpAPI
- Создать `SerpAPIGoogleTrendsAnalyzer`
- Обновить Search Node для использования нового анализатора

**Вывод:** Функционал **ограничен** - используется обычный поиск вместо специального Google Trends API.
