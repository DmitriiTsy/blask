# План разработки LangGraph приложения с нодами для анализа трендов и конкурентов

## 📋 Обзор проекта

Система на базе LangGraph для анализа трендов, конкурентов и статистики с использованием:
- **Думающей ноды** для принятия решений и формирования запросов
- **Ноды поиска** для работы с ключевыми словами и конкурентами
- **Ноды пост-анализа** для форматирования и визуализации данных

---

## 🏗️ Архитектура системы

### 1. Структура графа (Graph Structure)

```
┌─────────────────┐
│  START (Entry)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  THINKING NODE      │ ◄─── Думающая нода
│  (Decision Maker)   │      - Анализ запроса
└────────┬────────────┘      - Формирование стратегии
         │                    - Выбор маршрута
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ SEARCH  │ │ DIRECT  │
│  NODE   │ │ ANSWER  │
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘
           │
           ▼
┌─────────────────────┐
│  ANALYSIS NODE      │ ◄─── Нода анализа
│  (Post-processing)  │      - Обработка данных
└────────┬────────────┘      - Форматирование
         │                    - Создание графиков
         │
         ▼
┌─────────────────┐
│  END (Response)  │
└─────────────────┘
```

### 2. Определение State (Состояние графа)

```python
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # Входные данные
    user_query: str
    user_id: Optional[str]
    
    # Результаты думающей ноды
    decision: str  # "search", "direct_answer", "statistics"
    search_query: Optional[str]
    search_type: Optional[str]  # "keywords", "competitors", "trends"
    
    # Результаты поиска
    search_results: List[Dict[str, Any]]
    raw_data: Optional[Dict[str, Any]]
    
    # Результаты анализа
    processed_data: Optional[str]
    visualization: Optional[str]  # Base64 encoded image или путь к файлу
    charts_created: bool
    
    # Контекст и история
    conversation_history: List[Dict[str, str]]
    error: Optional[str]
    
    # Метаданные
    execution_path: List[str]  # Для трейсинга
```

---

## 🔧 Компоненты системы

### 1. Думающая нода (Thinking Node)

**Назначение:**
- Анализирует пользовательский запрос
- Определяет тип задачи (поиск, статистика, прямой ответ)
- Формирует оптимизированные запросы для поиска
- Выбирает маршрут выполнения

**Реализация:**
```python
def thinking_node(state: GraphState) -> GraphState:
    """
    Анализирует запрос и принимает решение о дальнейшем маршруте
    """
    # Использует LLM для анализа запроса
    # Определяет: нужен ли поиск, какой тип поиска, нужна ли статистика
    # Формирует оптимизированный search_query
    pass
```

**Инструменты:**
- `langchain.chat_models` для LLM
- `langchain.prompts` для промптов анализа
- `langchain.output_parsers` для структурированного вывода

### 2. Нода поиска (Search Node)

**Назначение:**
- Поиск по ключевым словам
- Анализ конкурентов
- Выявление трендов
- Сбор данных из различных источников

**Реализация:**
```python
def search_node(state: GraphState) -> GraphState:
    """
    Выполняет поиск по ключевым словам и конкурентам
    """
    # Интеграция с поисковыми API
    # Поиск по ключевым словам
    # Анализ конкурентов
    # Сбор данных о трендах
    pass
```

**Инструменты:**
- `langchain.tools` для интеграции с внешними API
- `langchain.utilities` для поисковых утилит (SerpAPI, Google Search)
- `langchain.retrievers` для RAG (если есть база знаний)
- Custom tools для специализированных источников

**Источники данных:**
- Google Trends API
- SerpAPI / Google Custom Search
- Специализированные API конкурентов (если доступны)
- Социальные сети (Twitter, Reddit) для трендов

### 3. Нода пост-анализа (Analysis Node)

**Назначение:**
- Обработка и структурирование данных
- Форматирование в удобный для пользователя вид
- Создание графиков для статистических данных
- Генерация финального ответа

**Реализация:**
```python
def analysis_node(state: GraphState) -> GraphState:
    """
    Обрабатывает данные и создает визуализации
    """
    # Парсинг и структурирование данных
    # Определение необходимости графиков
    # Создание графиков (matplotlib/plotly)
    # Форматирование ответа
    pass
```

**Инструменты:**
- `matplotlib` / `plotly` для графиков
- `pandas` для обработки данных
- `langchain.output_parsers` для структурирования
- LLM для генерации текстового ответа

---

## 📦 Технический стек

### Основные зависимости

```txt
# Core LangChain/LangGraph
langchain>=0.1.0
langgraph>=0.0.20
langchain-core>=0.1.0
langchain-openai>=0.0.5  # или langchain-anthropic
langchain-community>=0.0.20

# LLM Providers (выбрать один или несколько)
openai>=1.0.0
anthropic>=0.7.0

# Поиск и данные
google-search-results>=2.4.2  # SerpAPI
requests>=2.31.0
beautifulsoup4>=4.12.0

# Обработка данных и визуализация
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.17.0
pillow>=10.0.0

# Утилиты
python-dotenv>=1.0.0
pydantic>=2.0.0
typing-extensions>=4.8.0
```

