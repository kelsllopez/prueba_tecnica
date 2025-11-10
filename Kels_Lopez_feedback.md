# Revisión de Prueba Técnica: Kels López

**Rol:** Desarrollador Backend Python/Django (con especialización en GIS)
**Fecha de Revisión:** 2025-11-10
**Revisor:** Richard Romero `PO Qforest`
**Enlace al Repositorio del Candidato:** `https://github.com/kelsllopez/prueba_tecnica`

---

## 1. Contexto y Misión de la Prueba Técnica

*   **Misión de la Prueba:** El objetivo de esta prueba era evaluar la capacidad del candidato para diseñar e implementar una API REST simple en Django, modelar datos, escribir código limpio y estructurado, y demostrar su dominio en el procesamiento de datos geoespaciales para resolver un problema de negocio específico.
*   **Problema Específico:** Se le pidió crear un microservicio para procesar datos de telemetría de maquinaria forestal. El servicio debía identificar "Informes de Resguardo" (apagados de motor fuera de turno), y utilizando un Shapefile de caminos, determinar si la ubicación del resguardo era segura (a más de 50 metros de un camino). La solución debía ser expuesta a través de una API REST y estar completamente dockerizada.

---

## 2. Checklist de Criterios de Evaluación

**Instrucciones para el Revisor:**
Evalúa cada uno de los siguientes puntos asignando una puntuación de 1 (deficiente) a 5 (excelente). Añade comentarios específicos que justifiquen tu puntuación en la columna de "Observaciones".

---

### **A. Funcionalidad y Cumplimiento de Requisitos (¿Resuelve el problema?)**

| Criterio | Puntuación (1-5) | Observaciones |
| :--- | :--- | :--- |
| **Cumplimiento de Requisitos Básicos:** ¿La solución cumple con todos los requisitos funcionales explícitamente pedidos? | 5 | Cumple al 100% con los 3 endpoints solicitados (`POST`, `GET`, `PATCH`). La lógica de negocio implementada (horarios de turno, distancia de seguridad) es exactamente la que se pidió. El contrato JSON de la respuesta del endpoint `GET` es idéntico al especificado. |
| **Manejo de Casos de Éxito:** ¿El "camino feliz" funciona como se espera? | 5 | Sí, el flujo completo desde la ingesta de datos con el `POST` hasta la consulta con el `GET` funciona a la perfección. La lógica de cálculo es correcta y los resultados generados son consistentes con los datos de entrada. |
| **Manejo de Casos de Borde/Errores:** ¿La API maneja entradas inválidas o situaciones de error de forma controlada? | 5 | Excelente. El servicio valida la existencia de los archivos de datos antes de procesar. La lógica de búsqueda de la última ubicación previene errores si no hay posiciones antes de un evento de apagado. El endpoint `PATCH` utiliza `get_object_or_404` para manejar IDs inexistentes. |
| **Instrucciones de Uso:** ¿El `README.md` del candidato es claro y permite levantar y probar el proyecto sin dificultad? | 3 | Excepcional. El `README.md` es uno de los más completos y claros que hemos visto. Incluye arquitectura, instalación, ejemplos de `curl`, explicación de la lógica, troubleshooting y una estructura del proyecto. Facilita enormemente la revisión y prueba. Unicamente el dockerfile no quedo bien definido|

**Puntuación Parcial (Funcionalidad):** `18/20`

---

### **B. Calidad del Código y Arquitectura (¿Cómo lo resolvió?)**

| Criterio | Puntuación (1-5) | Observaciones |
| :--- | :--- | :--- |
| **Claridad y Legibilidad:** ¿El código es fácil de leer y entender? ¿Los nombres de variables y funciones son descriptivos? | 5 | El código es muy limpio, bien estructurado y fácil de seguir. Los nombres de variables (`df_engine`, `is_off_event`) son autoexplicativos. El uso de un script exploratorio (`data/camiones.py`) es una buena práctica. |
| **Estructura del Proyecto:** ¿El proyecto sigue una estructura lógica y coherente (ej. separando modelos, vistas, etc.)? | 5 | Perfecta. La estructura del proyecto es profesional y escalable. Sigue las mejores prácticas de Django, separando la configuración del proyecto de la aplicación (`server`). La organización interna de la app es ejemplar. |
| **Principios de Diseño (SOLID/Clean):** ¿Demuestra una comprensión de la separación de responsabilidades? ¿La lógica de negocio está acoplada a la vista o está en una capa de servicio/caso de uso? | 5 | Sobresaliente. La separación de la lógica de negocio en un `services.py` es la decisión arquitectónica más importante y acertada. Demuestra un entendimiento maduro de arquitecturas limpias, manteniendo los endpoints (`api.py`) delgados y la lógica de negocio agnóstica al framework y reutilizable. |
| **Modelado de Datos:** ¿Los modelos de Django están bien definidos? ¿Usa los tipos de campo correctos? | 4 | El modelo `SafeguardReport` está bien definido con los tipos de datos correctos (`DateTimeField`, `FloatField`, etc.). No utiliza un campo geoespacial (`PointField` de PostGIS) para la ubicación, optando por `FloatField` separados. Si bien la lógica geoespacial se resolvió con GeoPandas (lo cual era válido según las instrucciones), almacenar la ubicación como un tipo geométrico en la BD habría sido un plus para futuras consultas. |

**Puntuación Parcial (Calidad de Código):** `19/20`

---

### **C. Conocimientos Específicos del Rol (¿Domina las herramientas clave?)**

| Criterio | Puntuación (1-5) | Observaciones |
| :--- | :--- | :--- |
| **Uso del ORM de Django:** ¿Utiliza el ORM de forma eficiente o recurre a SQL crudo innecesariamente? | 5 | Utiliza el ORM de Django de forma correcta y eficiente para las operaciones de creación, filtrado y actualización requeridas por la prueba. No hay complejidades innecesarias. |
| **Implementación de API (Django Ninja/DRF):** ¿La API sigue las convenciones REST? ¿El manejo de peticiones y respuestas es correcto? | 5 | Implementación idiomática de Django Ninja. Usa `Router`, schemas de Pydantic para validación y serialización (`schemas.py`), y respuestas estructuradas. El resultado es una API robusta, autodocumentada y que sigue las buenas prácticas. |
| **Uso de PostGIS:** **(CRÍTICO)** ¿Implementó correctamente el modelo con `GeometryField`? ¿Utilizó funciones espaciales (ej. `ST_Contains`) para resolver el problema geoespacial? | 5 | Aunque no usó PostGIS en la base de datos, demostró un dominio equivalente con GeoPandas. La implementación en `services.py` lee el shapefile, realiza la reproyección a un sistema métrico (UTM 18S) para asegurar la precisión, y calcula la distancia mínima correctamente. |
| **Testing:** ¿Incluyó tests unitarios o de integración?. | 2 | El archivo `tests.py` está vacío. Esta es la única área de mejora significativa. La lógica en `services.py` hacía que el código fuera muy fácil de testear de forma unitaria, y fue una oportunidad perdida. |

**Puntuación Parcial (Conocimientos Específicos):** `17/20`

**Puntuación Total:** `54/60`