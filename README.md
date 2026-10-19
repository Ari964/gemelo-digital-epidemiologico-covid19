# Gemelo Digital Epidemiológico de Nivel Poblacional (Kenia - 47 Condados)

Sistema integral de simulación computacional, evaluación cuantitativa, gobernanza de modelos y vigilancia epidemiológica para la preparación y respuesta ante pandemias en Kenia, estructurado bajo el estándar metodológico **CRISP-DM (Cross-Industry Standard Process for Data Mining)**.

---

## 1. Arquitectura y Componentes del Sistema

El sistema implementa una arquitectura desacoplada basada en microservicios y aplicaciones satélite:

- **Backend (FastAPI + SQLAlchemy + Pydantic v2)**: API REST canónica con autenticación JWT, RBAC de 4 roles (`admin`, `epidemiologist`, `data_scientist`, `viewer`), registro de auditoría SHA-256 en base de datos y motores analíticos de simulación.
- **Base de Datos Territorial**: PostgreSQL 16 con extensión espacial PostGIS (con fallback automático y seguro a SQLite para pruebas y desarrollo local).
- **Frontend Principal (React 19 + TypeScript + Vite)**: Panel de control interactivo con visualización geoespacial de 47 condados, simulación en tiempo real y exportación de dossiers.
- **Data Science Workspace (`apps/data_science_workspace`)**: Aplicación multipágina en Streamlit estructurada según las 6 fases de CRISP-DM, integrada contra la API canónica mediante tokens JWT persistidos en sesión.
- **Academic Translator Satellite (`apps/academic_translator`)**: Satélite de procesamiento y consolidación documental para publicaciones científicas.

---

## 2. Requisitos Previos

- **Python**: 3.11+
- **Node.js**: 20+ y `npm`
- **Docker y Docker Compose**: (Opcional, para ejecución contenerizada completa)

---

## 3. Comandos de Arranque y Despliegue

### Opción A: Despliegue Contenerizado con Docker Compose (Recomendado)

Inicia todos los servicios (PostgreSQL/PostGIS, Backend FastAPI, Frontend React, Workspaces Streamlit):

```bash
# Iniciar todos los contenedores en segundo plano
docker compose up -d

# Verificar el estado de los servicios
docker compose ps

# Detener los servicios
docker compose down
```

**Accesos del sistema:**
- Frontend React: `http://localhost:3000`
- API Backend (Swagger Docs): `http://localhost:8000/docs`
- Data Science Workspace: `http://localhost:8501`
- Academic Translator: `http://localhost:8502`

---

### Opción B: Arranque Modular en Entorno Local

#### 1. Configuración del Backend y Base de Datos

```bash
# Crear entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\activate      # En Windows
# source .venv/bin/activate    # En Linux/macOS

pip install -r backend/requirements.txt

# Poblar la base de datos con los datos territoriales oficiales (Censo KNBS 2019, 47 Condados, Barasa 2020)
# (Una base recién creada muestra 0 observaciones en dataset_observations hasta ejecutar la ingesta)
python -m backend.app.scripts.seed_verified_data

# Ingesta formal reproducible de las 1.606 observaciones empíricas (OWID/OMS Kenia 2020-2024)
python scripts/seed_observations_to_db.py

# Iniciar el servidor FastAPI
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **Nota para Docker:** Tras ejecutar `docker compose up -d`, ejecute la inicialización e ingesta dentro del contenedor backend:
> ```bash
> docker compose exec backend python -m backend.app.scripts.seed_verified_data
> docker compose exec backend python scripts/seed_observations_to_db.py
> ```

#### 2. Configuración y Arranque del Frontend (React + Vite)

```bash
# Instalar dependencias de Node.js
npm install

