FROM postgres:latest

# Copia el script SQL en el directorio de inicialización de Docker
COPY init.sql /docker-entrypoint-initdb.d/

# El resto se manejará automáticamente por la imagen base de PostgreSQL
