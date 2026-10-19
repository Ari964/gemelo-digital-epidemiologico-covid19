"""
FastAPI Backend - Gemelo Digital Epidemiológico a Nivel Poblacional (Kenia 47 Condados)
--------------------------------------------------------------------------------------
Backend único de producción que provee:
1. Gestión de Usuarios y Seguridad (RBAC estricto: Admin, Epidemiólogo, Analista).
2. Bitácora de Auditoría criptográfica (identidad derivada estrictamente de JWT).
3. Motor Epidemiológico Híbrido en Python (SEIR Espacial Metapoblacional + ABM Hogares).
4. Exportación institucional de informes (ReportLab PDF y OpenPyXL Excel).
5. Asistente Copiloto Epidemiológico con Google Gemini (sin respuestas heurísticas simuladas).
6. Validación Científica y Aprobación Técnica de Modelos (CRISP-DM Fase 5).
7. Monitoreo On-Demand y Despliegue de Modelos (CRISP-DM Fase 6).
8. Explicabilidad Global Asíncrona con Sobol (CRISP-DM Fase 4).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.db.session import engine, Base
from backend.app.api.v1.api import api_router
from backend.app.scripts.seed_verified_data import seed_data
from backend.app.analytics.sobol_sensitivity import SobolSensitivityAnalyzer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de tablas y seed verificado
    print("[FastAPI] Inicializando esquema de base de datos y datos verificados...")
    Base.metadata.create_all(bind=engine)
    try:
        seed_data()
    except Exception as e:
        print(f"[FastAPI] Advertencia en inicialización de semillas: {e}")

    # Recuperación de trabajos de Sobol interrumpidos en reinicio
    SobolSensitivityAnalyzer.recover_on_startup()

    yield
    print("[FastAPI] Finalizando aplicación...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits access from Vite frontend and Streamlit workspaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar todos los routers bajo el prefijo único /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": "Population-Level Digital Twin for Pandemic Preparedness",
        "jurisdiction": "Kenya (47 Counties)",
        "methodology": "CRISP-DM (Phases 1-6)",
        "api_docs": f"{settings.API_V1_STR}/docs",
        "status": "online",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fastapi_backend"}
