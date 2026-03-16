# План интеграции CRM-функционала в Blask для Maincard.io

## 🎯 Контекст и цель

### Что делает Maincard.io:
[Maincard.io](https://maincard.io) - это **white-label платформа** для создания онлайн-казино, лотерей и спортивных букмекеров без разработчиков. Основные клиенты:
- **Casino Operators** - операторы казино, которые хотят создать свой бренд
- **Affiliate Managers** - аффилиат-менеджеры, которые хотят монетизировать трафик
- **Influencers** - инфлюенсеры, которые хотят создать свой бренд
- **First-time Founders** - новички в iGaming

### Что делает Blask (текущий проект):
- Competitive intelligence платформа
- Анализ трендов, конкурентов, рынков
- Расчет метрик (BAP, APS, CEB)
- Обнаружение новых брендов

### Цель интеграции:
Превратить Blask в **CRM-систему для Maincard клиентов**, которая:
1. Отслеживает бренды клиентов Maincard
2. Мониторит их конкурентов и рынок
3. Автоматически генерирует отчеты
4. Помогает принимать решения на основе данных
5. Интегрируется с Maincard для синхронизации данных

---

## 🏗️ Архитектура CRM-интеграции

### Новая архитектура графа:

```
START
  │
  ▼
┌─────────────────────┐
│  THINKING NODE      │ ◄─── Расширенная: определяет тип запроса
│  (Enhanced CRM)     │      - client_management
└────────┬────────────┘      - brand_monitoring
         │                   - competitor_tracking
         │                   - report_generation
         │                   - market_analysis
         │
    ┌────┴────┬──────────┬──────────┬────────────┬────────────┐
    │        │          │          │            │            │
    ▼        ▼          ▼          ▼            ▼            ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐
│ CLIENT │ │  BRAND   │ │ COMPETITOR│ │   REPORT    │ │  MARKET     │ │  ALERT       │
│  NODE  │ │ MONITOR  │ │  TRACKER  │ │  GENERATOR  │ │   NODE      │ │   NODE       │
│        │ │   NODE   │ │   NODE    │ │    NODE     │ │             │ │              │
└───┬────┘ └────┬─────┘ └─────┬────┘ └──────┬─────┘ └─────┬───────┘ └──────┬───────┘
    │           │              │             │              │               │
    └───────────┴──────────────┴─────────────┴──────────────┴───────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ AGGREGATION NODE │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  STORAGE NODE   │ ◄─── Сохранение в CRM БД
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  NOTIFICATION    │ ◄─── Уведомления клиентам
              │      NODE        │
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

## 🆕 Новые CRM-ноды

### 1. **Client Management Node** (`src/nodes/client_node.py`)

**Назначение:** Управление клиентами Maincard и их брендами

**Функционал:**
- Регистрация новых клиентов Maincard
- Привязка брендов к клиентам
- Управление подписками и тарифами
- Отслеживание активности клиентов
- История взаимодействий

**Инструменты:**
- `ClientManager` - управление клиентами
- `BrandLinker` - привязка брендов к клиентам
- `SubscriptionManager` - управление подписками

**Входные данные:**
```python
{
    "action": "create" | "update" | "get" | "list",
    "client_id": Optional[str],
    "client_data": {
        "name": str,
        "email": str,
        "maincard_account_id": str,  # ID в системе Maincard
        "subscription_tier": "basic" | "pro" | "enterprise",
        "brands": List[str]  # Список брендов клиента
    }
}
```

**Выходные данные:**
```python
{
    "client_id": "client_123",
    "name": "John's Casino",
    "maincard_account_id": "mc_456",
    "subscription_tier": "pro",
    "brands": ["johnscasino.com", "johnsbet.com"],
    "created_at": "2024-01-15T10:00:00Z",
    "last_active": "2024-01-20T15:30:00Z"
}
```

**Интеграция с Maincard:**
- API для получения списка клиентов
- Синхронизация данных о брендах
- Webhook для обновлений

---

### 2. **Brand Monitoring Node** (`src/nodes/monitoring_node.py`)

**Назначение:** Непрерывный мониторинг брендов клиентов

**Функционал:**
- Ежедневный/еженедельный мониторинг метрик брендов
- Отслеживание изменений BAP, APS, CEB
- Обнаружение проблем (падение метрик)
- Сравнение с конкурентами
- Автоматические алерты

**Инструменты:**
- `BrandMonitor` - мониторинг брендов
- `MetricsTracker` - отслеживание метрик
- `AlertGenerator` - генерация алертов

**Входные данные:**
```python
{
    "client_id": "client_123",
    "brand_name": "johnscasino.com",
    "monitoring_frequency": "daily" | "weekly" | "monthly",
    "metrics_to_track": ["BAP", "APS", "CEB", "search_volume"]
}
```

**Выходные данные:**
```python
{
    "brand_name": "johnscasino.com",
    "monitoring_status": "active",
    "last_check": "2024-01-20T10:00:00Z",
    "current_metrics": {
        "BAP": 0.15,
        "APS": 0.12,
        "CEB": 5000000,
        "trend": "rising"
    },
    "changes_24h": {
        "BAP": {"change": 0.02, "direction": "up"},
        "APS": {"change": 0.01, "direction": "up"}
    },
    "alerts": [
        {
            "type": "metric_drop",
            "metric": "BAP",
            "severity": "medium",
            "message": "BAP dropped by 5% in last 7 days"
        }
    ]
}
```

**Автоматизация:**
- Запуск по расписанию (каждый час/день)
- Сравнение с предыдущими значениями
- Генерация отчетов при значительных изменениях

---

### 3. **Competitor Tracker Node** (`src/nodes/tracker_node.py`)

**Назначение:** Отслеживание конкурентов клиентов

**Функционал:**
- Автоматическое определение конкурентов
- Мониторинг их метрик
- Сравнение с брендами клиентов
- Обнаружение новых конкурентов
- Анализ конкурентной позиции

**Инструменты:**
- `CompetitorIdentifier` - определение конкурентов
- `CompetitorMonitor` - мониторинг конкурентов
- `PositionAnalyzer` - анализ позиции

**Входные данные:**
```python
{
    "client_id": "client_123",
    "brand_name": "johnscasino.com",
    "country": "UK",
    "auto_discover": True  # Автоматически находить конкурентов
}
```

**Выходные данные:**
```python
{
    "brand_name": "johnscasino.com",
    "competitors": [
        {
            "name": "bet365.com",
            "bap": 0.35,
            "position": 1,
            "trend": "stable"
        },
        {
            "name": "betway.com",
            "bap": 0.20,
            "position": 2,
            "trend": "rising"
        }
    ],
    "client_position": 5,  # Позиция клиента среди конкурентов
    "market_share": 0.15,
    "recommendations": [
        "Focus on SEO to compete with bet365",
        "betway is growing fast - analyze their strategy"
    ]
}
```

---

### 4. **Report Generator Node** (`src/nodes/report_node.py`)

**Назначение:** Автоматическая генерация отчетов для клиентов

**Функционал:**
- Еженедельные/месячные отчеты
- Кастомные отчеты по запросу
- Визуализация данных
- Экспорт в PDF/Excel
- Email-рассылка отчетов

**Типы отчетов:**
1. **Brand Health Report** - здоровье бренда
2. **Competitive Analysis Report** - конкурентный анализ
3. **Market Opportunity Report** - возможности рынка
4. **Trends Report** - тренды индустрии
5. **Custom Report** - кастомный отчет

**Инструменты:**
- `ReportBuilder` - построение отчетов
- `VisualizationGenerator` - генерация графиков
- `PDFExporter` - экспорт в PDF
- `EmailSender` - отправка по email

**Входные данные:**
```python
{
    "client_id": "client_123",
    "report_type": "brand_health" | "competitive" | "market" | "trends" | "custom",
    "timeframe": "weekly" | "monthly" | "quarterly",
    "brands": List[str],  # Какие бренды включить
    "format": "pdf" | "excel" | "html",
    "send_email": True
}
```

**Выходные данные:**
```python
{
    "report_id": "report_789",
    "client_id": "client_123",
    "report_type": "brand_health",
    "generated_at": "2024-01-20T10:00:00Z",
    "timeframe": "weekly",
    "sections": [
        {
            "title": "Brand Metrics",
            "content": "...",
            "charts": [...]
        },
        {
            "title": "Competitive Position",
            "content": "...",
            "charts": [...]
        }
    ],
    "file_path": "/reports/client_123/report_789.pdf",
    "email_sent": True
}
```

---

### 5. **Alert Node** (`src/nodes/alert_node.py`)

**Назначение:** Генерация и отправка алертов клиентам

**Функционал:**
- Мониторинг критических изменений
- Генерация алертов при пороговых значениях
- Отправка уведомлений (email, SMS, Telegram)
- Настройка правил алертов
- История алертов

**Типы алертов:**
1. **Metric Drop** - падение метрики
2. **New Competitor** - появление нового конкурента
3. **Market Opportunity** - новая возможность на рынке
4. **Trend Change** - изменение тренда
5. **Custom Alert** - кастомный алерт

**Инструменты:**
- `AlertRuleEngine` - движок правил
- `NotificationSender` - отправка уведомлений
- `AlertHistory` - история алертов

**Входные данные:**
```python
{
    "client_id": "client_123",
    "alert_type": "metric_drop" | "new_competitor" | "market_opportunity" | "trend_change",
    "severity": "low" | "medium" | "high" | "critical",
    "message": str,
    "data": Dict[str, Any]
}
```

**Выходные данные:**
```python
{
    "alert_id": "alert_456",
    "client_id": "client_123",
    "alert_type": "metric_drop",
    "severity": "high",
    "message": "BAP dropped by 10% in last 7 days",
    "sent_at": "2024-01-20T10:00:00Z",
    "channels": ["email", "telegram"],
    "status": "sent"
}
```

---

### 6. **Maincard Integration Node** (`src/nodes/maincard_node.py`)

**Назначение:** Интеграция с Maincard API

**Функционал:**
- Синхронизация данных о клиентах
- Получение списка брендов клиентов
- Обновление статусов подписок
- Webhook обработка
- Двусторонняя синхронизация

**Инструменты:**
- `MaincardAPIClient` - клиент API Maincard
- `DataSyncer` - синхронизация данных
- `WebhookHandler` - обработка webhooks

**Входные данные:**
```python
{
    "action": "sync_clients" | "get_brands" | "update_subscription" | "handle_webhook",
    "maincard_account_id": Optional[str],
    "webhook_data": Optional[Dict]
}
```

**Выходные данные:**
```python
{
    "sync_status": "success",
    "clients_synced": 150,
    "brands_synced": 300,
    "last_sync": "2024-01-20T10:00:00Z"
}
```

---

## 💾 CRM База данных

### Схема таблиц:

```sql
-- Клиенты Maincard
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    maincard_account_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50),  -- basic, pro, enterprise
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'  -- active, inactive, suspended
);

