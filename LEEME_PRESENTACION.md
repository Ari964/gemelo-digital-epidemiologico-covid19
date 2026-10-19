# Gemelo Digital Epidemiologico - Guia de Presentacion

Este documento permite ejecutar y presentar el proyecto en cualquier momento,
sin necesidad de volver a entrenar ni recalcular resultados.

---

## 1. Requisitos previos (ya instalados en esta laptop)

- Python 3.11.9 (entorno virtual en `.venv`)
- Node.js y npm (para el frontend React)
- Dataset público real: `data/raw/owid_covid_kenya_raw.csv` (SHA-256 verificado)
- Resultados del protocolo v2.0 ya generados y guardados en disco.

---

## 2. Archivo para iniciar la presentacion

**Ejecutar:** `INICIAR_PRESENTACION.bat`

Esto hace lo siguiente:
1. Verifica que existan los archivos necesarios.
2. Inicia el backend FastAPI en `http://127.0.0.1:8002`.
3. Inicia el frontend React en `http://127.0.0.1:5173`.
4. Espera a que ambos servicios respondan.
5. Abre automaticamente el navegador en la aplicación.

No es necesario instalar nada adicional. El entorno virtual `.venv` y
`node_modules` ya están incluidos en el proyecto.

---

## 3. Acceso al sistema

### URL de la aplicacion
```
http://127.0.0.1:5173
```

### Documentacion de la API (backend)
```
http://127.0.0.1:8002/docs
```

### Credenciales de acceso
El sistema requiere autenticacion JWT. Utilice una cuenta existente en la
base de datos. Las credenciales no se almacenan en archivos versionados.

Si no recuerda las credenciales, puede crear un usuario desde el modulo
de seguridad o usar cualquier cuenta previamente registrada en la base de
datos SQLite (`epidemic_twin.db`).

> No desactive la autenticacion. El token de sesion caduca al cerrar
> sesion; para una nueva presentacion simplemente inicie sesion de nuevo.

---

## 4. Navegacion sugerida para la presentacion

El proyecto sigue la metodologia CRISP-DM. Sugerido el siguiente orden:

| Modulo | Que demostrar |
|--------|---------------|
| Ruta Evidencia | Trazabilidad completa desde datos publicos OWID hasta el modelo final. |
| Fase 5: Validacion | Cinco folds temporales, busca de hiperparametros, seleccion del campeón. |
| Articulo Cientifico | Tablas y figuras con interpretabilidad y explicabilidad. |

### Modulo "Articulo Cientifico" (pantalla principal para el docente)

Este modulo contiene todos los elementos del artículo científico con sus apartados de **Interpretabilidad** y **Explicabilidad**:

- **Particion temporal 80/20**: Division cronologica (181 semanas desarrollo, 45 semanas prueba). Sin mezcla aleatoria.
- **Mapa de calor**: Correlaciones Pearson de variables epidemiologicas, calculado solo en el bloque de desarrollo.
- **Observados vs Predicciones**: Serie temporal punto a punto (campeon vs persistencia vs Ridge vs Random Forest).
- **Residuos y distribucion de errores**: Analisis de residuos del campeon.
- **U de Theil (variante U1)**: Coeficiente comparando el pronóstico del campeón contra el baseline de persistencia, sobre las mismas fechas.
- **Pruebas estadisticas**: Wilcoxon pareado, Diebold-Mariano con correccion HLN, Shapiro-Wilk.
- **Cuadro de comparacion de modelos**: Metricas de validacion y prueba por cada modelo.

Cada tabla y figura tiene:
- **Interpretabilidad**: que representa, variables/unidades/periodo, como leerlo, hallazgo concreto, alcance y limites.
- **Explicabilidad**: datos y transformaciones, metodo, parametros, procedimiento, limitaciones.

### Descargas disponibles
Desde cada tarjeta de figura/tabla se pueden descargar:
- **PNG a 500 dpi** (fondo blanco, texto oscuro, estilo científico).
- **CSV de datos** subyacentes.
- **Paquete ZIP conjunto** (JSON de resultados + todas las figuras + CSV de exportación) desde la tarjeta "Descarga conjunta del artículo".

---

## 4. Detener el sistema

**Ejecutar:** `DETENER_PRESENTACION.bat`

Este script detiene únicamente los procesos del backend y del frontend que fueron iniciados por el lanzador. No cierra otros procesos del sistema.

---

## 5. Solución de problemas comunes

| Problema | Solución |
|----------|----------|
| El puerto 5173 o 8002 esta ocupado | Otro programa lo está usando. Cambie los puertos en `vite.config.ts` y `backend/main.py`, o cierre el otro programa primero. |
| El backend no responde | Verifique que .venv\Scripts\python.exe existe y que el archivo `backend/main.py` está presente. |
| El frontend no carga | Verifique que `node_modules` existe. Ejecute `npm install` si es necesario. |
| Ollama no disponible | La selección asistida por IA usa un fallback manual explícito. Las funcionalidades del artículo funcionan sin Ollama. |
| No puedo iniciar sesión | Use credenciales de usuario existentes en la base de datos SQLite. No hay credenciales predeterminadas expuestas. |
| Puerto ocupado por otro programa | Cambie los puertos en `vite.config.ts` (frontend) y `backend/main.py` (backend). |

---

## 6. Funciones que requieren conexión a internet

- **Ollama (IA local)**: Solo si está instalado localmente en `http://localhost:11434`. Si no está disponible, la selección asistida por IA usa criterios manuales explícitos (no se presenta como IA).
- **Descarga de dataset público**: El dataset ya está descargado en `data/raw/`. No se necesita internet para ejecutar el sistema.
- **Otras funciones**: No requieren internet.

---

## 7. Archivos importantes en el proyecto

| Ruta | Contenido |
|------|-----------|
| `data/raw/owid_covid_kenya_raw.csv` | Dataset público real (OWID/OMS, Kenia). SHA-256 verificado. |
| `models/protocolo_v2/protocolo_v2_resultados.json` | Resultados completos del protocolo v2.0. |
| `docs/figures/protocolo_v2/` | Figuras PNG (500 dpi) y SVG del artículo. |
| `docs/export/protocolo_v2/` | CSV de datos de tablas y figuras. |
| `backend/main.py` | Punto de entrada del backend FastAPI. |
| `vite.config.ts` | Configuración del frontend (puerto 5173). |

---

## 7. Estado de reproducibilidad

- Los cálculos científicos están en el script `scripts/protocolo_temporal_v2.py`.
- No se requiere re-entrenar ni recalcular resultados; todos los artefactos están en disco.
- Las figuras están en fondo blanco, exportadas a 500 dpi (dimensiones de píxeles reales, no solo etiqueta DPI).
- Las exportaciones CSV contienen los datos exactos de cada figura y tabla.

---

**Última actualización:** 18/10/2026
**Proyecto:** Gemelo Digital Epidemiologico - Kenia (47 condados)
**Metodología:** CRISP-DM