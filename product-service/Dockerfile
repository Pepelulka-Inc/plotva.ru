# Внимание !!!!!
# Докерфайл предназначен для сборки в контексте корневой директории.
# То есть его надо собирать из корня репозитория, а не из папки product-service. Например, вот так:
# docker build -f ./product-service/Dockerfile . 

FROM golang:1.23

WORKDIR /app

COPY ../go-common /app/go-common
COPY ../config.yml /app
WORKDIR /app/product-service

# Go mod and go sum
COPY product-service/go.mod product-service/go.sum .
# Installing dependencies
RUN go mod download
COPY product-service .
RUN CGO_ENABLED=0 GOOS=linux go build -o docker-entrypoint ./cmd

ENTRYPOINT ["./docker-entrypoint"]
CMD ["../config.yml"]