-- Бренды клиентов
CREATE TABLE client_brands (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    brand_name VARCHAR(255) NOT NULL,
    brand_url VARCHAR(500),
    country VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    monitoring_enabled BOOLEAN DEFAULT TRUE,
    monitoring_frequency VARCHAR(50) DEFAULT 'daily'
);

-- Метрики брендов (исторические)
CREATE TABLE brand_metrics_history (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES client_brands(id),
    metric_type VARCHAR(50),  -- BAP, APS, CEB
    value FLOAT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Конкуренты
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES client_brands(id),
    competitor_name VARCHAR(255) NOT NULL,
    competitor_url VARCHAR(500),
    first_detected DATE,
    last_checked TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'  -- active, inactive
);

-- Отчеты
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    report_type VARCHAR(100),
    timeframe VARCHAR(50),
    generated_at TIMESTAMP DEFAULT NOW(),
    file_path VARCHAR(500),
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP
);

-- Алерты
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    brand_id INTEGER REFERENCES client_brands(id),
    alert_type VARCHAR(100),
    severity VARCHAR(50),
    message TEXT,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'  -- pending, sent, read
);

-- Взаимодействия с клиентами
CREATE TABLE client_interactions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    interaction_type VARCHAR(100),  -- query, report_request, alert_view
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Настройки мониторинга
CREATE TABLE monitoring_settings (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    brand_id INTEGER REFERENCES client_brands(id),
    metrics_to_track TEXT[],  -- Array of metric types
    alert_rules JSONB,  -- Rules for alerts
    frequency VARCHAR(50) DEFAULT 'daily',
    enabled BOOLEAN DEFAULT TRUE
);
```

---

## 🔄 Расширенный GraphState для CRM

```python
class GraphState(TypedDict):
    # ... существующие поля ...
    
    # CRM fields
    client_id: Optional[str]
    maincard_account_id: Optional[str]
    client_data: Optional[Dict[str, Any]]
    
    # Brand Management
    brand_name: Optional[str]
    brand_id: Optional[str]
    brands_list: List[Dict[str, Any]]
    
    # Monitoring
    monitoring_enabled: bool
    monitoring_frequency: Optional[str]
    last_monitoring_check: Optional[str]
    
    # Competitors
    competitors_list: List[Dict[str, Any]]
    competitor_analysis: Optional[Dict[str, Any]]
    
    # Reports
    report_type: Optional[str]
    report_data: Optional[Dict[str, Any]]
    report_generated: bool
    
    # Alerts
    alerts_list: List[Dict[str, Any]]
    alert_generated: bool
    
    # Maincard Integration
    maincard_sync_status: Optional[str]
    maincard_data: Optional[Dict[str, Any]]
