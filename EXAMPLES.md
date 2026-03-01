# Examples of Usage

## Basic Usage

```python
from src.graph.graph import create_graph
from src.graph.state import create_initial_state

# Create graph
graph = create_graph()

# Create initial state
state = create_initial_state("What are the latest AI trends?")

# Execute graph
result = graph.invoke(state)

# Access results
print(result["formatted_response"])
if result.get("visualization"):
    print("Chart created!")
```

## Custom Search Node with Dependencies

```python
from src.graph.graph import create_graph
from src.nodes.search_node import create_search_node
from src.tools.search_tools import SerpAPISearchTool
from src.tools.competitor_tools import BasicCompetitorAnalyzer
from src.tools.trend_tools import SearchBasedTrendAnalyzer

# Create tools
search_tool = SerpAPISearchTool(api_key="your_key")
competitor_analyzer = BasicCompetitorAnalyzer(search_tool)
trend_analyzer = SearchBasedTrendAnalyzer(search_tool)

# Create custom search node
search_node = create_search_node(
    search_tool=search_tool,
    competitor_analyzer=competitor_analyzer,
    trend_analyzer=trend_analyzer
)

# Use in graph (modify graph.py to use custom node)
```

## Testing Individual Components

```python
from src.nodes.thinking_node import LLMDecisionMaker

# Test decision maker
maker = LLMDecisionMaker()
decision = maker.make_decision("What are AI trends?", [])
print(decision)
```

## Using Mock Tools for Testing

```python
from src.tools.search_tools import MockSearchTool
from src.tools.competitor_tools import MockCompetitorAnalyzer

# Create mocks
mock_search = MockSearchTool([
    {"title": "Test", "snippet": "Result", "link": "http://test.com"}
])

mock_competitor = MockCompetitorAnalyzer({
    "keyword": "test",
    "competitors": [{"name": "Comp1"}],
    "count": 1
})

# Use in tests
```
