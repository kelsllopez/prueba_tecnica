# Microservicio de Informes de Resguardo Forestal

Sistema de procesamiento de telemetría para máquinas forestales que genera informes de resguardo basados en eventos de apagado de motor fuera del horario de turno y análisis geoespacial de distancia a caminos.

##  Descripción

Este microservicio analiza datos de telemetría de máquinas forestales para:
- Identificar eventos de "resguardo" (motor apagado fuera del horario 08:30 - 19:30)
- Calcular la distancia de cada resguardo a los caminos más cercanos
- Clasificar resguardos como **seguros** (>50m de caminos) o **inseguros** (<50m)
- Proporcionar una API REST para consultar y gestionar informes

##  Arquitectura

- **Framework:** Django + Django Ninja
- **Base de Datos:** PostgreSQL con PostGIS
- **Análisis Geoespacial:** GeoPandas
- **Contenedores:** Docker + Docker Compose

##  Requisitos Previos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)

##  Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/kelsllopez/prueba_tecnica.git
cd prueba_tecnica
```

### 2. Estructura de archivos

El proyecto tiene la siguiente estructura:

```
prueba_tecnica/
├── data/                              # Archivos de datos
│   ├── LocationMessages-844585_page_1.xml
│   ├── LocationMessages-844585_page_2.xml
│   ├── EngineStatusMessages-844585.xml
│   ├── CAMINOS_7336.shp
│   ├── CAMINOS_7336.shx
│   ├── CAMINOS_7336.dbf
│   └── CAMINOS_7336.prj
├── server/                            # Aplicación Django
│   ├── api.py
│   ├── models.py
│   ├── services.py
│   └── ...
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### 3. Levantar los servicios

```bash
# Construir y levantar los contenedores
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up -d --build
```

La aplicación estará disponible en: `http://localhost:8000`

### 4. Aplicar migraciones (primera vez)

```bash
docker-compose exec web python manage.py migrate
```

## 🔧 Uso de la API

### 1. Iniciar el Procesamiento de Datos

Este endpoint lee los archivos XML, identifica resguardos y calcula distancias.

**Endpoint:** `POST /api/data-processing/`

```bash
curl -X POST http://localhost:8000/api/data-processing/ \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**
```json
{
  "message": "Data processing initiated successfully."
}
```

**Código de estado:** `202 Accepted`

### 2. Consultar Informes de Resguardo

Obtiene la lista de todos los informes activos.

**Endpoint:** `GET /api/safeguard-reports/`

```bash
curl -X GET http://localhost:8000/api/safeguard-reports/
```

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "machine_serial": "844585",
    "report_datetime": "2024-11-04T21:05:00Z",
    "engine_off_timestamp": "2024-11-04T20:05:00Z",
    "is_safe": false,
    "location": {
      "latitude": -37.12345,
      "longitude": -72.56789
    },
    "distance_to_road_m": 35.5,
    "is_active": true
  }
]
```

### 3. Desactivar un Informe (Soft Delete)

Realiza un borrado suave del informe especificado.

**Endpoint:** `PATCH /api/safeguard-reports/{id}/`

```bash
curl -X PATCH http://localhost:8000/api/safeguard-reports/1/ \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "machine_serial": "844585",
  "report_datetime": "2024-11-04T21:05:00Z",
  "engine_off_timestamp": "2024-11-04T20:05:00Z",
  "is_safe": false,
  "location": {
    "latitude": -37.12345,
    "longitude": -72.56789
  },
  "distance_to_road_m": 35.5,
  "is_active": false
}
```

##  Lógica de Negocio

### Definición de Resguardo

Un resguardo ocurre cuando:
- El motor de la máquina se apaga (`EngineStatus == 0`)
- El evento ocurre **fuera del horario de turno** (antes de 08:30 o después de 19:30)

### Clasificación de Seguridad

- **Resguardo Seguro** (`is_safe: true`): Distancia a camino ≥ 50 metros
- **Resguardo Inseguro** (`is_safe: false`): Distancia a camino < 50 metros

