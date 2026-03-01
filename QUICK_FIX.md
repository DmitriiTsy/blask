# Quick Fix: "command not found: pytest"

## Проблема
При попытке запустить `pytest` получаете ошибку:
```
zsh: command not found: pytest
```

## Решение

### Вариант 1: Использовать python3 -m pytest (быстрое решение)

Вместо `pytest` используйте:
```bash
python3 -m pytest tests/
```

Это работает даже если pytest не установлен глобально, но установлен в системе.

### Вариант 2: Установить через виртуальное окружение (рекомендуется)

```bash
# 1. Создать виртуальное окружение
python3 -m venv venv

# 2. Активировать
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Теперь pytest будет доступен
pytest tests/
```

### Вариант 3: Использовать скрипт установки

```bash
./install.sh
```

Это автоматически создаст виртуальное окружение и установит все зависимости.

### Вариант 4: Установить глобально (не рекомендуется)

```bash
pip3 install --user pytest pytest-cov
```

Затем добавьте в PATH (если нужно):
```bash
export PATH="$HOME/Library/Python/3.13/bin:$PATH"
```

## Проверка

После установки проверьте:
```bash
python3 -m pytest --version
# или
pytest --version
```

## Запуск тестов

```bash
# С виртуальным окружением
source venv/bin/activate
pytest tests/

# Без виртуального окружения
python3 -m pytest tests/
```
