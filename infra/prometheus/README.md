# Prometheus

Для сбора метрик с windows хоста используется `windows_exporter` - https://github.com/prometheus-community/windows_exporter.

При запуске docker-compose файла для prometheus, надо указать имя конфига, которое будет использоваться в переменной окружения
`PROMETHEUS_CONFIG_NAME`. Например:

```sh
PROMETHEUS_CONFIG_NAME=win.prometheus.yml
```