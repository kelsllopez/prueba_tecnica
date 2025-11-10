#### **1. Introducción y Contexto del Desafío**

**El Problema a Resolver:**
Tu misión es construir un microservicio que procesa datos de telemetría de una máquina forestal para generar "Informes de Resguardo". Un resguardo ocurre cuando la máquina se apaga fuera del horario de turno. El servicio debe analizar la última ubicación y, usando un Shapefile de caminos, determinar si el resguardo fue seguro (a mas de 50 metros de un camino) o inseguro.

#### **2. Recursos Proporcionados**

Te entregaremos un paquete `.zip` con los siguientes archivos:

1.  `LocationMessages-844585_page{1-2}.xml`: El historial de posiciones de la máquina.
2.  `EngineStatusMessages-844585.xml`: El historial de eventos de motor de la máquina.
3.  `CAMINOS_7336.shp`: La capa de caminos (incluye archivos .shx, .dbf, etc.).

#### **3. Requisitos Funcionales y Técnicos**

Tu servicio, expuesto a través de una API REST, debe:

1.  **Iniciar el Procesamiento de Datos (`POST /data-processing/`):**
    *   Debes crear un endpoint específico para iniciar la tarea de procesamiento de los archivos.
    *   **Método y URL:** `POST /data-processing/`
    *   **Cuerpo de la Petición:** Esta petición no necesita recibir un cuerpo (body). Su única finalidad es actuar como un disparador.
    *   **Lógica del Servidor:** Cuando este endpoint es llamado, el servidor debe ejecutar el proceso completo:
        a.  Localizar y leer los archivos `LocationMessages-844585_page{1-2}.xml` y `EngineStatusMessages-844585.xml` que se encuentran en el servicio.
        b.  Aplicar la **Lógica de Resguardo**: identificar los eventos de "motor apagado" que ocurran **fuera del horario de turno (08:30 - 19:30)**.
        c.  Para el resguardo, aplicar la **Lógica de Distancia**: calcular la distancia en metros a la capa de caminos. Un resguardo es **inseguro** si la distancia es **menor a 50 metros**.
        d.  Crear y guardar los `Informes de Resguardo` correspondientes en la base de datos.
    *   **Respuesta de la API:** La respuesta a esta petición `POST` debe ser un código de estado `202 Accepted` y un cuerpo JSON simple que confirme que la tarea ha comenzado, por ejemplo:
        ```json
        {
          "message": "Data processing initiated successfully."
        }
        ```


2.  **Consultar Informes (`GET /safeguard-reports/`):**
    *   Crear un endpoint para listar los informes generados.
    *   **Contrato de Respuesta (Requisito Clave):** La respuesta debe ser un array de objetos JSON con la siguiente estructura exacta:

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

3.  **Actualizar Estado (`PATCH /safeguard-reports/{id}/`):**
    *   Crear un endpoint que permita un **borrado suave (soft delete)**.
    *   Debe aceptar un cuerpo `PATCH` como `{ "is_active": false }`.
    *   La lista de informes por defecto solo debe mostrar los registros con `is_active: true`.

4.  **Arquitectura y Stack:**
    *   **Framework:** Django y Django Ninja.
    *   **Análisis Geoespacial:** GeoPandas, librería similar o Postgres con QGIS.
    *   **Contenerización:** La solución completa debe estar dockerizada.

#### **4. Entregables**

Un enlace a un repositorio de Git que contenga:
1.  El código fuente completo del proyecto.
2.  `Dockerfile` y `docker-compose.yml`.
3.  Un `README.md` con instrucciones claras para:
    *   Configurar el entorno con Docker.
    *   Ejecutar el endpoint de procesamiento de datos.
    *   Ejemplos de cómo consultar la API (ej. con cURL).

#### **5. Criterios de Evaluación**

1.  **Cumplimiento del Contrato de la API:** ¿El endpoint `GET` devuelve la estructura JSON exacta que se especificó?
2.  **Correctitud Funcional:** ¿La lógica de identificación de resguardos y el cálculo de distancia son correctos?
3.  **Calidad del Código y Dockerización:** Claridad, buenas prácticas y reproducibilidad del entorno.
