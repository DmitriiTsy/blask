# План реализации AI-агентов для анализа онлайн-казино конкурентов

## 🎯 Фокус проекта

**Узкий спектр:** Анализ конкурентов в индустрии онлайн-казино (iGaming)

**Основная цель:** 
- Автоматически определять конкурентов (бренды, которые предлагают онлайн-казино)
- Мониторить их метрики и ключевые слова
- Генерировать автоматические отчеты с помощью AI

**Примечание:** Анализ ключевых слов уже реализован через `search_node` и `competitor_tools`.

---

## 🤖 Два основных AI-агента

### 1. **Competitor Tracker Agent** (LangChain Agent)
### 2. **Report Generator Agent** (LangChain Agent)

---

## 🏗️ Архитектура с LangChain

```
START
  │
  ▼
┌─────────────────────┐
│  THINKING NODE      │ ◄─── Определяет тип запроса
│  (Enhanced)         │      - competitor_tracking
└────────┬────────────┘      - report_generation
         │
    ┌────┴────┐
    │        │
    ▼        ▼
┌──────────┐ ┌────────────┐
│COMPETITOR│ │   REPORT    │
│  TRACKER │ │  GENERATOR  │
│  AGENT   │ │    AGENT    │
│          │ │             │
└────┬─────┘ └──────┬──────┘
     │              │
     └──────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ AGGREGATION   │
    │     NODE      │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │  STORAGE NODE │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ ANALYSIS NODE │
    └───────┬───────┘
            │
            ▼
           END
```

---

## 1️⃣ Competitor Tracker Agent

### Назначение
Автоматически определяет и отслеживает конкурентов в индустрии онлайн-казино.

### Что делает агент:
1. **Определяет конкурентов** - находит бренды, которые предлагают онлайн-казино
2. **Мониторит их метрики** - отслеживает BAP, APS, CEB, поисковый объем
3. **Анализирует ключевые слова** - использует существующий функционал
4. **Отслеживает изменения** - обнаруживает изменения в стратегии
5. **Обнаруживает новых конкурентов** - находит новые бренды на рынке

### Реализация с LangChain

#### Структура файлов:
```
src/
├── agents/
│   ├── __init__.py
│   └── competitor_tracker_agent.py
├── tools/
│   ├── competitor_tracking_tools.py  # Новые инструменты
│   └── ... (существующие)
└── nodes/
    └── competitor_tracker_node.py  # Новая нода
```

#### Инструменты для агента (`src/tools/competitor_tracking_tools.py`):

