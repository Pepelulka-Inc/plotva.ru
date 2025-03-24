# plotva.ru

Пример конфига для запуска сервисов:

```yaml
db:
  host: localhost
  port: 5432
  user: ...
  password: ...
  db_name: ...
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
