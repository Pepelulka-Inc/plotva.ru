# Внимание !!!!!
# Докерфайл предназначен для сборки в контексте корневой директории.
# То есть его надо собирать из корня репозитория, а не из папки product-service. Например, вот так:
# docker build -f ./product-service/Dockerfile . 
#
# Для запуска сервиса в контейнере, надо смонтировать директорию с конфигом в /cfg, чтобы он мог найти файл /cfg/config.yml

FROM golang:1.23

WORKDIR /app

COPY ./go-common /app/go-common
WORKDIR /app/product-service

# Go mod and go sum
COPY product-service/go.mod product-service/go.sum ./
# Installing dependencies
RUN go mod download
COPY product-service .
RUN CGO_ENABLED=0 GOOS=linux go build -o docker-entrypoint ./cmd

ENTRYPOINT ["./docker-entrypoint"]
CMD ["/cfg/config.yml"]
