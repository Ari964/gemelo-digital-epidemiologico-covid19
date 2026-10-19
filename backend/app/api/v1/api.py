from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    users,
    audit,
    counties,
    simulations,
    reports,
    chat,
    validation,
    data,
    monitoring,
    sobol,
    predictions,
    data_assistant,
    langchain_agent,
    langflow
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación y Seguridad"])
api_router.include_router(users.router, prefix="/users", tags=["Gestión de Usuarios (RBAC)"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Bitácora de Auditoría"])
api_router.include_router(counties.router, prefix="/counties", tags=["Datos Espaciales 47 Condados"])
api_router.include_router(data.router, prefix="/data", tags=["Integración de Datos CRISP-DM"])
api_router.include_router(simulations.router, prefix="/simulations", tags=["Simulaciones Epidemiológicas"])
api_router.include_router(reports.router, prefix="/reports", tags=["Exportación de Informes (PDF/Excel)"])
api_router.include_router(chat.router, prefix="/ai/chat", tags=["Copiloto Epidemiológico IA"])
api_router.include_router(validation.router, prefix="/validation", tags=["Validación y Aprobación Técnica"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoreo y Despliegue de Modelos (Fase 6)"])
api_router.include_router(sobol.router, prefix="/analytics", tags=["Explicabilidad y Sensibilidad Global de Sobol (Fase 4)"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predicciones Semanales de Vigilancia y Sensibilidad"])
api_router.include_router(data_assistant.router, prefix="/data-assistant", tags=["Asistente de Datos del Gemelo Digital"])
api_router.include_router(langchain_agent.router, prefix="/langchain-agent", tags=["Agente Integrador LangChain"])
api_router.include_router(langflow.router, prefix="/langflow", tags=["Práctica y Flujo de Vigilancia Langflow"])