```python
"""Tools for competitor tracking in iGaming industry."""

from langchain.tools import tool
from typing import List, Dict, Any, Optional
from ..tools.search_tools import SearchTool
from ..tools.competitor_tools import CompetitorAnalyzer
from ..utils.logging import get_logger

logger = get_logger(__name__)


@tool
def identify_igaming_competitors(
    brand_name: str, 
    country: Optional[str] = None
) -> Dict[str, Any]:
    """
    Identify competitors in online casino industry for a given brand.
    
    Focuses specifically on iGaming/online casino brands.
    
    Args:
        brand_name: Name of the brand to find competitors for
        country: Optional country code for localized search
    
    Returns:
        Dictionary with list of competitors and their basic info
    """
    # Используем существующий SearchTool
    from ..config import get_settings
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool
    
    settings = get_settings()
    
    if settings.serpapi_key:
        search_tool = SerpAPISearchTool(settings.serpapi_key)
    else:
        search_tool = MockSearchTool()
    
    # Поиск конкурентов в iGaming
    queries = [
        f"{brand_name} online casino competitors",
        f"best online casino like {brand_name}",
        f"{brand_name} alternative casino sites",
    ]
    
    if country:
        queries.append(f"{brand_name} casino competitors {country}")
    
    all_competitors = []
    seen_domains = set()
    
    for query in queries:
        results = search_tool.search(query)
        
        for result in results:
            link = result.get("link", "")
            # Извлекаем домен
            domain = link.split("/")[2] if "/" in link else link
            
            # Фильтруем только онлайн-казино (проверяем по ключевым словам)
            title_lower = result.get("title", "").lower()
            snippet_lower = result.get("snippet", "").lower()
            
            casino_keywords = ["casino", "bet", "gambling", "poker", "slot", "jackpot"]
            is_casino = any(keyword in title_lower or keyword in snippet_lower 
                          for keyword in casino_keywords)
            
            if is_casino and domain not in seen_domains:
                seen_domains.add(domain)
                all_competitors.append({
                    "name": result.get("title", domain),
                    "domain": domain,
                    "url": link,
                    "description": result.get("snippet", ""),
                    "source": "search"
                })
    
    logger.info(f"Found {len(all_competitors)} iGaming competitors for {brand_name}")
    
    return {
        "brand": brand_name,
        "country": country,
        "competitors": all_competitors[:20],  # Top 20
        "count": len(all_competitors)
    }


@tool
def monitor_competitor_keywords(
    competitor_domain: str,
    timeframe: str = "30d"
) -> Dict[str, Any]:
    """
    Monitor keywords that a competitor is targeting.
    
    Uses existing keyword analysis functionality.
    
    Args:
        competitor_domain: Domain of the competitor (e.g., "bet365.com")
        timeframe: Time period for analysis (e.g., "30d", "90d")
    
    Returns:
        Dictionary with competitor's keywords and metrics
    """
    from ..config import get_settings
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool
    from ..tools.trend_tools import SerpAPIGoogleTrendsAnalyzer
    
    settings = get_settings()
    
    if not settings.serpapi_key:
        logger.warning("SerpAPI key not available for keyword monitoring")
        return {
            "competitor": competitor_domain,
            "keywords": [],
            "error": "SerpAPI key not available"
        }
    
    search_tool = SerpAPISearchTool(settings.serpapi_key)
    trend_analyzer = SerpAPIGoogleTrendsAnalyzer(settings.serpapi_key)
    
    # Извлекаем бренд из домена
    brand_name = competitor_domain.replace(".com", "").replace("www.", "")
    
    # Анализируем тренды для бренда
    try:
        trend_data = trend_analyzer.get_trends(brand_name, timeframe)
        
        # Извлекаем ключевые слова из related queries
        keywords = []
        if trend_data.get("related_queries"):
            rising = trend_data["related_queries"].get("rising", [])
            top = trend_data["related_queries"].get("top", [])
            
            for query in rising[:10]:
                keywords.append({
                    "keyword": query.get("query", ""),
                    "type": "rising",
                    "growth": query.get("value", 0)
                })
            
            for query in top[:10]:
                keywords.append({
                    "keyword": query.get("query", ""),
                    "type": "top",
                    "volume": query.get("value", 0)
                })
        
        return {
            "competitor": competitor_domain,
            "brand_name": brand_name,
            "keywords": keywords,
            "total_keywords": len(keywords),
            "trend_data": trend_data,
            "timeframe": timeframe
        }
    except Exception as e:
        logger.error(f"Error monitoring keywords for {competitor_domain}: {e}")
        return {
            "competitor": competitor_domain,
            "keywords": [],
            "error": str(e)
        }


@tool
def calculate_competitor_metrics(
    competitor_domain: str,
    market_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Calculate metrics (BAP, APS, CEB) for a competitor.
    
    Args:
        competitor_domain: Domain of the competitor
        market_data: Optional market data for comparison
    
    Returns:
        Dictionary with calculated metrics
    """
    from ..config import get_settings
    from ..tools.trend_tools import SerpAPIGoogleTrendsAnalyzer
    
    settings = get_settings()
    
    if not settings.serpapi_key:
        return {
            "competitor": competitor_domain,
            "bap": None,
            "aps": None,
            "ceb": None,
            "error": "SerpAPI key not available"
        }
    
    trend_analyzer = SerpAPIGoogleTrendsAnalyzer(settings.serpapi_key)
    brand_name = competitor_domain.replace(".com", "").replace("www.", "")
    
    try:
        # Получаем данные о трендах
        trend_data = trend_analyzer.get_trends(brand_name, "1y")
        
        # Упрощенный расчет метрик
        interest_over_time = trend_data.get("interest_over_time", [])
        if interest_over_time:
            avg_interest = sum(
                point.get("value", 0) for point in interest_over_time
            ) / len(interest_over_time)
        else:
            avg_interest = 0
        
        # BAP (Brand's Accumulated Power) - упрощенная версия
        # В реальности нужны данные о всем рынке
        bap = min(avg_interest / 100, 1.0) if avg_interest > 0 else 0.0
        
        # APS (Acquisition Power Score) - упрощенная версия
        # Основан на росте интереса
        rising_queries = trend_data.get("related_queries", {}).get("rising", [])
        growth_rate = len(rising_queries) / 10.0 if rising_queries else 0.0
        aps = bap * (1 + growth_rate * 0.1)
        
        # CEB (Competitive Earning Baseline) - упрощенная версия
        # Основан на BAP и APS
        base_revenue = 1000000  # Базовая оценка
        ceb = base_revenue * bap * aps
        
        return {
            "competitor": competitor_domain,
            "brand_name": brand_name,
            "bap": round(bap, 4),
            "aps": round(aps, 4),
            "ceb": round(ceb, 2),
            "avg_interest": round(avg_interest, 2),
            "growth_rate": round(growth_rate, 4)
        }
    except Exception as e:
        logger.error(f"Error calculating metrics for {competitor_domain}: {e}")
        return {
            "competitor": competitor_domain,
            "error": str(e)
        }


@tool
def detect_competitor_changes(
    competitor_domain: str,
    previous_data: Dict[str, Any],
    current_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Detect changes in competitor's strategy (keywords, metrics).
    
    Args:
        competitor_domain: Domain of the competitor
        previous_data: Previous monitoring data
        current_data: Current monitoring data
    
    Returns:
        Dictionary with detected changes
    """
    changes = {
        "competitor": competitor_domain,
        "changes_detected": [],
        "severity": "low"
    }
    
    # Сравниваем ключевые слова
    prev_keywords = set(
        k.get("keyword", "") for k in previous_data.get("keywords", [])
    )
    curr_keywords = set(
        k.get("keyword", "") for k in current_data.get("keywords", [])
    )
    
    new_keywords = curr_keywords - prev_keywords
    dropped_keywords = prev_keywords - curr_keywords
    
    if new_keywords:
        changes["changes_detected"].append({
            "type": "new_keywords",
            "keywords": list(new_keywords),
            "count": len(new_keywords)
        })
        changes["severity"] = "medium"
    
    if dropped_keywords:
        changes["changes_detected"].append({
            "type": "dropped_keywords",
            "keywords": list(dropped_keywords),
            "count": len(dropped_keywords)
        })
    
    # Сравниваем метрики
    prev_bap = previous_data.get("metrics", {}).get("bap", 0)
    curr_bap = current_data.get("metrics", {}).get("bap", 0)
    
    if abs(curr_bap - prev_bap) > 0.05:  # Изменение больше 5%
        changes["changes_detected"].append({
            "type": "metric_change",
            "metric": "bap",
            "previous": prev_bap,
            "current": curr_bap,
            "change": curr_bap - prev_bap,
            "change_percent": ((curr_bap - prev_bap) / prev_bap * 100) if prev_bap > 0 else 0
        })
        if abs(curr_bap - prev_bap) > 0.1:
            changes["severity"] = "high"
    
    return changes


@tool
def discover_new_igaming_brands(
    country: Optional[str] = None,
    timeframe: str = "30d"
) -> Dict[str, Any]:
    """
    Discover new online casino brands in the market.
    
    Args:
        country: Optional country code
        timeframe: Time period (e.g., "30d")
    
    Returns:
        Dictionary with newly discovered brands
    """
    from ..config import get_settings
    from ..tools.search_tools import SerpAPISearchTool, MockSearchTool
    
    settings = get_settings()
    
    if settings.serpapi_key:
        search_tool = SerpAPISearchTool(settings.serpapi_key)
    else:
        search_tool = MockSearchTool()
    
    queries = [
        "new online casino 2024",
        "latest casino sites",
        "new gambling platforms"
    ]
    
    if country:
        queries.append(f"new casino {country} 2024")
    
    new_brands = []
    seen_domains = set()
    
    for query in queries:
        results = search_tool.search(query)
        
        for result in results:
            link = result.get("link", "")
            domain = link.split("/")[2] if "/" in link else link
            
            if domain not in seen_domains:
                seen_domains.add(domain)
                new_brands.append({
                    "name": result.get("title", domain),
                    "domain": domain,
                    "url": link,
                    "description": result.get("snippet", ""),
                    "discovered_via": query
                })
    
    return {
        "country": country,
        "timeframe": timeframe,
        "new_brands": new_brands[:15],  # Top 15
        "count": len(new_brands)
    }
```