```

---

## 🎨 Новые разделы Frontend (Streamlit)

### 1. **Client Dashboard** (`src/webapp/client_dashboard.py`)

**Разделы:**
- Обзор клиента
- Список брендов
- Метрики в реальном времени
- Последние отчеты
- Алерты

### 2. **Brand Monitoring** (`src/webapp/brand_monitoring.py`)

**Разделы:**
- Графики метрик (BAP, APS, CEB)
- История изменений
- Сравнение с конкурентами
- Настройки мониторинга

### 3. **Competitor Analysis** (`src/webapp/competitor_analysis.py`)

**Разделы:**
- Список конкурентов
- Сравнительная таблица
- Позиция на рынке
- Рекомендации

### 4. **Reports** (`src/webapp/reports.py`)

**Разделы:**
- История отчетов
- Генерация нового отчета
- Шаблоны отчетов
- Экспорт

### 5. **Alerts Center** (`src/webapp/alerts.py`)

**Разделы:**
- Активные алерты
- История алертов
- Настройка правил
- Уведомления

### 6. **Settings** (`src/webapp/settings.py`)

**Разделы:**
- Профиль клиента
- Настройки мониторинга
- Интеграции (Maincard)
- Уведомления

---

## 🔌 API Endpoints для интеграции

### REST API для Maincard:

```python
# Получить список клиентов
GET /api/v1/clients
GET /api/v1/clients/{client_id}

