# Настройка Streamlit Cloud

## 🚀 После пуша в GitHub

После того как вы запушили код в GitHub, следуйте этим шагам:

### Шаг 1: Перейдите на Streamlit Cloud

Зайдите на: **https://share.streamlit.io/**

### Шаг 2: Войдите через GitHub

Нажмите "Sign in" и авторизуйтесь через GitHub аккаунт.

### Шаг 3: Создайте новое приложение

1. Нажмите **"New app"**
2. Заполните форму:
   - **Repository**: `DmitriiTsy/blask`
   - **Branch**: `main`
   - **Main file path**: `src/webapp.py`
   - **App URL** (опционально): можно оставить автоматический или задать свой

### Шаг 4: Добавьте Secrets (API ключи)

1. Нажмите **"Advanced settings"**
2. Перейдите в **"Secrets"**
3. Добавьте следующие переменные:

```toml
OPENAI_API_KEY = "sk-your-key-here"
SERPAPI_KEY = "your-serpapi-key-here"  # опционально
```

**Важно:** Используйте формат TOML (как показано выше)

### Шаг 5: Deploy

1. Нажмите **"Deploy"**
2. Дождитесь завершения деплоя (обычно 1-2 минуты)
3. Приложение будет доступно по адресу: `https://blask.streamlit.app` (или ваш кастомный URL)

---

## ✅ Проверка

После деплоя проверьте:

1. ✅ Приложение открывается
2. ✅ Можно ввести запрос
3. ✅ Результаты отображаются
4. ✅ Thinking Component показывает активные ноды

---

## 🔄 Обновления

После каждого `git push` в репозиторий, Streamlit Cloud автоматически:
- Обнаружит изменения
- Пересоберет приложение
- Задеплоит новую версию

Обычно это занимает 1-2 минуты.

---

## 🐛 Troubleshooting

### Приложение не запускается

1. Проверьте логи в Streamlit Cloud dashboard
2. Убедитесь что все Secrets добавлены правильно
3. Проверьте что `src/webapp.py` существует в репозитории

### Ошибка импорта модулей

Убедитесь что в `src/webapp.py` есть код для добавления пути:
```python
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

### API ключи не работают

1. Проверьте формат Secrets (должен быть TOML)
2. Убедитесь что ключи правильные
3. Проверьте что нет лишних пробелов

---

## 📝 Полезные ссылки

- Streamlit Cloud: https://share.streamlit.io/
- Документация: https://docs.streamlit.io/streamlit-community-cloud
- Ваш репозиторий: https://github.com/DmitriiTsy/blask
