# Dockerfile — versión estable para GeoPandas en Django
FROM python:3.11-slim

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    proj-bin \
    libproj-dev \
    python3-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Variables necesarias para GDAL y PROJ
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_VERSION=3.6.0
ENV PROJ_LIB=/usr/share/proj

# Crea directorio del proyecto
WORKDIR /app

# Copia dependencias primero para usar cache de Docker
COPY requirements.txt /app/

# Forzamos instalación de librerías geoespaciales con sus extras
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir --no-binary :all: shapely
RUN pip install --no-cache-dir geopandas fiona pyproj rtree
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . /app

# Expone el puerto 8000
EXPOSE 8000

# Comando final
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