# Управление брендами
GET /api/v1/clients/{client_id}/brands
POST /api/v1/clients/{client_id}/brands
PUT /api/v1/brands/{brand_id}

# Метрики
GET /api/v1/brands/{brand_id}/metrics
GET /api/v1/brands/{brand_id}/metrics/history

# Конкуренты
GET /api/v1/brands/{brand_id}/competitors
POST /api/v1/brands/{brand_id}/competitors/discover

# Отчеты
GET /api/v1/clients/{client_id}/reports
POST /api/v1/clients/{client_id}/reports/generate

# Алерты
GET /api/v1/clients/{client_id}/alerts
POST /api/v1/alerts/rules

# Webhooks (для Maincard)
POST /api/v1/webhooks/maincard
```

---

## 📋 План реализации (по приоритетам)

### Фаза 1: Базовая CRM инфраструктура (2-3 недели)
- [ ] Создание схемы БД
- [ ] Client Management Node
- [ ] Maincard Integration Node
- [ ] Базовый API
- [ ] Аутентификация и авторизация

### Фаза 2: Мониторинг и трекинг (3-4 недели)
- [ ] Brand Monitoring Node
- [ ] Competitor Tracker Node
- [ ] Автоматизация мониторинга
- [ ] Dashboard для клиентов

### Фаза 3: Отчеты и алерты (2-3 недели)
- [ ] Report Generator Node
- [ ] Alert Node
- [ ] Email/SMS уведомления
- [ ] Экспорт отчетов

### Фаза 4: Frontend и UX (2-3 недели)
- [ ] Client Dashboard
- [ ] Brand Monitoring UI
- [ ] Competitor Analysis UI
- [ ] Reports UI
- [ ] Alerts Center

### Фаза 5: Интеграции и оптимизация (2 недели)
- [ ] Полная интеграция с Maincard
- [ ] Webhook обработка
- [ ] Кэширование
- [ ] Оптимизация производительности

### Фаза 6: Тестирование и документация (1-2 недели)
- [ ] Unit тесты
- [ ] Интеграционные тесты
- [ ] API документация
- [ ] User Guide

---

## 🎯 Ключевые преимущества для Maincard клиентов

1. **Автоматический мониторинг** - клиенты не нужно вручную отслеживать метрики
2. **Конкурентная разведка** - автоматическое обнаружение и анализ конкурентов
3. **Проактивные алерты** - уведомления о важных изменениях
4. **Автоматические отчеты** - регулярные отчеты без усилий
5. **Интеграция с Maincard** - все данные синхронизированы
6. **Data-driven решения** - помощь в принятии решений на основе данных

---

## 📊 Примеры использования

### Сценарий 1: Новый клиент Maincard
1. Клиент регистрируется в Maincard
2. Maincard отправляет webhook в Blask
3. Blask создает запись клиента
4. Автоматически начинает мониторинг его брендов
5. Генерирует первый отчет через неделю

### Сценарий 2: Падение метрик
1. Brand Monitoring Node обнаруживает падение BAP на 10%
2. Alert Node генерирует алерт
3. Отправляется email и Telegram уведомление клиенту
4. В отчете появляется рекомендация по улучшению

### Сценарий 3: Новый конкурент
1. Competitor Tracker обнаруживает новый бренд
2. Анализирует его метрики
3. Сравнивает с брендом клиента
4. Генерирует алерт и рекомендации

---

## 🔧 Технические детали

### Аутентификация:
- JWT токены для API
- OAuth для Maincard интеграции
- API ключи для клиентов

### Безопасность:
- Шифрование данных
- Rate limiting
- Audit logs
- GDPR compliance

### Масштабируемость:
- Очереди задач (Celery) для мониторинга
- Кэширование (Redis)
- Горизонтальное масштабирование
- CDN для статики

---

## 📝 Заключение

Этот план превращает Blask в полноценную CRM-систему для клиентов Maincard, которая:
- Автоматически отслеживает их бренды
- Помогает анализировать конкурентов
- Генерирует отчеты
- Отправляет алерты
- Интегрируется с Maincard

Реализация займет примерно 12-16 недель при работе одного разработчика, или 6-8 недель при работе команды из 2-3 человек.