#### Реализация агента (`src/agents/competitor_tracker_agent.py`):

```python
"""Competitor Tracker Agent using LangChain."""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool

from ..config import get_settings
from ..utils.logging import get_logger
from .competitor_tracking_tools import (
    identify_igaming_competitors,
    monitor_competitor_keywords,
    calculate_competitor_metrics,
    detect_competitor_changes,
    discover_new_igaming_brands
)

logger = get_logger(__name__)


class CompetitorTrackerAgent:
    """
    LangChain Agent for tracking competitors in iGaming industry.
    
    Uses tools to identify, monitor, and analyze competitors.
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Competitor Tracker Agent.
        
        Args:
            llm: Optional LLM instance (creates default if not provided)
        """
        settings = get_settings()
        
        if llm is None:
            self.llm = ChatOpenAI(
                model=settings.default_model,
                temperature=0,  # Low temperature for consistent tracking
                api_key=settings.openai_api_key
            )
        else:
            self.llm = llm
        
        # Create tools
        self.tools = [
            identify_igaming_competitors,
            monitor_competitor_keywords,
            calculate_competitor_metrics,
            detect_competitor_changes,
            discover_new_igaming_brands
        ]
        
        # Create agent
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert competitor tracking agent for the iGaming (online casino) industry.

Your task is to:
1. Identify competitors for online casino brands
2. Monitor their keywords and metrics
3. Track changes in their strategy
4. Discover new competitors in the market

Focus specifically on online casino, betting, and gambling brands.

Use the available tools to:
- identify_igaming_competitors: Find competitors for a brand
- monitor_competitor_keywords: Monitor keywords a competitor is targeting
- calculate_competitor_metrics: Calculate BAP, APS, CEB metrics
- detect_competitor_changes: Detect changes in competitor strategy
- discover_new_igaming_brands: Find new brands in the market

Always provide detailed analysis and actionable insights."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def track_competitors(
        self,
        brand_name: str,
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track competitors for a given brand.
        
        Args:
            brand_name: Name of the brand to track competitors for
            country: Optional country code
        
        Returns:
            Dictionary with competitor tracking results
        """
        input_text = f"Identify and analyze competitors for {brand_name}"
        if country:
            input_text += f" in {country}"
        input_text += ". Provide detailed analysis including their keywords and metrics."
        
        try:
            result = self.agent_executor.invoke({"input": input_text})
            logger.info(f"Competitor tracking completed for {brand_name}")
            return result
        except Exception as e:
            logger.error(f"Error in competitor tracking: {e}")
            return {
                "error": str(e),
                "brand": brand_name
            }
    
    def monitor_competitor(
        self,
        competitor_domain: str,
        previous_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Monitor a specific competitor.
        
        Args:
            competitor_domain: Domain of the competitor
            previous_data: Optional previous monitoring data for comparison
        
        Returns:
            Dictionary with monitoring results
        """
        input_text = f"Monitor competitor {competitor_domain}"
        
        if previous_data:
            input_text += f" and compare with previous data. Detect any changes."
        else:
            input_text += ". Analyze their keywords and calculate metrics."
        
        try:
            result = self.agent_executor.invoke({"input": input_text})
            logger.info(f"Competitor monitoring completed for {competitor_domain}")
            return result
        except Exception as e:
            logger.error(f"Error in competitor monitoring: {e}")
            return {
                "error": str(e),
                "competitor": competitor_domain
            }
    
    def discover_new_competitors(
        self,
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover new competitors in the market.
        
        Args:
            country: Optional country code
        
        Returns:
            Dictionary with newly discovered competitors
        """
        input_text = f"Discover new online casino brands"
        if country:
            input_text += f" in {country}"
        input_text += " and analyze them."
        
        try:
            result = self.agent_executor.invoke({"input": input_text})
            logger.info("New competitor discovery completed")
            return result
        except Exception as e:
            logger.error(f"Error in competitor discovery: {e}")
            return {
                "error": str(e)
            }
```