### Структура проекта

```
Blask/
├── src/
│   ├── __init__.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py           # Определение GraphState
│   │   ├── graph.py            # Основной граф
│   │   └── edges.py            # Условные переходы
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── thinking_node.py    # Думающая нода
│   │   ├── search_node.py      # Нода поиска
│   │   └── analysis_node.py    # Нода анализа
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tools.py     # Инструменты поиска
│   │   ├── competitor_tools.py # Инструменты конкурентов
│   │   └── trend_tools.py      # Инструменты трендов
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── visualization.py    # Создание графиков
│   │   └── formatters.py       # Форматирование данных
│   └── config/
│       ├── __init__.py
│       └── settings.py         # Конфигурация
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   └── test_graph.py
├── .env.example
├── requirements.txt
├── README.md
└── PLAN.md
```

---

## 🚀 Этапы разработки

### Этап 1: Базовая инфраструктура (Week 1)

**Задачи:**
1. ✅ Настройка окружения и зависимостей
2. ✅ Определение структуры State
3. ✅ Создание базовой структуры графа
4. ✅ Реализация простой думающей ноды
5. ✅ Настройка условных переходов (conditional edges)

**Результат:**
- Работающий граф с базовой логикой маршрутизации
- Тесты для проверки flow

### Этап 2: Интеграция поиска (Week 2)

**Задачи:**
1. ✅ Реализация ноды поиска
2. ✅ Интеграция с поисковыми API (SerpAPI, Google Search)
3. ✅ Создание tools для поиска по ключевым словам
4. ✅ Создание tools для анализа конкурентов
5. ✅ Обработка ошибок и fallback механизмы

**Результат:**
- Функциональный поиск по ключевым словам
- Базовый анализ конкурентов

### Этап 3: Анализ трендов (Week 2-3)

**Задачи:**
1. ✅ Интеграция с Google Trends API
2. ✅ Анализ социальных сетей для трендов
3. ✅ Улучшение думающей ноды для определения трендов
4. ✅ Агрегация данных из разных источников

**Результат:**
- Система выявления трендов
- Агрегированные данные из множества источников

### Этап 4: Пост-анализ и визуализация (Week 3-4)

**Задачи:**
1. ✅ Реализация ноды анализа
2. ✅ Создание модуля визуализации (графики)
3. ✅ Определение когда нужны графики (LLM-based)
4. ✅ Форматирование ответов для пользователя
5. ✅ Обработка статистических запросов

**Результат:**
- Автоматическое создание графиков
- Форматированные ответы

### Этап 5: Оптимизация и улучшения (Week 4+)

**Задачи:**
1. ✅ Добавление памяти (memory) для контекста
2. ✅ Улучшение промптов
3. ✅ Обработка edge cases
4. ✅ Добавление логирования и трейсинга (LangSmith)
5. ✅ Оптимизация производительности
6. ✅ Добавление асинхронности где возможно

**Результат:**
- Production-ready система
- Мониторинг и логирование

---

## 🎯 Детальная реализация компонентов

### 1. Думающая нода - Детали

**Промпт для анализа:**
```python
THINKING_PROMPT = """
Ты - эксперт по анализу запросов. Твоя задача:
1. Определить тип запроса:
   - "search" - нужен поиск информации
   - "direct_answer" - можно ответить напрямую
   - "statistics" - нужна статистика и графики

2. Если нужен поиск, определи:
   - Тип поиска: "keywords", "competitors", "trends"
   - Оптимизированный поисковый запрос

3. Определи, нужны ли графики (для статистики)

Запрос пользователя: {user_query}
История разговора: {conversation_history}

Ответь в формате JSON:
{{
    "decision": "search|direct_answer|statistics",
    "search_type": "keywords|competitors|trends|null",
    "search_query": "оптимизированный запрос или null",
    "needs_charts": true/false,
    "reasoning": "объяснение решения"
}}
"""
```

**Логика:**
- Использует LLM для анализа
- Парсит структурированный ответ
- Обновляет state с решением
- Возвращает state для условного перехода

### 2. Нода поиска - Детали

**Инструменты:**
```python
# Поиск по ключевым словам
@tool
def search_keywords(query: str) -> str:
    """Поиск информации по ключевым словам"""
    # Использует SerpAPI или Google Custom Search
    pass

# Анализ конкурентов
@tool
def analyze_competitors(keyword: str) -> str:
    """Анализ конкурентов по ключевому слову"""
    # Поиск конкурентов, анализ их стратегий
    pass

# Тренды
@tool
def get_trends(topic: str, timeframe: str = "30d") -> str:
    """Получение трендов по теме"""
    # Google Trends API, социальные сети
    pass
```

