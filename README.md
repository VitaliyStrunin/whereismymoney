# WhereIsMyMoney

Backend-сервис для учёта личных расходов. Пользователь может управлять расходами, категориями и тегами через REST API. Данные изолированы по владельцу на уровне бизнес-логики и SQL-запросов.

## Стек

Python 3.12+, Flask, SQLAlchemy 2, PostgreSQL 18, Psycopg 3, Alembic, Pydantic 2, PyJWT, pytest, Ruff, uv, Docker Compose.

## Возможности

- регистрация и вход по email и паролю;
- JWT access token и refresh sessions с ротацией;
- отзыв refresh session при logout;
- CRUD для расходов, категорий и тегов;
- связь расходов с категориями и тегами;
- limit/offset-пагинация;
- частичное обновление расходов;
- изоляция данных между пользователями;

## Архитектура

~~~text
backend/
├── api/              HTTP-слой и Flask blueprints
├── core/             настройки, безопасность, исключения
├── database/         SQLAlchemy Base и фабрика сессий
├── models/           SQLAlchemy-модели
├── repositories/     запросы к базе
├── schemas/          Pydantic DTO
├── services/         бизнес-логика и транзакции
└── main.py           application factory

alembic/              миграции
tests/                API и тесты
~~~

Основной поток обработки:

~~~text
Route → DTO → Service → Repository → SQLAlchemy → PostgreSQL
~~~

Application factory принимает фабрику сессий, поэтому тесты используют отдельную базу.

## Запуск через Docker

Требования: Docker Desktop или Docker Engine с Compose, свободные порты 8000 и 5433.

Создайте локальный файл окружения:

~~~powershell
Copy-Item .env.example .env
~~~

Запустите приложение:

~~~bash
docker compose up --build
~~~

Compose поднимает PostgreSQL, ждёт healthcheck базы, применяет миграции и запускает Flask.

API:

~~~text
http://localhost:8000
~~~

Внутри Docker приложение подключается к PostgreSQL по адресу db:5432. С хост-компьютера база доступна по адресу localhost:5433.

## Конфигурация

Настройки загружаются из переменных окружения и файла .env через pydantic-settings.

### База данных

| Переменная | Описание |
|---|---|
| DB_USER | Пользователь PostgreSQL |
| DB_PASSWORD | Пароль PostgreSQL |
| DB_HOST | Адрес PostgreSQL |
| DB_PORT | Порт PostgreSQL |
| DB_NAME | Имя базы приложения |

Для тестов используются отдельные TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_HOST, TEST_DB_PORT и TEST_DB_NAME. Тестовая конфигурация проверяет, что тестовая и основная базы не совпадают.

### Авторизация

| Переменная | Описание |
|---|---|
| JWT_SECRET_KEY | Секрет подписи access token |
| JWT_ACCESS_TOKEN_TTL_MINUTES | Время жизни access token |
| JWT_ALGORITHM | Алгоритм JWT |
| REFRESH_TOKEN_TTL_DAYS | Время жизни refresh session |
| REFRESH_TOKEN_COOKIE_NAME | Имя refresh cookie |
| REFRESH_TOKEN_SECURE | Secure-флаг cookie |
| REFRESH_TOKEN_SAMESITE | Политика SameSite |
| REFRESH_TOKEN_SECRET | Секрет refresh-механизма |

Демонстрационные секреты подходят только для локальной разработки. Для production нужно задать собственные значения и включить REFRESH_TOKEN_SECURE=true.

## API

Защищённые endpoints требуют заголовок:

~~~http
Authorization: Bearer <access_token>
~~~

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | /auth/register | Регистрация пользователя |
| POST | /auth/login | Вход и выдача access token |
| POST | /auth/refresh | Обновление токенов |
| POST | /auth/logout | Отзыв refresh session |
| GET | /auth/me | Текущий пользователь |
| GET | /categories | Список категорий |
| POST | /categories | Создание категории |
| GET | /categories/{id} | Получение категории |
| PATCH | /categories/{id} | Изменение категории |
| DELETE | /categories/{id} | Удаление категории |
| GET | /tags | Список тегов |
| POST | /tags | Создание тега |
| GET | /tags/{id} | Получение тега |
| PATCH | /tags/{id} | Изменение тега |
| DELETE | /tags/{id} | Удаление тега |
| GET | /expenses | Список расходов |
| POST | /expenses | Создание расхода |
| GET | /expenses/{id} | Получение расхода |
| PATCH | /expenses/{id} | Частичное обновление |
| DELETE | /expenses/{id} | Удаление расхода |

Списки поддерживают параметры limit и offset. Максимальное значение limit — 100.

Пример создания расхода:

~~~json
{
  "amount": "1250.50",
  "description": "Ужин",
  "expense_date": "2026-07-21",
  "category_id": 2,
  "tag_ids": [4, 5]
}
~~~

## Модель данных

Таблицы:

- users;
- categories;
- tags;
- expenses;
- expense_tags;
- refresh_sessions.

Основные ограничения:

- email уникален;
- названия категорий и тегов уникальны для конкретного пользователя;
- пользовательские данные удаляются каскадно;
- используемая категория защищена ограничением RESTRICT;
- refresh token хранится в базе в виде хеша.

## Безопасность

Пароли хешируются через scrypt.

JWT access token содержит идентификатор пользователя, тип токена, время выпуска и срок действия. При обработке проверяются подпись, алгоритм, тип и срок действия.

Refresh token передаётся через HttpOnly cookie, а в PostgreSQL хранится хеш. При обновлении токенов старая сессия отзывается и создаётся новая.

## Тесты

Тестовый контур использует Flask test client, отдельную PostgreSQL-базу и Alembic-миграции. Проверяются CRUD-операции, валидация, пагинация, авторизация, ошибки и межпользовательская изоляция.