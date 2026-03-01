# Архитектура системы Blask

## 🎯 Общая схема работы

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                                │
│         "Что в тренде в AI? Покажи статистику"              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              THINKING NODE (Думающая нода)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Анализ запроса через LLM                           │  │
│  │ 2. Определение типа: search/statistics/direct_answer │  │
│  │ 3. Формирование оптимизированного search_query       │  │
│  │ 4. Определение необходимости графиков                │  │
│  └──────────────────────────────────────────────────────┘  │
│  Output: decision, search_type, search_query, needs_charts │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│  SEARCH NODE  │              │  DIRECT PATH   │
│               │              │  (skip search) │
│ ┌───────────┐ │              └───────┬───────┘
│ │ Keywords  │ │                      │
│ │ Search    │ │                      │
│ └───────────┘ │                      │
│ ┌───────────┐ │                      │
│ │Competitors│ │                      │
│ │Analysis   │ │                      │
│ └───────────┘ │                      │
│ ┌───────────┐ │                      │
│ │ Trends    │ │                      │
│ │ Detection │ │                      │
│ └───────────┘ │                      │
└───────┬───────┘                      │
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           ANALYSIS NODE (Нода пост-анализа)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Обработка и структурирование данных               │  │
│  │ 2. Определение необходимости графиков                 │  │
│  │ 3. Создание визуализаций (matplotlib/plotly)         │  │
│  │ 4. Форматирование ответа через LLM                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  Output: processed_data, visualization, formatted_response │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                            │
│  • Текстовый ответ с анализом                               │
│  • Графики (если нужны)                                     │
│  • Структурированные данные                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Поток данных (Data Flow)

### State передача между нодами

```python
# Начальное состояние
GraphState {
    user_query: "Покажи тренды AI"
    decision: None
    search_results: []
    ...
}

# После Thinking Node
GraphState {
    user_query: "Покажи тренды AI"
    decision: "search"
    search_type: "trends"
    search_query: "AI trends 2024"
    needs_charts: True
    ...
}

# После Search Node
GraphState {
    ...
    search_results: [
        {"source": "Google Trends", "data": {...}},
        {"source": "Twitter", "data": {...}}
    ]
    raw_data: {...}
    ...
}

# После Analysis Node
GraphState {
    ...
    processed_data: "Анализ показывает..."
    visualization: "base64_image_or_path"
    charts_created: True
    ...
}
```

## 🧩 Компоненты системы

### 1. Thinking Node - Детальная схема

```
┌─────────────────────────────────────┐
│      Thinking Node                  │
├─────────────────────────────────────┤
│ Input: user_query, conversation_hist│
│                                     │
│ Process:                            │
│  1. LLM Analysis                    │
│     └─> Structured Output Parser    │
│  2. Decision Logic                  │
│     ├─> Type: search/statistics/... │
│     ├─> Search type: keywords/...   │
│     └─> Needs charts: true/false    │
│                                     │
│ Output: Updated State                │
└─────────────────────────────────────┘
```

### 2. Search Node - Инструменты

```
┌─────────────────────────────────────┐
│      Search Node                     │
├─────────────────────────────────────┤
│ Tools Available:                     │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ search_keywords(query)          │ │
│ │   └─> SerpAPI / Google Search   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ analyze_competitors(keyword)    │ │
│ │   └─> Competitor Analysis API   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ get_trends(topic, timeframe)    │ │
│ │   └─> Google Trends API         │ │
│ │   └─> Social Media APIs         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Output: search_results, raw_data    │
└─────────────────────────────────────┘
```

### 3. Analysis Node - Обработка

```
┌─────────────────────────────────────┐
│      Analysis Node                   │
├─────────────────────────────────────┤
│ Input: search_results, decision      │
│                                     │
│ Process:                            │
│  1. Data Parsing                    │
│     └─> Structure extraction        │
│                                     │
│  2. Chart Detection                 │
│     └─> LLM: "Does this need charts?"│
│                                     │
│  3. Visualization (if needed)       │
│     ├─> matplotlib (static)         │
│     └─> plotly (interactive)       │
│                                     │
│  4. Response Formatting             │
│     └─> LLM: Generate user-friendly│
│                                     │
│ Output: processed_data, visualization│
└─────────────────────────────────────┘
```

## 🔀 Условные переходы (Routing Logic)

### После Thinking Node

```python
def route_decision(state):
    if state["decision"] == "direct_answer":
        return "analysis_node"  # Пропустить поиск
    elif state["decision"] == "search":
        return "search_node"
    elif state["decision"] == "statistics":
        return "search_node"  # Сначала поиск данных
    else:
        return "analysis_node"  # Fallback
```

### После Search Node

```python
def route_after_search(state):
    # Всегда идем в анализ после поиска
    return "analysis_node"
```

## 📊 Примеры сценариев

### Сценарий 1: Простой поиск

```
User: "Что такое LangGraph?"
  ↓
Thinking: decision="direct_answer"
  ↓
Analysis: Формирует ответ из знаний LLM
  ↓
Response: Текстовый ответ
```

### Сценарий 2: Поиск с трендами

```
User: "Что в тренде в AI?"
  ↓
Thinking: decision="search", search_type="trends"
  ↓
Search: get_trends("AI")
  ↓
Analysis: Форматирует тренды
  ↓
Response: Список трендов
```

### Сценарий 3: Статистика с графиками

```
User: "Покажи статистику Python за год"
  ↓
Thinking: decision="statistics", needs_charts=True
  ↓
Search: search_keywords("Python statistics 2024")
  ↓
Analysis: 
  - Парсит данные
  - Создает график (line chart)
  - Форматирует ответ
  ↓
Response: Текст + График
```

## 🔧 Технические детали

### State Schema

```python
class GraphState(TypedDict):
    # Input
    user_query: str
    user_id: Optional[str]
    
    # Thinking Node Output
    decision: str
    search_query: Optional[str]
    search_type: Optional[str]
    needs_charts: bool
    
    # Search Node Output
    search_results: List[Dict]
    raw_data: Optional[Dict]
    
    # Analysis Node Output
    processed_data: Optional[str]
    visualization: Optional[str]
    charts_created: bool
    
    # Context
    conversation_history: List[Dict]
    execution_path: List[str]
    error: Optional[str]
```

### Error Handling

```
┌─────────────────┐
│   Any Node      │
│   Error Occurs  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Error Handler  │
│  ┌───────────┐  │
│  │ Log Error │  │
│  │ Set state │  │
│  │ .error    │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Fallback Path  │
│  or Retry       │
└─────────────────┘
```

## 🚀 Масштабирование

### Возможные улучшения

1. **Параллельный поиск**
   - Запуск нескольких поисковых инструментов одновременно
   - Агрегация результатов

2. **Кэширование**
   - Кэш результатов поиска
   - Кэш LLM ответов

3. **Memory/Context**
   - Сохранение истории разговора
   - Векторная БД для контекста

4. **Streaming**
   - Стриминг ответов
   - Прогрессивная загрузка данных

5. **Мультиагентность**
   - Отдельные агенты для разных типов поиска
   - Координация между агентами