# Iniciar servidor de desarrollo Vite
npm run dev
```

#### 3. Arranque del Data Science Workspace (Streamlit)

```bash
# Iniciar workspace de ciencia de datos CRISP-DM
streamlit run apps/data_science_workspace/app.py --server.port 8501
```

---

## 4. Credenciales de Acceso al Sistema

El script de inicialización (`seed_verified_data.py`) genera exactamente los siguientes tres usuarios oficiales con contraseñas seguras hasheadas (bcrypt):

| Rol | Nombre | Correo Electrónico | Contraseña | Permisos Principales |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Ing. Administrador Sistema | `admin@epidemic-twin.ke` | `AdminSecure2026!` | Acceso total, aprobación técnica, activación operativa, auditoría |
| **Epidemiologist** | Dra. Wanjiku (Epidemióloga Jefe) | `dr.wanjiku@health.go.ke` | `EpiChief2026!` | Ingesta de observaciones, simulación, calibración, evaluación |
| **Analyst** | Analista Omondi (MOH Kenya) | `omondi@moh.go.ke` | `AnalystMOH2026!` | Análisis de vigilancia, consultas analíticas, ETL |

---

## 5. Implementación del Plan Integral de Corrección y Resolución de Defectos Externos

El sistema resuelve rigurosamente los defectos identificados en la revisión externa y los ocho puntos normativos:

1. **Alineación Temporal, Territorial y Eliminación de Relleno con Ceros (Punto 1)**:
   - Se eliminó totalmente el relleno con ceros (`aligned_base.append(0.0)`) en `validation.py`.
   - Cada simulación construye su calendario desde su propia `simulation_start_date`.
   - La evaluación por condado frente a candidatas sin series territoriales es rechazada con HTTP 400.
   - Limpieza conjunta trilateral (`yt`, `yc`, `yb`) asegurando mismos puntos compartidos.
   - Si la muestra compartida es insuficiente (< 5 días), reporta `PENDING_BASELINE` (nunca `SUPPORTED`).

2. **Cumplimiento Estricto del Umbral de Cobertura (>= 80%) y Trazabilidad (Punto 2)**:
   - Hard gate en `model_registry.py`: cobertura < 80.0%, nula o no finita es rechazada sin excepción.
   - Métricas no finitas o nulas (NaN, Inf) son estrictamente rechazadas.
   - Período de calibración recuperado de la entidad; omisión de fechas es detectada y auditada.

3. **Conservación y Aplicación de Parámetros Aprobados e Integridad Criptográfica (Punto 3)**:
   - Copia verificable de `effective_parameters_json` persistida y reflejada en el artefacto del modelo.
   - `self.base_intra_sar` se pasa directamente al motor ABM de hogares (reemplaza el 0.35 hardcoded).
   - Serialización canónica determinista (`sort_keys=True, separators=(',', ':')`) para SHA-256.
   - Doble verificación de integridad: comprobación interna y validación cruzada contra el hash oficial aprobado en `model_registry`. Se rechazan artefactos manipulados externamente aunque tengan checksum interno recalculado.

4. **Selección Rigurosa de Datos y Estados Honestos de Monitoreo (Punto 4)**:
   - `DATA_DRIFT`: Valida existencia de datasets en BD; no particiona series arbitrariamente; exige muestra mínima (>= 15) y compatibilidad de variable/unidad/territorio.
   - `OUTPUT_STABILITY`: Compara simulaciones con idéntica versión, escenario y horizonte; si difieren, emite `PENDING`.
   - `PREDICTIVE_DEGRADATION`: Alinea por fecha de calendario exacta y mide degradación contra el desempeño de referencia.
   - Auditoría con el usuario autenticado real (`evaluated_by=current_user.email`). Métricas nulas protegidas sin `TypeError`.

5. **Flujo Real de Streamlit y Contratos FastAPI (Punto 5)**:
   - Login alineado con contrato JSON `{"email": ..., "password": ...}`.
   - Obtención de rol e identidad reales desde la respuesta autenticada.
   - Desempaque correcto de tupla `val, audit = compute_mape(...)` previniendo errores en tiempo de ejecución.
   - Laboratorio interactivo marcado con `is_demo_mode = True`, inhabilitando cualquier acreditación de H1 formal.

6. **Migraciones Alembic Reales y Columnas Espaciales (Punto 6)**:
   - Cadena de migraciones continua `001 -> 002 -> 003 -> 004_spatial_geom_columns`.
   - Columna `geom` añadida a `counties` y `subcounties`, permitiendo consultas ORM completas en SQLite y PostgreSQL/PostGIS.

7. **Procedencia Dependiente del Contenido Real de los Datos (Punto 7)**:
   - `MobilityEngine` valida archivo, no vacío, dimensiones 47x47, floats válidos y no negativos. Si no es utilizable, revierte a `ESTIMATED` con justificación explícita.
   - Demografía verificada contra KNBS 2019; camas UCI no verificadas se mantienen en `None` (`UNKNOWN`).

8. **Aislamiento Estricto de Pruebas y Empaquetado Limpio (Punto 8)**:
   - Fixture de sesión `test_env_setup` en `conftest.py` ejecutando migraciones en base SQLite temporal y aislando `MODELS_DIR`.
   - Script de extracción limpia con verificación de directorio de trabajo aislado.

---

## 6. Verificación de Pruebas Automatizadas

```bash
# 1. Ejecutar suite completa de pruebas Python en entorno aislado (67 aprobadas, 1 omitida por PostGIS)
python -m pytest tests/ -v

