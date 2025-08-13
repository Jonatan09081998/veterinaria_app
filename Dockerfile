# Usa una imagen de Python basada en Alpine
FROM python:3.12-alpine

# Instala las herramientas de compilación necesarias
RUN apk add --no-cache \
    build-base \
    linux-headers \
    gcc \
    musl-dev

# Establece el directorio de trabajo
WORKDIR /workspace

# Copia el archivo de requerimientos
COPY requirements.txt /workspace

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 81

# Comando para mantener el contenedor en ejecución (ajusta según tus necesidades)
CMD [ "python", "run.py" ]