#### Нода для агента (`src/nodes/competitor_tracker_node.py`):

```python
"""Competitor Tracker Node using LangChain Agent."""

from typing import Dict, Any
from ..graph.state import GraphState
from ..agents.competitor_tracker_agent import CompetitorTrackerAgent
from ..utils.errors import handle_node_error
from ..utils.logging import get_logger

logger = get_logger(__name__)


def competitor_tracker_node(state: GraphState) -> GraphState:
    """
    Node that uses Competitor Tracker Agent to track competitors.
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with competitor tracking results
    """
    try:
        logger.info("Starting competitor tracker node")
        
        # Get brand name from state
        brand_name = state.get("brand_name") or state.get("search_query")
        
        if not brand_name:
            raise ValueError("brand_name or search_query is required")
        
        # Get country if available
        country = state.get("country")
        
        # Create agent
        agent = CompetitorTrackerAgent()
        
        # Track competitors
        result = agent.track_competitors(brand_name, country)
        
        # Update state
        state["tracked_competitors"] = result.get("output", {})
        state["execution_path"].append("competitor_tracker_node")
        
        # Extract competitors list if available
        if "competitors" in result.get("output", {}):
            state["competitors_list"] = result["output"]["competitors"]
        
        logger.info(f"Competitor tracking completed for {brand_name}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in competitor tracker node: {e}")
        return handle_node_error(state, e, "competitor_tracker_node")
```

