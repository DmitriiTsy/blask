# Code Structure and SOLID Principles

## Project Structure

```
Blask/
├── src/
│   ├── config/          # Configuration (Settings)
│   ├── graph/           # Graph definition and state
│   ├── nodes/           # Node implementations
│   ├── tools/           # Search and analysis tools
│   ├── utils/           # Utilities (visualization, formatting, errors)
│   └── main.py          # Entry point
├── tests/               # Test suite (100% coverage)
└── [config files]       # pytest.ini, mypy.ini, etc.
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)

Each module has a single, well-defined responsibility:

- **`thinking_node.py`** - Only handles query analysis and decision making
- **`search_node.py`** - Only handles search operations
- **`analysis_node.py`** - Only handles data processing and formatting
- **`search_tools.py`** - Only handles search functionality
- **`visualization.py`** - Only handles chart creation
- **`formatters.py`** - Only handles response formatting

### Open/Closed Principle (OCP)

Classes are open for extension but closed for modification:

- **`SearchTool`** (ABC) - Can add new search implementations without modifying existing code
- **`CompetitorAnalyzer`** (ABC) - Can add new analysis strategies
- **`TrendAnalyzer`** (ABC) - Can add new trend sources
- **`ChartCreator`** (ABC) - Can add new chart types

### Liskov Substitution Principle (LSP)

Subclasses can replace base classes:

- `MockSearchTool` can replace `SerpAPISearchTool`
- `MockCompetitorAnalyzer` can replace `BasicCompetitorAnalyzer`
- All implementations follow their base class contracts

### Interface Segregation Principle (ISP)

Small, specific interfaces:

- **`DecisionMaker`** - Only decision-making interface
- **`DataFormatter`** - Only formatting interface
- **`NodeProcessor`** (Protocol) - Only node processing interface
- Tools have separate interfaces for different concerns

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:

- Nodes depend on `SearchTool` (ABC), not `SerpAPISearchTool`
- Nodes depend on `CompetitorAnalyzer` (ABC), not concrete implementations
- Factory functions (`create_search_node`) inject dependencies
- All dependencies are injected, not created inside classes

## Type Safety

- **Strict Typing**: All functions have type hints
- **TypedDict**: `GraphState` uses TypedDict for state safety
- **Protocols**: Used for structural typing (`NodeProcessor`)
- **Abstract Base Classes**: Used for interfaces
- **mypy**: Configured for strict type checking

## Testing Strategy

### Test Coverage: 100%

Every component has comprehensive tests:

1. **Unit Tests** - Test individual functions/classes in isolation
2. **Integration Tests** - Test component interactions
3. **Error Handling Tests** - Test error scenarios
4. **Edge Case Tests** - Test boundary conditions

### Test Organization

- `test_state.py` - State management tests
- `test_config.py` - Configuration tests
- `test_errors.py` - Error handling tests
- `test_tools.py` - Tool tests
- `test_thinking_node.py` - Thinking node tests
- `test_search_node.py` - Search node tests
- `test_analysis_node.py` - Analysis node tests
- `test_visualization.py` - Visualization tests
- `test_formatters.py` - Formatter tests
- `test_graph.py` - Graph structure tests

## Code Quality Standards

1. **Comments**: All code comments in English
2. **Docstrings**: All functions/classes have docstrings
3. **Type Hints**: All functions have complete type hints
4. **Error Handling**: Comprehensive error handling with logging
5. **Logging**: Proper logging at all levels
6. **Modularity**: Small, focused modules
7. **Reusability**: Components are reusable and composable

## Dependency Injection

Dependencies are injected, not created:

```python
# Good: Dependency injection
def create_search_node(search_tool: SearchTool):
    processor = SearchNodeProcessor(search_tool)
    return search_node

# Bad: Creating dependencies inside
def search_node(state):
    tool = SerpAPISearchTool()  # Don't do this
```

## Extension Points

Easy to extend without modifying existing code:

1. **New Search Tools**: Implement `SearchTool` ABC
2. **New Analyzers**: Implement `CompetitorAnalyzer` or `TrendAnalyzer` ABC
3. **New Chart Types**: Extend `ChartCreator` ABC
4. **New Formatters**: Implement `DataFormatter` interface
5. **New Nodes**: Follow `NodeProcessor` protocol

## Best Practices Followed

- ✅ Small, focused modules
- ✅ Dependency injection
- ✅ Interface segregation
- ✅ Abstract base classes
- ✅ Protocol-based typing
- ✅ Comprehensive error handling
- ✅ Full test coverage
- ✅ Type safety
- ✅ English comments
- ✅ Clear documentation
