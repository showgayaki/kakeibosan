FROM mariadb:10.11.3-jammy

RUN apt-get update -y && apt-get upgrade -y
COPY kakeibosan.sql //docker-entrypoint-initdb.d/