---

## 2️⃣ Report Generator Agent

### Назначение
Автоматически генерирует отчеты с помощью AI, анализируя данные о конкурентах.

### Что делает агент:
1. **Собирает данные** - из разных источников (конкуренты, метрики, ключевые слова)
2. **Анализирует с LLM** - использует LLM для глубокого анализа
3. **Генерирует отчет** - создает структурированный отчет
4. **Создает визуализации** - генерирует графики и диаграммы
5. **Экспортирует** - в PDF, Excel, HTML

### Реализация с LangChain

#### Инструменты для агента (`src/tools/report_tools.py`):

```python
"""Tools for report generation."""

from langchain.tools import tool
from typing import Dict, Any, List, Optional
from ..utils.logging import get_logger
from ..utils.visualization import create_visualization
from ..utils.formatters import ResponseFormatter

logger = get_logger(__name__)


@tool
def collect_competitor_data(
    competitors: List[str],
    include_keywords: bool = True,
    include_metrics: bool = True
) -> Dict[str, Any]:
    """
    Collect data about competitors for report generation.
    
    Args:
        competitors: List of competitor domains
        include_keywords: Whether to include keyword data
        include_metrics: Whether to include metrics data
    
    Returns:
        Dictionary with collected competitor data
    """
    from ..agents.competitor_tracker_agent import CompetitorTrackerAgent
    
    agent = CompetitorTrackerAgent()
    collected_data = {
        "competitors": [],
        "total_count": len(competitors)
    }
    
    for competitor in competitors:
        competitor_data = {
            "domain": competitor
        }
        
        if include_keywords:
            keywords_result = agent.monitor_competitor(competitor)
            competitor_data["keywords"] = keywords_result.get("output", {})
        
        if include_metrics:
            # Calculate metrics
            from .competitor_tracking_tools import calculate_competitor_metrics
            metrics = calculate_competitor_metrics(competitor)
            competitor_data["metrics"] = metrics
        
        collected_data["competitors"].append(competitor_data)
    
    return collected_data


@tool
def analyze_data_with_llm(
    data: Dict[str, Any],
    analysis_type: str = "competitive_analysis"
) -> str:
    """
    Analyze data using LLM to generate insights.
    
    Args:
        data: Data to analyze
        analysis_type: Type of analysis (competitive_analysis, keyword_analysis, etc.)
    
    Returns:
        Analysis text generated by LLM
    """
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from ..config import get_settings
    
    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0.7,  # Higher temperature for creative analysis
        api_key=settings.openai_api_key
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert analyst for the iGaming industry.
        
Analyze the provided data and generate comprehensive insights for a {analysis_type} report.

Focus on:
- Key findings and trends
- Competitive positioning
- Opportunities and threats
- Actionable recommendations

Provide detailed, professional analysis suitable for a business report."""),
        ("human", "Analyze this data:\n{data}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({"data": str(data)})
    
    return result.content if hasattr(result, 'content') else str(result)


@tool
def generate_report_visualization(
    data: Dict[str, Any],
    chart_type: str = "bar"
) -> str:
    """
    Generate visualization for report.
    
    Args:
        data: Data to visualize
        chart_type: Type of chart (bar, line, pie, etc.)
    
    Returns:
        Base64 encoded image or file path
    """
    from ..utils.visualization import create_visualization
    
    try:
        visualization = create_visualization(data, chart_type)
        return visualization
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        return ""


@tool
def export_report_to_pdf(
    report_content: str,
    visualizations: List[str],
    output_path: str
) -> str:
    """
    Export report to PDF format.
    
    Args:
        report_content: Report content (HTML or markdown)
        visualizations: List of visualization file paths or base64 images
        output_path: Path to save PDF
    
    Returns:
        Path to generated PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        import base64
        from io import BytesIO
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        for line in report_content.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 0.2*inch))
        
        # Add visualizations
        for viz in visualizations:
            if viz.startswith("data:image"):
                # Base64 image
                base64_data = viz.split(",")[1]
                image_data = base64.b64decode(base64_data)
                img = Image(BytesIO(image_data), width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 0.3*inch))
        
        doc.build(story)
        logger.info(f"PDF report exported to {output_path}")
        return output_path
        
    except ImportError:
        logger.warning("reportlab not installed, cannot export to PDF")
        return ""
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        return ""
```

