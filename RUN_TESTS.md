# Как запустить тесты

## Быстрый запуск

### Все тесты
```bash
python3 -m pytest tests/
```

### С подробным выводом
```bash
python3 -m pytest tests/ -v
```

### С покрытием кода
```bash
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Конкретный тест
```bash
python3 -m pytest tests/test_state.py -v
```

### Конкретный тест-класс
```bash
python3 -m pytest tests/test_formatters.py::TestFormatSearchResults -v
```

### Конкретный тест-метод
```bash
python3 -m pytest tests/test_formatters.py::TestFormatSearchResults::test_format_with_limit -v
```

## Если pytest не установлен

### Вариант 1: Использовать python3 -m pytest
```bash
python3 -m pytest tests/
```

### Вариант 2: Установить в виртуальном окружении
```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Теперь можно использовать pytest напрямую
pytest tests/
```

## Полезные опции

### Показать print statements
```bash
python3 -m pytest tests/ -s
```

### Остановиться на первой ошибке
```bash
python3 -m pytest tests/ -x
```

### Запустить только упавшие тесты
```bash
python3 -m pytest tests/ --lf
```

### Показать покрытие в терминале
```bash
python3 -m pytest tests/ --cov=src --cov-report=term-missing
```

### Генерация HTML отчета о покрытии
```bash
python3 -m pytest tests/ --cov=src --cov-report=html
# Отчет будет в htmlcov/index.html
```

## Проверка исправленных тестов

После исправлений можно проверить конкретные тесты:

```bash
# Проверить исправленный тест форматирования
python3 -m pytest tests/test_formatters.py::TestFormatSearchResults::test_format_with_limit -v

# Проверить исправленный тест обработки ошибок
python3 -m pytest tests/test_search_node.py::TestSearchNode::test_search_node_error_handling -v
```
