# Быстрый старт - Запуск тестов

## Шаг 1: Установка зависимостей

Выберите один из вариантов:

### Вариант A: Автоматическая установка (рекомендуется)
```bash
./install.sh
```

### Вариант B: Ручная установка
```bash
# 1. Создать виртуальное окружение
python3 -m venv venv

# 2. Активировать окружение
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt
```

## Шаг 2: Запуск тестов

### Если используете виртуальное окружение:
```bash
# Активировать окружение (если еще не активировано)
source venv/bin/activate

# Запустить все тесты
pytest tests/ -v

# Или с покрытием
pytest tests/ --cov=src --cov-report=html
```

### Если НЕ используете виртуальное окружение:
```bash
# Использовать python3 -m pytest
python3 -m pytest tests/ -v
```

## Проверка исправленных тестов

После исправлений запустите:

```bash
# Все тесты
python3 -m pytest tests/ -v

# Только исправленные тесты
python3 -m pytest tests/test_formatters.py::TestFormatSearchResults::test_format_with_limit -v
python3 -m pytest tests/test_search_node.py::TestSearchNode::test_search_node_error_handling -v
```

## Если все еще не работает

Установите pytest напрямую:
```bash
pip3 install --user pytest pytest-cov
```

Затем запустите:
```bash
python3 -m pytest tests/ -v
```
