# План реализации AI-агентов для клонирования функционала Blask.com

## 🎯 Основная цель

Клонировать функционал [Blask.com](https://blask.com) с фокусом на:
- **Анализ ключевых слов конкурентов** - видеть что гуглят конкуренты
- **Автоматическое отслеживание конкурентов** - AI агенты для мониторинга
- **Автоматические отчеты** - генерация отчетов AI агентом
- **Умные алерты** - проактивные уведомления при изменениях

---

## 🤖 Архитектура с AI-агентами

### Новый граф с агентами:

```
START
  │
  ▼
┌─────────────────────┐
│  THINKING NODE      │ ◄─── Определяет тип запроса
│  (Enhanced)          │      - competitor_keyword_analysis
└────────┬────────────┘      - competitor_tracking
         │                   - report_generation
         │                   - alert_setup
         │
    ┌────┴────┬──────────┬──────────┬────────────┐
    │        │          │          │            │
    ▼        ▼          ▼          ▼            ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────┐
│ KEYWORD│ │COMPETITOR│ │  REPORT   │ │   ALERT    │ │  MARKET      │
│ ANALYZER│ │  TRACKER │ │ GENERATOR │ │   AGENT    │ │  ANALYZER    │
│  AGENT │ │  AGENT   │ │   AGENT   │ │            │ │   AGENT      │
└───┬────┘ └────┬─────┘ └─────┬────┘ └──────┬─────┘ └──────┬───────┘
    │           │              │             │              │
    └───────────┴──────────────┴─────────────┴──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ AGGREGATION NODE │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  STORAGE NODE   │ ◄─── Сохранение данных
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  ANALYSIS NODE  │
              └────────┬─────────┘
                       │
                       ▼
                      END
```

---

## 🆕 AI-агенты (LangGraph Agents)

### 1. **Keyword Analyzer Agent** (`src/agents/keyword_analyzer_agent.py`)

**Назначение:** Анализ ключевых слов, которые используют конкуренты

**Что делает агент:**
- Анализирует поисковые запросы конкурентов
- Определяет топ ключевые слова по конкурентам
- Сравнивает ключевые слова разных конкурентов
- Выявляет новые трендовые ключевые слова
- Анализирует сезонность ключевых слов

**Инструменты агента:**
- `CompetitorKeywordExtractor` - извлечение ключевых слов конкурентов
- `KeywordVolumeAnalyzer` - анализ объема поиска
- `KeywordTrendAnalyzer` - анализ трендов ключевых слов
- `KeywordComparator` - сравнение ключевых слов

**Пример работы:**
```python
# Агент получает задачу
task = {
    "competitor": "bet365.com",
    "country": "UK",
    "timeframe": "30d",
    "analysis_type": "top_keywords"
}

# Агент использует инструменты
1. Извлекает ключевые слова из поисковых запросов bet365
2. Анализирует объем поиска по каждому ключевому слову
3. Определяет тренды
4. Сравнивает с другими конкурентами

# Результат
{
    "competitor": "bet365.com",
    "top_keywords": [
        {"keyword": "bet365 login", "volume": 1000000, "trend": "stable"},
        {"keyword": "bet365 bonus", "volume": 500000, "trend": "rising"},
        {"keyword": "bet365 app", "volume": 300000, "trend": "rising"}
    ],
    "new_trending_keywords": ["bet365 crypto", "bet365 esports"],
    "competitor_comparison": {
        "betway": {"common_keywords": 15, "unique_keywords": 5},
        "william hill": {"common_keywords": 12, "unique_keywords": 8}
    }
}
```

**Реализация как LangGraph Agent:**
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class KeywordAnalyzerAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert keyword analyst for iGaming industry.
            Your task is to analyze what keywords competitors are using.
            Use the available tools to extract and analyze competitor keywords."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def analyze(self, competitor: str, country: str = None) -> Dict:
        result = self.agent.invoke({
            "input": f"Analyze keywords for competitor {competitor} in {country or 'global'}"
        })
        return result
```

---

### 2. **Competitor Tracker Agent** (`src/agents/competitor_tracker_agent.py`)

**Назначение:** Автоматическое отслеживание конкурентов и их активности

**Что делает агент:**
- Автоматически определяет конкурентов для бренда
- Мониторит их метрики (BAP, APS, CEB)
- Отслеживает изменения в их ключевых словах
- Обнаруживает новых конкурентов
- Анализирует их стратегию

**Инструменты агента:**
- `CompetitorIdentifier` - определение конкурентов
- `CompetitorMonitor` - мониторинг метрик
- `KeywordChangeDetector` - обнаружение изменений в ключевых словах
- `NewCompetitorDetector` - обнаружение новых конкурентов
- `StrategyAnalyzer` - анализ стратегии конкурентов

**Пример работы:**
```python
# Агент получает задачу
task = {
    "brand": "johnscasino.com",
    "country": "UK",
    "monitoring_frequency": "daily",
    "track_keywords": True
}

# Агент работает автономно
1. Определяет конкурентов для johnscasino.com
2. Мониторит их метрики каждый день
3. Отслеживает изменения в их ключевых словах
4. Обнаруживает новых конкурентов
5. Анализирует их стратегию

# Результат
{
    "brand": "johnscasino.com",
    "competitors": [
        {
            "name": "bet365.com",
            "bap": 0.35,
            "trend": "stable",
            "top_keywords": [...],
            "keyword_changes": {
                "new_keywords": ["bet365 crypto"],
                "dropped_keywords": ["bet365 old bonus"]
            }
        }
    ],
    "new_competitors": [
        {"name": "newcasino2024.com", "discovered": "2024-01-20"}
    ],
    "alerts": [
        {"type": "new_competitor", "competitor": "newcasino2024.com"}
    ]
}
```

**Реализация как LangGraph Agent:**
```python
class CompetitorTrackerAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a competitor tracking agent for iGaming.
            Your task is to continuously monitor competitors, their metrics, and keyword strategies.
            Use tools to identify competitors, track their metrics, and detect changes."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def track(self, brand: str, country: str = None) -> Dict:
        result = self.agent.invoke({
            "input": f"Track competitors for {brand} in {country or 'global'}"
        })
        return result
```

---

### 3. **Report Generator Agent** (`src/agents/report_generator_agent.py`)

**Назначение:** Автоматическая генерация отчетов с помощью AI

**Что делает агент:**
- Собирает данные из разных источников
- Анализирует данные с помощью LLM
- Генерирует структурированные отчеты
- Создает визуализации
- Форматирует отчеты для разных форматов (PDF, Excel, HTML)

**Типы отчетов:**
1. **Competitor Keyword Report** - отчет о ключевых словах конкурентов
2. **Brand Health Report** - здоровье бренда
3. **Competitive Analysis Report** - конкурентный анализ
4. **Market Opportunity Report** - возможности рынка
5. **Trends Report** - тренды индустрии

**Инструменты агента:**
- `DataCollector` - сбор данных
- `DataAnalyzer` - анализ данных с LLM
- `ReportBuilder` - построение отчета
- `VisualizationGenerator` - генерация графиков
- `PDFExporter` - экспорт в PDF
- `ExcelExporter` - экспорт в Excel

**Пример работы:**
```python
# Агент получает задачу
task = {
    "report_type": "competitor_keyword_report",
    "brand": "johnscasino.com",
    "competitors": ["bet365.com", "betway.com"],
    "timeframe": "30d",
    "format": "pdf"
}

# Агент работает
1. Собирает данные о ключевых словах конкурентов
2. Анализирует данные с помощью LLM
3. Генерирует структурированный отчет
4. Создает визуализации
5. Экспортирует в PDF

# Результат
{
    "report_id": "report_123",
    "report_type": "competitor_keyword_report",
    "sections": [
        {
            "title": "Top Keywords by Competitor",
            "content": "Analysis of top keywords...",
            "charts": [...]
        },
        {
            "title": "Keyword Trends",
            "content": "Trending keywords analysis...",
            "charts": [...]
        }
    ],
    "file_path": "/reports/report_123.pdf"
}
```

**Реализация как LangGraph Agent:**
```python
class ReportGeneratorAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert report generator for competitive intelligence.
            Your task is to collect data, analyze it, and generate comprehensive reports.
            Use tools to gather data, analyze with LLM, and create visualizations."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def generate(self, report_type: str, params: Dict) -> Dict:
        result = self.agent.invoke({
            "input": f"Generate {report_type} report with params: {params}"
        })
        return result
```

---

### 4. **Alert Agent** (`src/agents/alert_agent.py`)

**Назначение:** Умные алерты при критических изменениях

**Что делает агент:**
- Мониторит метрики и ключевые слова
- Определяет критические изменения
- Генерирует контекстуальные алерты
- Отправляет уведомления
- Обучается на основе обратной связи

**Типы алертов:**
1. **Keyword Change Alert** - изменение в ключевых словах конкурента
2. **New Competitor Alert** - обнаружение нового конкурента
3. **Metric Drop Alert** - падение метрики
4. **Trend Change Alert** - изменение тренда
5. **Opportunity Alert** - новая возможность

**Инструменты агента:**
- `ChangeDetector` - обнаружение изменений
- `AlertRuleEngine` - движок правил
- `ContextAnalyzer` - анализ контекста с LLM
- `NotificationSender` - отправка уведомлений

**Пример работы:**
```python
# Агент мониторит изменения
monitoring_data = {
    "brand": "johnscasino.com",
    "competitor": "bet365.com",
    "keyword_changes": {
        "new_keywords": ["bet365 crypto"],
        "dropped_keywords": ["bet365 old bonus"]
    },
    "metric_changes": {
        "bap": {"change": -0.05, "direction": "down"}
    }
}

# Агент анализирует
1. Определяет что изменения значительны
2. Анализирует контекст с LLM
3. Генерирует алерт
4. Отправляет уведомление

# Результат
{
    "alert_id": "alert_456",
    "type": "keyword_change",
    "severity": "medium",
    "message": "bet365.com started targeting 'bet365 crypto' keyword. This might indicate a shift towards crypto betting.",
    "recommendations": [
        "Consider adding crypto-related keywords to your strategy",
        "Monitor bet365's crypto betting features"
    ],
    "sent_at": "2024-01-20T10:00:00Z"
}
```

**Реализация как LangGraph Agent:**
```python
class AlertAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an alert agent for competitive intelligence.
            Your task is to monitor changes, analyze their significance, and generate contextual alerts.
            Use tools to detect changes, analyze context, and send notifications."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def monitor_and_alert(self, monitoring_data: Dict) -> Dict:
        result = self.agent.invoke({
            "input": f"Monitor and generate alerts for: {monitoring_data}"
        })
        return result
```

---

## 🛠️ Новые инструменты для агентов

### 1. **Keyword Analysis Tools** (`src/tools/keyword_tools.py`)

```python
from langchain.tools import tool
from typing import List, Dict

@tool
def extract_competitor_keywords(competitor_url: str, country: str = None) -> Dict:
    """Extract keywords that competitor is targeting."""
    # Использует SerpAPI для анализа поисковых запросов
    # Анализирует сайт конкурента
    # Извлекает ключевые слова из контента
    pass

@tool
def analyze_keyword_volume(keywords: List[str], country: str = None) -> Dict:
    """Analyze search volume for keywords."""
    # Использует Google Trends API
    # Анализирует объем поиска
    pass

@tool
def compare_competitor_keywords(competitor1: str, competitor2: str) -> Dict:
    """Compare keywords between two competitors."""
    # Сравнивает ключевые слова двух конкурентов
    # Находит общие и уникальные ключевые слова
    pass

@tool
def detect_keyword_trends(keywords: List[str], timeframe: str = "30d") -> Dict:
    """Detect trends in keywords."""
    # Анализирует тренды ключевых слов
    # Определяет растущие и падающие ключевые слова
    pass
```

### 2. **Competitor Tracking Tools** (`src/tools/competitor_tracking_tools.py`)

```python
@tool
def identify_competitors(brand: str, country: str = None) -> List[str]:
    """Identify competitors for a brand."""
    # Использует поиск для определения конкурентов
    # Анализирует похожие бренды
    pass

@tool
def monitor_competitor_metrics(competitor: str, metrics: List[str]) -> Dict:
    """Monitor metrics for a competitor."""
    # Мониторит BAP, APS, CEB для конкурента
    pass

@tool
def detect_keyword_changes(competitor: str, previous_keywords: List[str]) -> Dict:
    """Detect changes in competitor keywords."""
    # Сравнивает текущие и предыдущие ключевые слова
    # Обнаруживает новые и удаленные ключевые слова
    pass

@tool
def discover_new_competitors(country: str, timeframe: str = "30d") -> List[Dict]:
    """Discover new competitors in the market."""
    # Обнаруживает новых конкурентов
    # Анализирует их ключевые слова
    pass
```

### 3. **Report Generation Tools** (`src/tools/report_tools.py`)

```python
@tool
def collect_report_data(report_type: str, params: Dict) -> Dict:
    """Collect data for report generation."""
    # Собирает данные из разных источников
    pass

@tool
def analyze_data_with_llm(data: Dict, analysis_type: str) -> str:
    """Analyze data using LLM."""
    # Использует LLM для анализа данных
    # Генерирует инсайты
    pass

@tool
def generate_visualization(data: Dict, chart_type: str) -> str:
    """Generate visualization for report."""
    # Создает графики и визуализации
    pass

@tool
def export_report(report_data: Dict, format: str) -> str:
    """Export report to specified format."""
    # Экспортирует отчет в PDF, Excel, HTML
    pass
```

---

## 📊 Расширенный GraphState

```python
class GraphState(TypedDict):
    # ... существующие поля ...
    
    # Keyword Analysis
    competitor_keywords: Dict[str, List[str]]  # competitor -> keywords
    keyword_analysis: Optional[Dict[str, Any]]
    keyword_trends: Optional[Dict[str, Any]]
    
    # Competitor Tracking
    tracked_competitors: List[Dict[str, Any]]
    competitor_changes: List[Dict[str, Any]]
    new_competitors: List[Dict[str, Any]]
    
    # Reports
    report_type: Optional[str]
    report_data: Optional[Dict[str, Any]]
    report_generated: bool
    report_file_path: Optional[str]
    
    # Alerts
    alerts_generated: List[Dict[str, Any]]
    alert_rules: Optional[Dict[str, Any]]
    
    # Agent execution
    agent_execution_path: List[str]
    agent_decisions: List[Dict[str, Any]]
```

---

## 🔄 Новые ноды с агентами

### 1. **Competitor Keyword Analysis Node** (`src/nodes/keyword_analysis_node.py`)

```python
def keyword_analysis_node(state: GraphState) -> GraphState:
    """
    Node that uses Keyword Analyzer Agent to analyze competitor keywords.
    """
    from ..agents.keyword_analyzer_agent import KeywordAnalyzerAgent
    from ..config import get_settings
    
    settings = get_settings()
    llm = ChatOpenAI(model=settings.default_model, temperature=0)
    
    # Create tools
    tools = [
        extract_competitor_keywords,
        analyze_keyword_volume,
        compare_competitor_keywords,
        detect_keyword_trends
    ]
    
    # Create agent
    agent = KeywordAnalyzerAgent(llm, tools)
    
    # Get competitor from state
    competitor = state.get("search_query")  # или из другого поля
    
    # Run agent
    result = agent.analyze(competitor, state.get("country"))
    
    # Update state
    state["competitor_keywords"] = result.get("top_keywords", [])
    state["keyword_analysis"] = result
    state["execution_path"].append("keyword_analysis_node")
    
    return state
```

### 2. **Competitor Tracker Node** (`src/nodes/competitor_tracker_node.py`)

```python
def competitor_tracker_node(state: GraphState) -> GraphState:
    """
    Node that uses Competitor Tracker Agent to track competitors.
    """
    from ..agents.competitor_tracker_agent import CompetitorTrackerAgent
    from ..config import get_settings
    
    settings = get_settings()
    llm = ChatOpenAI(model=settings.default_model, temperature=0)
    
    # Create tools
    tools = [
        identify_competitors,
        monitor_competitor_metrics,
        detect_keyword_changes,
        discover_new_competitors
    ]
    
    # Create agent
    agent = CompetitorTrackerAgent(llm, tools)
    
    # Get brand from state
    brand = state.get("brand_name") or state.get("search_query")
    
    # Run agent
    result = agent.track(brand, state.get("country"))
    
    # Update state
    state["tracked_competitors"] = result.get("competitors", [])
    state["new_competitors"] = result.get("new_competitors", [])
    state["execution_path"].append("competitor_tracker_node")
    
    return state
```

### 3. **Report Generator Node** (`src/nodes/report_generator_node.py`)

```python
def report_generator_node(state: GraphState) -> GraphState:
    """
    Node that uses Report Generator Agent to generate reports.
    """
    from ..agents.report_generator_agent import ReportGeneratorAgent
    from ..config import get_settings
    
    settings = get_settings()
    llm = ChatOpenAI(model=settings.default_model, temperature=0.3)  # Higher temp for creativity
    
    # Create tools
    tools = [
        collect_report_data,
        analyze_data_with_llm,
        generate_visualization,
        export_report
    ]
    
    # Create agent
    agent = ReportGeneratorAgent(llm, tools)
    
    # Get report params from state
    report_type = state.get("report_type", "competitor_keyword_report")
    params = {
        "brand": state.get("brand_name"),
        "competitors": state.get("tracked_competitors", []),
        "timeframe": state.get("timeframe", "30d")
    }
    
    # Run agent
    result = agent.generate(report_type, params)
    
    # Update state
    state["report_data"] = result
    state["report_generated"] = True
    state["report_file_path"] = result.get("file_path")
    state["execution_path"].append("report_generator_node")
    
    return state
```

### 4. **Alert Node** (`src/nodes/alert_node.py`)

```python
def alert_node(state: GraphState) -> GraphState:
    """
    Node that uses Alert Agent to generate alerts.
    """
    from ..agents.alert_agent import AlertAgent
    from ..config import get_settings
    
    settings = get_settings()
    llm = ChatOpenAI(model=settings.default_model, temperature=0)
    
    # Create tools
    tools = [
        detect_keyword_changes,
        monitor_competitor_metrics,
        # ... другие инструменты
    ]
    
    # Create agent
    agent = AlertAgent(llm, tools)
    
    # Prepare monitoring data
    monitoring_data = {
        "brand": state.get("brand_name"),
        "competitors": state.get("tracked_competitors", []),
        "keyword_changes": state.get("keyword_analysis", {}),
        "metric_changes": state.get("competitor_changes", [])
    }
    
    # Run agent
    result = agent.monitor_and_alert(monitoring_data)
    
    # Update state
    if result.get("alerts"):
        state["alerts_generated"] = result["alerts"]
    state["execution_path"].append("alert_node")
    
    return state
```

---

## 🔄 Обновленная маршрутизация

```python
def route_after_thinking(state: GraphState) -> str:
    """Route to appropriate node based on decision."""
    decision = state.get("decision")
    search_type = state.get("search_type")
    
    # Новые типы решений для агентов
    if decision == "competitor_keyword_analysis":
        return "keyword_analysis_node"
    elif decision == "competitor_tracking":
        return "competitor_tracker_node"
    elif decision == "report_generation":
        return "report_generator_node"
    elif decision == "alert_setup":
        return "alert_node"
    elif decision == "search":
        return "search_node"
    else:
        return "analysis_node"
```

---

## 📋 План реализации

### Фаза 1: Keyword Analysis Tools (1-2 недели)
- [ ] Создать инструменты для анализа ключевых слов
- [ ] Интеграция с SerpAPI для извлечения ключевых слов
- [ ] Интеграция с Google Trends для анализа объема
- [ ] Тесты инструментов

### Фаза 2: Keyword Analyzer Agent (1-2 недели)
- [ ] Создать Keyword Analyzer Agent
- [ ] Интегрировать инструменты
- [ ] Создать ноду keyword_analysis_node
- [ ] Тесты агента

### Фаза 3: Competitor Tracker Agent (2-3 недели)
- [ ] Создать инструменты для отслеживания конкурентов
- [ ] Создать Competitor Tracker Agent
- [ ] Создать ноду competitor_tracker_node
- [ ] Автоматизация мониторинга
- [ ] Тесты агента

### Фаза 4: Report Generator Agent (2-3 недели)
- [ ] Создать инструменты для генерации отчетов
- [ ] Создать Report Generator Agent
- [ ] Создать ноду report_generator_node
- [ ] Экспорт в PDF/Excel
- [ ] Тесты агента

### Фаза 5: Alert Agent (1-2 недели)
- [ ] Создать инструменты для алертов
- [ ] Создать Alert Agent
- [ ] Создать ноду alert_node
- [ ] Интеграция с уведомлениями
- [ ] Тесты агента

### Фаза 6: Интеграция и тестирование (1-2 недели)
- [ ] Интеграция всех агентов в граф
- [ ] Обновление маршрутизации
- [ ] End-to-end тесты
- [ ] Оптимизация производительности

---

## 🎯 Ключевые особенности

1. **AI-агенты** - каждый агент автономно принимает решения
2. **Анализ ключевых слов** - фокус на том, что гуглят конкуренты
3. **Автоматизация** - агенты работают автономно
4. **Контекстуальные алерты** - умные уведомления с рекомендациями
5. **Автоматические отчеты** - генерация отчетов AI агентом

---

## 📝 Заключение

Этот план превращает Blask в полноценную competitive intelligence платформу с AI-агентами, которая:
- Анализирует ключевые слова конкурентов
- Автоматически отслеживает конкурентов
- Генерирует отчеты с помощью AI
- Отправляет умные алерты

Реализация займет примерно 8-12 недель при работе одного разработчика, или 4-6 недель при работе команды из 2-3 человек.