#### Реализация агента (`src/agents/report_generator_agent.py`):

```python
"""Report Generator Agent using LangChain."""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime

from ..config import get_settings
from ..utils.logging import get_logger
from .report_tools import (
    collect_competitor_data,
    analyze_data_with_llm,
    generate_report_visualization,
    export_report_to_pdf
)

logger = get_logger(__name__)


class ReportGeneratorAgent:
    """
    LangChain Agent for generating competitive intelligence reports.
    
    Uses tools to collect data, analyze with LLM, and generate reports.
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize Report Generator Agent.
        
        Args:
            llm: Optional LLM instance
        """
        settings = get_settings()
        
        if llm is None:
            self.llm = ChatOpenAI(
                model=settings.default_model,
                temperature=0.3,  # Balanced for creative but consistent reports
                api_key=settings.openai_api_key
            )
        else:
            self.llm = llm
        
        # Create tools
        self.tools = [
            collect_competitor_data,
            analyze_data_with_llm,
            generate_report_visualization,
            export_report_to_pdf
        ]
        
        # Create agent
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert report generator for competitive intelligence in the iGaming industry.

Your task is to generate comprehensive, professional reports that include:
1. Executive summary
2. Competitive analysis
3. Keyword analysis
4. Metrics comparison
5. Trends and insights
6. Recommendations

Use the available tools to:
- collect_competitor_data: Gather data about competitors
- analyze_data_with_llm: Generate deep insights using LLM
- generate_report_visualization: Create charts and graphs
- export_report_to_pdf: Export final report to PDF

Always create well-structured, actionable reports suitable for business decision-making."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def generate_competitive_report(
        self,
        brand_name: str,
        competitors: List[str],
        report_type: str = "competitive_analysis"
    ) -> Dict[str, Any]:
        """
        Generate competitive analysis report.
        
        Args:
            brand_name: Name of the brand
            competitors: List of competitor domains
            report_type: Type of report
        
        Returns:
            Dictionary with report data and file path
        """
        input_text = f"""Generate a {report_type} report for {brand_name}.

Competitors to analyze: {', '.join(competitors)}

Include:
1. Competitive positioning
2. Keyword analysis
3. Metrics comparison (BAP, APS, CEB)
4. Trends and insights
5. Actionable recommendations

Create visualizations and export to PDF."""
        
        try:
            result = self.agent_executor.invoke({"input": input_text})
            
            # Generate report file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = f"report_{brand_name}_{timestamp}"
            
            return {
                "report_id": report_id,
                "brand_name": brand_name,
                "report_type": report_type,
                "content": result.get("output", ""),
                "generated_at": datetime.now().isoformat(),
                "competitors_analyzed": len(competitors)
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "error": str(e),
                "brand_name": brand_name
            }
```