### Cálculo de Distancia

Se utiliza GeoPandas para:
1. Cargar el shapefile de caminos (CAMINOS_7336.shp)
2. Convertir las coordenadas del resguardo a un punto geoespacial
3. Calcular la distancia mínima al camino más cercano usando proyección UTM

##  Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo del servicio web
docker-compose logs -f web

# Detener los servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos de BD)
docker-compose down -v

# Acceder a la shell de Django
docker-compose exec web python manage.py shell

# Crear un superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar tests
docker-compose exec web python manage.py test
```

##  Verificación del Sistema

### 1. Verificar que los contenedores están corriendo

```bash
docker-compose ps
```

Deberías ver algo como:
```
NAME                COMMAND                  SERVICE             STATUS
project-web-1       "python manage.py ru…"   web                 running
project-db-1        "docker-entrypoint.s…"   db                  running
```

### 2. Verificar la base de datos

```bash
docker-compose exec db psql -U postgres -d safeguards -c "\dt"
```

### 3. Probar el flujo completo

```bash
# 1. Procesar datos
curl -X POST http://localhost:8000/api/data-processing/

# 2. Esperar unos segundos y consultar informes
curl -X GET http://localhost:8000/api/safeguard-reports/

# 3. Desactivar un informe
curl -X PATCH http://localhost:8000/api/safeguard-reports/1/ \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```
---

## 🧩 Acceso al Panel Administrativo

Al levantar los contenedores, el sistema crea un superusuario por defecto para pruebas locales:

| Campo | Valor |
|-------|--------|
| **Usuario** | `admin` |
| **Contraseña** | `admin` |
| **URL** | [http://localhost:8000/admin/](http://localhost:8000/admin/) |


---

##  Estructura del Proyecto

```
.
├── data/                       # Archivos de datos (XML y Shapefiles)
│   ├── CAMINOS_7336.*         # Shapefile de caminos
│   ├── EngineStatusMessages-844585.xml
│   ├── LocationMessages-844585_page_1.xml
│   └── LocationMessages-844585_page_2.xml
├── server/                     # Aplicación Django principal
│   ├── api.py                 # Endpoints de la API (Django Ninja)
│   ├── models.py              # Modelos de datos
│   ├── services.py            # Lógica de negocio
│   ├── schemas.py             # Esquemas de respuesta
│   └── ...
├── prueba_tecnica/             # Configuración de Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── docker-compose.yml         # Orquestación de contenedores
├── Dockerfile                 # Imagen de la aplicación
├── requirements.txt           # Dependencias de Python
├── manage.py                  # CLI de Django
└── README.md                  # Este archivo
```

##  Troubleshooting

### Problema: Los contenedores no inician

```bash
# Limpiar y reconstruir
docker-compose down -v
docker-compose up --build
```

### Problema: Error al leer archivos XML o Shapefile

Verifica que:
1. Los archivos existen en el directorio `data/`
2. Los permisos de lectura son correctos
3. Los paths en el código coinciden con la estructura

### Problema: Error de conexión a la base de datos

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Ver logs de la base de datos
docker-compose logs db
```

##  Notas Adicionales

- El sistema usa zonas horarias (timezone-aware datetimes)
- Las coordenadas se proyectan a UTM Zone 18S (EPSG:32718) para cálculos precisos
- Los informes con `is_active: false` no aparecen en el listado por defecto
- El procesamiento es idempotente: puedes ejecutarlo múltiples veces

##  Licencia

MIT License

##  Autor

**Kels López**
- GitHub: [@kelsllopez](https://github.com/kelsllopez)
- Repositorio: [prueba_tecnica](https://github.com/kelsllopez/prueba_tecnica)

---

## 🧾 Evaluación

Este proyecto fue desarrollado como parte de una **prueba técnica para Q-Forest**, cumpliendo los requisitos de:
- Procesamiento asíncrono de datos geoespaciales
- API REST documentada con Swagger (Django Ninja)
- Entorno completamente dockerizado y reproducible
