# QA Engineer Assessment - Inventory Management API

## Descripcion

Este proyecto contiene una API de gestion de inventario desarrollada con FastAPI. Tu objetivo es realizar un analisis completo de calidad, identificar bugs, escribir pruebas automatizadas y documentar los problemas encontrados.

## Tiempo Estimado

**3 horas maximo**

## Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- Git
- Cuenta de GitHub

## Levantar el Proyecto

```bash
docker-compose up --build
```

La API estara disponible en `http://localhost:8000`

Documentacion Swagger: `http://localhost:8000/docs`

## Endpoints Disponibles

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /auth/login | Obtener token de acceso |
| GET | /products | Listar productos |
| GET | /products/{id} | Obtener producto por ID |
| POST | /products | Crear producto |
| PUT | /products/{id} | Actualizar producto |
| DELETE | /products/{id} | Eliminar producto |
| POST | /inventory/adjust | Ajustar inventario |
| GET | /inventory/low-stock | Productos con bajo stock |
| GET | /health | Health check |

## Credenciales de Prueba

```
Usuario: admin
Password: admin123

Usuario: user
Password: user123
```

## Tu Mision

### 1. Analisis y Deteccion de Bugs (30%)

- Analiza el codigo fuente y la API en busca de bugs
- Documenta cada bug encontrado como un **Issue en GitHub**
- Cada issue debe incluir:
  - Titulo descriptivo
  - Pasos para reproducir
  - Comportamiento esperado vs actual
  - Severidad (Critical, High, Medium, Low)
  - Evidencia (logs, screenshots, respuestas de API)

### 2. Pruebas Automatizadas (40%)

Crea una suite de pruebas que incluya:

#### Pruebas Unitarias
- Archivo: `tests/test_unit.py`
- Pruebas para funciones individuales
- Usar `pytest`

#### Pruebas de Integracion/API
- Archivo: `tests/test_api.py`
- Pruebas end-to-end de los endpoints
- Usar `pytest` con `httpx` o `TestClient`

#### Pruebas de UI (Opcional - Puntos Extra)
- Archivo: `tests/test_ui.py`
- Pruebas con Selenium para la documentacion Swagger
- Verificar que los endpoints respondan correctamente

### 3. Code Coverage (20%)

- Lograr **100% de code coverage** en los archivos de la carpeta `app/`
- Generar reporte HTML de coverage
- Comando: `pytest --cov=app --cov-report=html tests/`

### 4. Documentacion (10%)

Crea un archivo `TESTING_REPORT.md` que incluya:

- Resumen ejecutivo de hallazgos
- Lista de bugs encontrados con referencias a los Issues
- Metricas de coverage alcanzadas
- Recomendaciones de mejora
- Instrucciones para ejecutar las pruebas

## Estructura de Entrega

```
/tests
  /test_unit.py
  /test_api.py
  /test_ui.py (opcional)
  /conftest.py
/TESTING_REPORT.md
/requirements-test.txt
```

## Herramientas Sugeridas

- pytest
- pytest-cov
- httpx
- selenium (opcional)
- pytest-html

## Criterios de Evaluacion

| Criterio | Puntos |
|----------|--------|
| Bugs identificados correctamente | 30 |
| Calidad de pruebas automatizadas | 40 |
| Coverage al 100% | 20 |
| Documentacion y reporte | 10 |
| **Total** | **100** |

## Notas Importantes

- Fork este repositorio antes de comenzar
- Haz commits frecuentes con mensajes descriptivos
- No modifiques el codigo fuente de la API (carpeta `app/`)
- Solo debes agregar pruebas y documentacion
- Los Issues deben crearse en tu fork

## Preguntas

Si tienes dudas durante el assessment, documentalas en tu reporte final.

---

Buena suerte!