#### Нода для агента (`src/nodes/report_generator_node.py`):

```python
"""Report Generator Node using LangChain Agent."""

from typing import Dict, Any
from ..graph.state import GraphState
from ..agents.report_generator_agent import ReportGeneratorAgent
from ..utils.errors import handle_node_error
from ..utils.logging import get_logger

logger = get_logger(__name__)


def report_generator_node(state: GraphState) -> GraphState:
    """
    Node that uses Report Generator Agent to generate reports.
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with report data
    """
    try:
        logger.info("Starting report generator node")
        
        # Get data from state
        brand_name = state.get("brand_name") or state.get("search_query")
        competitors = state.get("competitors_list", [])
        report_type = state.get("report_type", "competitive_analysis")
        
        if not brand_name:
            raise ValueError("brand_name or search_query is required")
        
        if not competitors:
            # Try to get from tracked_competitors
            tracked = state.get("tracked_competitors", {})
            if isinstance(tracked, dict) and "competitors" in tracked:
                competitors = [c.get("domain", "") for c in tracked["competitors"]]
        
        if not competitors:
            logger.warning("No competitors found, generating report without competitor data")
        
        # Create agent
        agent = ReportGeneratorAgent()
        
        # Generate report
        result = agent.generate_competitive_report(
            brand_name,
            competitors,
            report_type
        )
        
        # Update state
        state["report_data"] = result
        state["report_generated"] = True
        if "report_id" in result:
            state["report_file_path"] = f"reports/{result['report_id']}.pdf"
        state["execution_path"].append("report_generator_node")
        
        logger.info(f"Report generated for {brand_name}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in report generator node: {e}")
        return handle_node_error(state, e, "report_generator_node")
```

---

## 📋 План реализации

### Фаза 1: Competitor Tracker Agent (2-3 недели)
- [ ] Создать инструменты для отслеживания конкурентов (`competitor_tracking_tools.py`)
- [ ] Реализовать `CompetitorTrackerAgent` с LangChain
- [ ] Создать ноду `competitor_tracker_node`
- [ ] Интегрировать в граф
- [ ] Тесты

### Фаза 2: Report Generator Agent (2-3 недели)
- [ ] Создать инструменты для генерации отчетов (`report_tools.py`)
- [ ] Реализовать `ReportGeneratorAgent` с LangChain
- [ ] Создать ноду `report_generator_node`
- [ ] Интегрировать в граф
- [ ] Тесты

### Фаза 3: Интеграция и тестирование (1-2 недели)
- [ ] Обновить маршрутизацию в графе
- [ ] Обновить Thinking Node для новых типов решений
- [ ] End-to-end тесты
- [ ] Оптимизация

---

## 🎯 Итог

Созданы два AI-агента с LangChain:
1. **Competitor Tracker Agent** - автоматически определяет и отслеживает конкурентов в онлайн-казино
2. **Report Generator Agent** - автоматически генерирует отчеты с помощью AI

Оба агента сфокусированы на узком спектре - индустрия онлайн-казино (iGaming).
