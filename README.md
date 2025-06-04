# plotva.ru

**Бэкенд для интернет-магазина рыбалки**

Микросервисная архитектура с современным стеком технологий для высоконагруженного интернет-магазина товаров для рыбалки.

## Архитектура системы

## Технологический стек

### Backend Services
- **Go** - Auth Service, Product Service (Echo framework)
- **Python** - User Service (aiohttp), Order Service (FastAPI), Search Service (FastAPI), Elastic Update Service

### Базы данных и хранилища
- **PostgreSQL** - Основная реляционная БД для всех сервисов
- **ClickHouse** - Аналитическая OLAP БД для ETL процессов  
- **Elasticsearch** - Полнотекстовый поиск по товарам, продавцам, комментариям
- **S3** - Объектное хранилище для файлов пользователей

### Обмен данными и потоковая обработка
- **Apache Kafka** - Event streaming платформа

### DevOps и инфраструктура
- **Docker & Docker Compose** - Контейнеризация и запуск
- **Graffana + Prometheus + Loki + Alloy** - Полный стек Observability

## Сервисы и их роли

### Auth Service (Go/Echo) 
**Функции:**
- Выдача JWT токенов
- OAuth интеграция с Yandex
- Создание пользователей

**Эндпоинты:**
- `POST /api/user/create` - Создание пользователя
- `POST /api/user/login/uuid` - Вход по UUID
- `POST /api/user/login/phone` - Вход по номеру телефона  
- `GET /api/user/login/oauth` - OAuth авторизация через Yandex

### Product Service (Go/Echo)
**Функции:**
- Управление каталогом товаров и категорий
- Фильтрация и поиск товаров
- Отправка событий просмотра товаров в Kafka
- CRUD операции с товарами

**Эндпоинты:**
- `GET /api/product/category/all` - Все категории
- `POST /api/product/category/add` - Добавить категорию
- `POST /api/product/add` - Добавить товар
- `POST /api/product/filter` - Фильтрация товаров
- `GET /api/product/:id` - Товар по ID
- `GET /api/product/view/:user_id/:id` - Просмотр товара (отправляет событие в Kafka)

### User Service (Python/aiohttp) 
**Функции:**
- Управление профилями пользователей
- Корзина покупок
- Интеграция с S3 для загрузки файлов

**Эндпоинты:**
- `PUT /users/{user_id}` - Обновить пользователя
- `POST /users` - Создать пользователя
- `GET /users/list` - Список всех пользователей
- `GET /cart/{user_id}` - Корзина пользователя
- `POST /cart/add` - Добавить в корзину
- `DELETE /cart/clear` - Очистить корзину

### Order Service (Python/FastAPI)
**Функции:**
- Обработка заказов
- Интеграция с системами оплаты
- Отправка событий заказов в Kafka для аналитики

### Search Service (Python/FastAPI)
**Функции:**
- Полнотекстовый поиск по товарам
- Поиск по категориям
- Поиск продавцов
- Поиск в комментариях
- Интеграция с Elasticsearch

**Эндпоинты:**
- `GET /products?name=...` - Поиск товаров по названию
- `GET /products?category=...` - Поиск по категории
- `GET /sellers?name=...` - Поиск продавцов
- `GET /comments?content=...` - Поиск в комментариях

### Elastic Update Service (Python)
**Функции:**
- Потребление событий из Kafka
- Обновление индексов Elasticsearch в реальном времени
- Обработка топиков: `products`, `sellers`, `comments`
- Автоматическая инициализация индексов

## ETL система (Kafka + ClickHouse)

### Архитектура потоковой обработки данных в системе plotva.ru

**Центральная шина сообщений Apache Kafka**

Система использует Apache Kafka как центральную платформу для потоковой обработки данных. Основные топики: `product_views` (события просмотра товаров), `orders` (события заказов), `products`, `sellers`, `comments` (изменения данных для поиска). Kafka обеспечивает надежную доставку сообщений в формате JSON между микросервисами, позволяя Product Service отправлять события просмотров, Order Service - события заказов, а различным потребителям обрабатывать эти данные асинхронно в реальном времени.

**Аналитическая обработка через ClickHouse**

ClickHouse потребляет события из Kafka через специальные Kafka Engine таблицы (`kafka_product_views`, `kafka_orders`) и автоматически перенаправляет данные в аналитические MergeTree таблицы (`product_views`, `orders`) с помощью Materialized Views. Это обеспечивает реальное время обновления аналитических данных для построения отчетов по популярности товаров, анализа продаж, создания рекомендательных систем и бизнес-аналитики без влияния на производительность основных сервисов.


### ClickHouse Analytics

**Таблицы для аналитики:**
- `product_views` - Просмотры товаров для построения рекомендаций
- `orders` - История заказов для анализа продаж

**Materialized Views:**
- Автоматическое потребление данных из Kafka
- Реальное время обновления аналитических данных
- Оптимизация под аналитические запросы с MergeTree engine

## Взаимодействие сервисов

### Синхронное взаимодействие
- **HTTP API** между сервисами через Nginx
- **JWT авторизация** для защищённых эндпоинтов
- **PostgreSQL** как единое хранилище данных

### Асинхронное взаимодействие  
- **Kafka Events** для событий просмотров и заказов
- **Elasticsearch Updates** в реальном времени
- **ClickHouse Ingestion** для аналитики

## Конфигурация

### Пример конфига сервисов

```yaml
db:
  host: localhost
  port: 5432
  user: pepe
  password: pepe
  db_name: pepe

auth-service:
  db_min_conns: 2
  db_max_conns: 10
  port: 8081
  oauth:
    client_id: pepe
    client_secret: pepe
    redirect_url: "http://localhost:8081/api/user/login/callback"
    scopes:
      - "login:default_phone"
    auth_url_endpoint: "https://oauth.yandex.ru/authorize"
    token_url_endpoint: "https://oauth.yandex.ru/token"
    
jwt:
  secret: abcdef

clickhouse:
  host: localhost
  port: 9000
  user: ...
  password: ...
  db_name: ...

kafka:
  brokers:
    - "localhost:9092"
  max_retry: 5

product-service:
  db_min_conns: 2
  db_max_conns: 10
  port: 8080
```

**Также многие сервисы конфигурируются переменными окружения**

## Запуск проекта

### Предварительные требования
- Docker и Docker Compose
- Go 1.21+
- Python 3.9+

### Настройка pre-commit для разработчиков
```bash
pip install pre-commit
pre-commit install
```

### Запуск проекта

Запуск проекта регулируется самописным скриптом для запуска.
Чтобы запустить весь проект:
```bash
cd infra/_scripts/starter
go run ./cmd ../start.yaml start
```

Конфигурация для запуска в `infra/_scripts/start.yaml`

## Observability

- **Grafana** - Дашборды и визуализация метрик
- **Prometheus** - Сбор метрик из сервисов
- **Loki** - Централизованные логи
- **Tempo** - Distributed tracing
- **OpenTelemetry** - Инструментирование сервисов

## Нагрузочное тестирование

Доступны тесты производительности с инструментом **k6**:
```bash
cd tests/load-testing/product-service/1_filter_test
npm install
k6 run
```