**Логика:**
- Получает search_query и search_type из state
- Вызывает соответствующий tool
- Сохраняет результаты в state.search_results
- Обрабатывает ошибки

### 3. Нода анализа - Детали

**Определение необходимости графиков:**
```python
def should_create_charts(state: GraphState) -> bool:
    """Определяет, нужны ли графики на основе данных"""
    # Проверяет state.decision == "statistics"
    # Анализирует структуру данных
    # Использует LLM для определения
    pass
```

**Создание графиков:**
```python
def create_visualization(data: Dict, chart_type: str) -> str:
    """Создает график и возвращает base64 или путь"""
    # Определяет тип графика (line, bar, pie)
    # Использует matplotlib/plotly
    # Сохраняет и возвращает путь или base64
    pass
```

**Форматирование:**
```python
def format_response(state: GraphState) -> str:
    """Форматирует финальный ответ для пользователя"""
    # Использует LLM для генерации читаемого ответа
    # Включает графики если есть
    # Структурирует данные
    pass
```

---

## 🔄 Условные переходы (Conditional Edges)

```python
def route_after_thinking(state: GraphState) -> str:
    """Определяет следующий узел после думающей ноды"""
    decision = state.get("decision")
    
    if decision == "direct_answer":
        return "analysis_node"  # Пропускаем поиск
    elif decision == "search":
        return "search_node"
    elif decision == "statistics":
        return "search_node"  # Сначала поиск, потом анализ
    else:
        return "analysis_node"  # Fallback

def route_after_search(state: GraphState) -> str:
    """Определяет следующий узел после поиска"""
    # Всегда идем в анализ
    return "analysis_node"
```

---

## 📊 Примеры использования

### Пример 1: Поиск по ключевым словам
```
Пользователь: "Что сейчас в тренде в области AI?"
→ Thinking Node: decision="search", search_type="trends", search_query="AI trends 2024"
→ Search Node: получает тренды
→ Analysis Node: форматирует и возвращает ответ
```

### Пример 2: Статистика с графиками
```
Пользователь: "Покажи статистику использования Python за последний год"
→ Thinking Node: decision="statistics", needs_charts=True
→ Search Node: собирает статистику
→ Analysis Node: создает график, форматирует ответ
```

### Пример 3: Анализ конкурентов
```
Пользователь: "Кто мои конкуренты в области e-commerce?"
→ Thinking Node: decision="search", search_type="competitors"
→ Search Node: анализирует конкурентов
→ Analysis Node: структурирует список конкурентов
```

---

## 🧪 Тестирование

### Unit тесты
- Тестирование каждой ноды отдельно
- Тестирование tools
- Тестирование форматирования

### Integration тесты
- Тестирование полного flow графа
- Тестирование условных переходов
- Тестирование обработки ошибок

### E2E тесты
- Тестирование реальных сценариев
- Проверка качества ответов
- Проверка визуализаций

---

## 📈 Мониторинг и отладка

### LangSmith Integration
```python
# Настройка трейсинга
from langsmith import traceable

@traceable
def thinking_node(state: GraphState):
    # Автоматический трейсинг
    pass
```

### Логирование
- Логирование всех переходов между нодами
- Логирование решений думающей ноды
- Логирование ошибок и fallback'ов

---

## 🔐 Безопасность и конфигурация

### Environment Variables
```env
# LLM
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Поиск
SERPAPI_KEY=your_key
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_id

# Опционально
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=your_project
```

### Best Practices
- Никогда не коммитить API ключи
- Использовать .env файлы
- Валидация входных данных
- Обработка rate limits
- Кэширование где возможно

---

## 🎓 Дополнительные улучшения (Future)

1. **Память (Memory)**
   - Сохранение контекста между сессиями
   - Использование векторных БД для истории

2. **Мультиагентность**
   - Отдельные агенты для разных типов поиска
   - Координация между агентами

3. **Streaming**
   - Стриминг ответов пользователю
   - Прогрессивная загрузка данных

4. **Кэширование**
   - Кэширование результатов поиска
   - Кэширование LLM ответов

5. **Веб-интерфейс**
   - FastAPI для API
   - Streamlit/Gradio для UI

---

## ✅ Чеклист готовности

- [ ] Базовая структура проекта
- [ ] Определение State
- [ ] Реализация всех нод
- [ ] Условные переходы
- [ ] Интеграция с поисковыми API
- [ ] Создание графиков
- [ ] Форматирование ответов
- [ ] Обработка ошибок
- [ ] Тесты
- [ ] Документация
- [ ] Конфигурация
- [ ] Деплой

---

## 📚 Полезные ресурсы

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Tutorials](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Best Practices Guide](https://langchain-ai.github.io/langgraph/how-tos/)

---

**Дата создания:** 2024
**Версия плана:** 1.0
