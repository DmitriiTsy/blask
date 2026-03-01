# Деплой Blask приложения

## ⚠️ Важно: Streamlit Cloud требует GitHub

Streamlit Cloud **обязательно** требует GitHub репозиторий. Если не хотите использовать GitHub, используйте альтернативы ниже.

---

## 🚀 Варианты БЕЗ GitHub

### 1. Railway.app (БЕЗ GitHub) ⭐⭐⭐

**Плюсы:**
- ✅ Можно задеплоить через CLI или веб-интерфейс
- ✅ Не требует GitHub (можно загрузить код напрямую)
- ✅ Бесплатный tier
- ✅ Очень просто

**Как задеплоить БЕЗ GitHub:**

1. **Установите Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Логин:**
```bash
railway login
```

3. **В директории проекта:**
```bash
railway init
railway up
```

4. **Добавьте переменные окружения:**
```bash
railway variables set OPENAI_API_KEY=your_key
railway variables set SERPAPI_KEY=your_key
```

5. **Деплой:**
```bash
railway deploy
```

**Или через веб-интерфейс:**
- Зайдите на https://railway.app/
- New Project → Empty Project
- Settings → Source → Upload code (можно загрузить ZIP)

---

### 2. Render.com (БЕЗ GitHub) ⭐⭐

**Плюсы:**
- ✅ Можно загрузить код через веб-интерфейс
- ✅ Бесплатный tier
- ✅ Простая настройка

**Как задеплоить:**

1. **Создайте ZIP архива проекта** (без venv и .env)

2. **Зайдите на https://render.com/**

3. **New → Web Service**

4. **Upload ZIP file** (вместо GitHub)

5. **Настройте:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0`

6. **Добавьте Environment Variables**

7. **Deploy**

---

### 3. Fly.io (БЕЗ GitHub) ⭐

**Плюсы:**
- ✅ Можно деплоить через CLI
- ✅ Бесплатный tier
- ✅ Хорошая документация

**Как задеплоить:**

1. **Установите Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Логин:**
```bash
fly auth login
```

3. **Создайте приложение:**
```bash
fly launch
```

4. **Добавьте переменные:**
```bash
fly secrets set OPENAI_API_KEY=your_key
fly secrets set SERPAPI_KEY=your_key
```

5. **Деплой:**
```bash
fly deploy
```

---

### 4. Heroku (БЕЗ GitHub, через CLI)

**Плюсы:**
- ✅ Можно деплоить через Git (локальный)
- ✅ Надежный
- ❌ Платно (от $7/месяц)

**Как задеплоить:**

1. **Установите Heroku CLI**

2. **Логин:**
```bash
heroku login
```

3. **Создайте приложение:**
```bash
heroku create your-app-name
```

4. **Добавьте переменные:**
```bash
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SERPAPI_KEY=your_key
```

5. **Деплой (использует локальный Git, не GitHub):**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

---

## 🔒 Компромисс: Приватный GitHub репозиторий

Если все же хотите использовать Streamlit Cloud, но не хотите публичный код:

1. **Создайте приватный репозиторий на GitHub** (бесплатно)
2. **Закоммитьте код туда**
3. **Streamlit Cloud работает с приватными репозиториями**

---

## 🚀 Рекомендуемые варианты

### 1. Streamlit Cloud (САМЫЙ ПРОСТОЙ, но требует GitHub) ⭐

**Плюсы:**
- ✅ Бесплатно
- ✅ Специально для Streamlit
- ✅ Автоматический деплой из GitHub
- ✅ Простая настройка
- ✅ HTTPS из коробки

**Как задеплоить:**

1. **Закоммитьте проект в GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/blask.git
git push -u origin main
```

2. **Зайдите на https://share.streamlit.io/**

3. **Войдите через GitHub**

4. **Нажмите "New app"**

5. **Заполните:**
   - Repository: `yourusername/blask`
   - Branch: `main`
   - Main file path: `src/webapp.py`

6. **Добавьте Secrets (API ключи):**
   - `OPENAI_API_KEY` = ваш ключ
   - `SERPAPI_KEY` = ваш ключ (опционально)

7. **Нажмите "Deploy"**

**Готово!** Приложение будет доступно по адресу: `https://your-app-name.streamlit.app`

---

### 2. Railway.app (Очень просто) ⭐⭐

**Плюсы:**
- ✅ Бесплатный tier (с ограничениями)
- ✅ Простая настройка
- ✅ Автоматический деплой из GitHub
- ✅ Поддержка Python

**Как задеплоить:**

1. **Создайте файл `Procfile`:**
```
web: streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0
```

2. **Создайте `railway.json` (опционально):**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. **Закоммитьте в GitHub**

4. **Зайдите на https://railway.app/**

5. **New Project → Deploy from GitHub repo**

6. **Выберите ваш репозиторий**

7. **Добавьте переменные окружения:**
   - `OPENAI_API_KEY`
   - `SERPAPI_KEY` (опционально)

8. **Railway автоматически задеплоит**

---

### 3. Render.com (Бесплатно)

**Плюсы:**
- ✅ Бесплатный tier
- ✅ Автоматический деплой
- ✅ Простая настройка

**Как задеплоить:**

1. **Создайте `render.yaml`:**
```yaml
services:
  - type: web
    name: blask
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: SERPAPI_KEY
        sync: false
```

2. **Закоммитьте в GitHub**

3. **Зайдите на https://render.com/**

4. **New → Web Service**

5. **Подключите GitHub репозиторий**

6. **Настройте:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0`

7. **Добавьте Environment Variables**

8. **Deploy**

---

### 4. Heroku (Платно, но надежно)

**Плюсы:**
- ✅ Надежный
- ✅ Хорошая документация
- ❌ Платно (от $7/месяц)

**Как задеплоить:**

1. **Создайте `Procfile`:**
```
web: streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0
```

2. **Создайте `runtime.txt`:**
```
python-3.13.3
```

3. **Установите Heroku CLI:**
```bash
brew install heroku/brew/heroku
```

4. **Логин:**
```bash
heroku login
```

5. **Создайте приложение:**
```bash
heroku create your-app-name
```

6. **Добавьте переменные:**
```bash
heroku config:set OPENAI_API_KEY=your_key
heroku config:set SERPAPI_KEY=your_key
```

7. **Деплой:**
```bash
git push heroku main
```

---

## 📝 Необходимые файлы для деплоя

### Procfile (для Heroku/Railway)
```
web: streamlit run src/webapp.py --server.port $PORT --server.address 0.0.0.0
```

### .streamlit/config.toml (опционально)
```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false
```

### runtime.txt (для Heroku)
```
python-3.13.3
```

---

## 🔒 Безопасность

**ВАЖНО:** Никогда не коммитьте `.env` файл!

Убедитесь, что `.gitignore` содержит:
```
.env
.env.local
*.env
```

Все API ключи добавляйте через:
- Streamlit Cloud: Secrets
- Railway: Environment Variables
- Render: Environment Variables
- Heroku: Config Vars

---

## 🎯 Рекомендация

**Для начала используйте Streamlit Cloud** - это самый простой и быстрый способ:
1. Бесплатно
2. Специально для Streamlit
3. Минимум настроек
4. Автоматический деплой из GitHub

**Альтернатива:** Railway.app - тоже очень просто и бесплатно.

---

## 📚 Полезные ссылки

- Streamlit Cloud: https://share.streamlit.io/
- Railway: https://railway.app/
- Render: https://render.com/
- Heroku: https://www.heroku.com/
