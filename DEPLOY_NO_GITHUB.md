# Деплой БЕЗ GitHub

## 🎯 Быстрый выбор

**Если не хотите использовать GitHub, лучшие варианты:**

1. **Railway.app** - самый простой, можно через CLI или веб
2. **Render.com** - можно загрузить ZIP файл
3. **Fly.io** - через CLI, бесплатно
4. **Heroku** - через локальный Git (не GitHub)

---

## 🚂 Railway.app (РЕКОМЕНДУЕТСЯ)

### Вариант 1: Через CLI (самый простой)

```bash
# 1. Установите Railway CLI
npm i -g @railway/cli

# 2. Логин
railway login

# 3. В директории проекта
cd /Users/dmitrii/maincard/Blask
railway init

# 4. Добавьте переменные
railway variables set OPENAI_API_KEY=your_key_here
railway variables set SERPAPI_KEY=your_key_here

# 5. Деплой
railway up
```

### Вариант 2: Через веб-интерфейс

1. Зайдите на https://railway.app/
2. New Project → Empty Project
3. Settings → Source → Upload code
4. Загрузите ZIP архива проекта (без venv, .env, __pycache__)
5. Добавьте переменные окружения
6. Railway автоматически определит Python и задеплоит

**Railway автоматически использует Procfile** (уже создан)

---

## 🌐 Render.com

1. **Создайте ZIP архива:**
```bash
# В директории проекта
zip -r blask.zip . -x "venv/*" ".env" "__pycache__/*" "*.pyc" ".git/*"
```

2. **Зайдите на https://render.com/**

3. **New → Web Service**

4. **Upload ZIP file**

5. **Настройте:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0`

6. **Добавьте Environment Variables:**
   - `OPENAI_API_KEY`
   - `SERPAPI_KEY` (опционально)

7. **Deploy**

---

## ✈️ Fly.io

```bash
# 1. Установите Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Логин
fly auth login

# 3. Создайте fly.toml (создам ниже)
fly launch

# 4. Добавьте секреты
fly secrets set OPENAI_API_KEY=your_key
fly secrets set SERPAPI_KEY=your_key

# 5. Деплой
fly deploy
```

---

## 📦 Подготовка к деплою (удалить лишнее)

Перед созданием ZIP или деплоем, убедитесь что удалили:

```bash
# Удалите из проекта перед деплоем:
- venv/
- .env
- __pycache__/
- *.pyc
- .git/ (если не нужен)
- .pytest_cache/
- htmlcov/
```

---

## 🎯 Моя рекомендация

**Используйте Railway.app через CLI** - это самый простой способ без GitHub:

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set OPENAI_API_KEY=your_key
railway up
```

Готово! Приложение будет доступно по адресу типа: `https://your-app.railway.app`
