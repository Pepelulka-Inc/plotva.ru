# plotva.ru

Пример конфига для запуска сервисов:

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