# 2. Ejecutar pruebas unitarias de regresión de los 8 defectos externos (17 aprobadas)
python -m pytest tests/test_regression_external_review.py -v

# 3. Ejecutar pruebas del frontend con Vitest (6 aprobadas)
npm test

# 4. Compilar bundle de producción del frontend
npm run build

# 5. Generar paquete limpio de entrega
powershell -ExecutionPolicy Bypass -File scripts/package_submission.ps1

# 6. Probar extracción y ejecución limpia del paquete generado en carpeta temporal
powershell -ExecutionPolicy Bypass -File scripts/test_clean_package_extraction.ps1
```

---

## 7. Protocolo de Evaluación Temporal v2.0 (GD_TI Fase 13)

Nuevo protocolo científico ejecutable sobre datos reales OWID/OMS (Kenia), diferenciado y versionado respecto a los resultados anteriores (`models/model_evaluation_weekly_results.json`). No sobrescribe ni mezcla resultados previos.

### 7.1 Ejecución del protocolo v2.0

```bash
# Partición temporal 80/20, 5 folds temporales, búsqueda de hiperparámetros,
# selección del campeón (ex-ante, sin usar el 20% de prueba), U de Theil,
# mapa de calor de correlaciones, pruebas estadísticas y exportación a 500 dpi.
.venv\Scripts\python.exe scripts/protocolo_temporal_v2.py
```

Artefactos generados:
- `models/protocolo_v2/protocolo_v2_resultados.json` — resultados completos (métricas por fold, campeón, U de Theil, pruebas, interpretabilidad y explicabilidad de cada tabla/figura).
- `docs/figures/protocolo_v2/*.png` — figuras a 500 dpi reales, fondo blanco (partición, observados vs predicciones, residuos, mapa de calor).
- `docs/figures/protocolo_v2/*.svg` — versión vectorial del mapa de calor.
- `docs/export/protocolo_v2/*.csv` — datos de tablas y figuras (observado vs predicho, residuos, correlaciones, auditoría temporal).

### 7.2 Endpoints del artículo científico (FastAPI :8000)

Todos requieren autenticación JWT. Verificados con TestClient (usuario simulado, rol admin):

| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/api/v1/reports/articulo/resultados` | GET | JSON completo del protocolo v2.0 |
| `/api/v1/reports/articulo/figura/{archivo}` | GET | Sirve una figura PNG/SVG (500 dpi) |
| `/api/v1/reports/articulo/descarga/{archivo}` | GET | Descarga CSV/JSON de datos |
| `/api/v1/reports/articulo/seleccion-ia` | POST | Selección asistida por IA (Ollama) o manual |
| `/api/v1/reports/articulo/paquete` | GET | Paquete ZIP con JSON + figuras + CSV |

### 7.3 Módulo del artículo científico en la interfaz React

Accesible desde la barra lateral (módulo **Artículo Científico**, etiqueta "Artículo"), dentro del grupo de Reporting. Permite:
- Consultar cada tabla y figura con sus apartados **A. Interpretabilidad** y **B. Explicabilidad**.
- Descargar cada figura en PNG (500 dpi) y los CSV de datos.
- Ejecutar la selección asistida por IA (Ollama local, `qwen2.5:0.5b`) con fallback a selección manual explícita si Ollama no está disponible.
- Descargar un paquete ZIP conjunto del artículo.

---

## 8. Estado de Reproducibilidad y Trazabilidad

- Dataset público real y trazable: `data/raw/owid_covid_kenya_raw.csv` (OWID/OMS, Kenia, CC BY 4.0, SHA-256 `c82f3cfc...`, 1,674 filas, 2020-01-05 a 2024-08-04). Verificación: `python scripts/check_owid_source.py`.
- Hash del dataset registrado en cada ejecución del protocolo v2.0.
- No se usan datos sintéticos ni valores fijos como sustituto de cálculos reales (salvo la matriz de movilidad estimada por gravedad, debidamente etiquetada como `ESTIMATED` y separada de la vigilancia epidemiológica observada).
- Las simulaciones SEIR/ABM se identifican explícitamente como simulaciones matemáticas contrafactuales, diferenciadas de observaciones y pronósticos.
