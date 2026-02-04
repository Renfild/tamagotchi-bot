# 🐾 Tamagotchi Bot

Продвинутый Telegram-бот с мини-приложением для генерации и ухода за виртуальными питомцами — полноценный тамагочи с социальными функциями, мини-играми и экономикой.

## 🏗 Архитектура

### Backend
- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot
- **FastAPI** — REST API
- **PostgreSQL** — основная база данных (asyncpg)
- **Redis** — кеш, сессии, очереди
- **Celery** — фоновые задачи
- **MinIO/S3** — хранение изображений
- **WebSocket** — real-time обновления

### Frontend (Mini App)
- **React 18 + TypeScript**
- **Telegram WebApp API**
- **Framer Motion** — анимации
- **Zustand** — state management

## 🚀 Быстрый старт

### Требования
- Docker 20.10+
- Docker Compose 2.0+
- Make (опционально)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/tamagotchi-bot.git
cd tamagotchi-bot
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
# Отредактируйте .env, добавьте свои значения
```

3. Запустите сервисы:
```bash
docker-compose up -d
```

4. Выполните миграции:
```bash
docker-compose exec api alembic upgrade head
```

5. Откройте бота в Telegram: `@your_bot_username`

## 📁 Структура проекта

```
tamagotchi-bot/
├── backend/                 # Backend приложение
│   ├── bot/                # Telegram бот (aiogram)
│   │   ├── handlers/       # Обработчики команд
│   │   ├── keyboards/      # Клавиатуры
│   │   ├── middlewares/    # Middleware
│   │   └── utils/          # Утилиты
│   ├── api/                # FastAPI приложение
│   │   └── routes/         # API endpoints
│   ├── core/               # Ядро приложения
│   │   ├── config.py       # Конфигурация
│   │   └── database.py     # База данных
│   ├── models/             # SQLAlchemy модели
│   ├── tasks/              # Celery задачи
│   ├── migrations/         # Alembic миграции
│   ├── requirements.txt    # Python зависимости
│   └── Dockerfile.*        # Docker файлы
├── frontend/               # React Mini App
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы
│   │   ├── store/          # Zustand stores
│   │   ├── hooks/          # Custom hooks
│   │   └── api/            # API клиент
│   ├── public/
│   └── package.json
├── infra/                  # Инфраструктура
│   └── nginx/              # Nginx конфигурация
├── docker-compose.yml      # Docker Compose
└── README.md
```

## 🤖 Функционал бота

### Основные команды
- `/start` — онбординг, выбор языка
- `/pet` — статус питомца
- `/inventory` — инвентарь
- `/shop` — магазин
- `/games` — мини-игры
- `/friends` — друзья
- `/breeding` — разведение
- `/arena` — PvP битвы
- `/quests` — квесты
- `/achievements` — достижения
- `/leaderboard` — рейтинг
- `/settings` — настройки
- `/help` — помощь

### Система уведомлений
- Голод (3 стадии)
- Настроение
- Здоровье (болезни)
- Сон
- События и достижения
- Экстренные уведомления

## 📱 Mini App — Экраны

1. **Splash Screen** — загрузка и авторизация
2. **Pet Generator** — создание питомца
3. **Pet Hub** — главный экран с питомцем
4. **Inventory** — инвентарь предметов
5. **Shop** — магазин
6. **Games** — мини-игры
7. **Friends** — социальные функции
8. **Arena** — PvP битвы
9. **Quests** — квесты
10. **Achievements** — достижения
11. **Settings** — настройки

## 🎮 Игровые механики

### Питомец
- 10 типов питомцев
- 6 уровней редкости
- 8 типов личности
- Система эволюции (5 стадий)
- Кастомизация внешности

### Статистика
- 🍖 Сытость (0-100)
- 😊 Настроение (0-100)
- ❤️ Здоровье (0-100)
- ⚡ Энергия (0-100)
- 🧼 Гигиена (0-100)

### Экономика
- 🪙 Монеты — основная валюта
- 💎 Кристаллы — премиум валюта
- 🎟️ Арена-токены — для PvP

### Мини-игры
- Бег за едой
- Пазл
- Ритм-игра
- Рыбалка
- Лабиринт
- PvP Дуэль

## 🔧 Разработка

### Локальная разработка

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запуск бота
python -m bot.main

# Запуск API
uvicorn api.main:app --reload

# Запуск Celery
celery -A tasks.worker worker --loglevel=info
celery -A tasks.scheduler beat --loglevel=info
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Миграции базы данных
```bash
# Создать миграцию
docker-compose exec api alembic revision --autogenerate -m "description"

# Применить миграции
docker-compose exec api alembic upgrade head

# Откатить миграцию
docker-compose exec api alembic downgrade -1
```

## 🧪 Тестирование

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📊 Мониторинг

- Prometheus метрики: `/metrics`
- Flower (Celery): `http://localhost:5555`
- API Docs: `http://localhost:8000/docs`

## 🚀 Деплой

### Через GitHub Actions
1. Добавьте секреты в репозиторий:
   - `SSH_PRIVATE_KEY`
   - `SERVER_HOST`
   - `SERVER_USER`

2. Push в main ветку запустит CI/CD pipeline

### Ручной деплой
```bash
# На сервере
git pull
docker-compose pull
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## 📝 Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | - |
| `DATABASE_URL` | URL PostgreSQL | - |
| `REDIS_URL` | URL Redis | - |
| `JWT_SECRET` | Секрет для JWT | - |
| `MINIO_ENDPOINT` | Endpoint MinIO | minio:9000 |
| `WEBAPP_URL` | URL Mini App | - |

## 🤝 Contributing

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.

## 👥 Авторы

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) — Telegram Bot Framework
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Web Framework
- [Telegram WebApps](https://core.telegram.org/bots/webapps) — Mini Apps Platform
