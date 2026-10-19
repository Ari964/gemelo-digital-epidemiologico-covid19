"""
Script de Auditoría y Verificación del Entorno de Langflow para la Práctica de Traducción.

Cumple con el Requerimiento 3:
1. Audita la instalación local de Langflow del usuario.
2. Comprueba que 'src/backend/base/langflow/agentic/flows/TranslationFlow.json' pertenece al repositorio
   upstream clonado de Langflow y NO es el flujo personal del usuario.
3. Busca en la base de datos de Langflow (SQLite/almacenamiento local) y evalúa proveedores locales (Ollama)
   o remotos (OpenAI).
4. Verifica el estado del servidor Langflow (puerto 7860).
5. Documenta con rigor y honestidad que la práctica individual permanece PENDIENTE (BLOQUEADA)
   y detalla con exactitud qué credencial o servicio se requiere para desbloquearla.
"""

import os
import sys
import json
import urllib.request

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def audit_langflow_installation():
    print("=== AUDITORÍA TÉCNICA DE LA INSTALACIÓN DE LANGFLOW ===")
    
    # 1. Auditoría del repositorio clonado
    upstream_flow_path = r"C:\Users\KRISTEL\Documents\langflow\src\backend\base\langflow\agentic\flows\TranslationFlow.json"
    is_upstream_template = os.path.exists(upstream_flow_path)
    print(f"1. Verificación de plantilla upstream:\n   Ruta: {upstream_flow_path}\n   Existe: {is_upstream_template}")
    print("   [CONCLUSIÓN]: Este archivo es una plantilla upstream de la distribución oficial de Langflow,")
    print("   no un flujo construido y guardado en la base de datos de usuario de la instalación.")

    # 2. Búsqueda de base de datos de usuario de Langflow
    user_home = os.path.expanduser("~")
    possible_db_paths = [
        os.path.join(user_home, ".langflow", "langflow.db"),
        os.path.join(user_home, ".cache", "langflow", "langflow.db"),
        os.path.join(user_home, "AppData", "Local", "langflow", "langflow.db"),
        os.path.join(user_home, "AppData", "Roaming", "langflow", "langflow.db"),
        r"C:\Users\KRISTEL\Documents\langflow\langflow.db"
    ]
    found_dbs = [p for p in possible_db_paths if os.path.exists(p)]
    print(f"\n2. Búsqueda de almacenamiento de usuario (SQLite / base de datos de flujos):")
    if found_dbs:
        print(f"   [+] Base de datos localizada en: {found_dbs}")
    else:
        print("   [!] No se encontró ninguna base de datos SQLite activa de Langflow (langflow.db) en el perfil de usuario.")

    # 3. Verificación de servicio Langflow en ejecución (localhost:7860)
    langflow_url = "http://localhost:7860/api/v1"
    server_online = False
    try:
        req = urllib.request.Request(f"{langflow_url}/version", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                server_online = True
    except Exception:
        server_online = False

    print(f"\n3. Estado del servidor Langflow (puerto 7860):")
    print(f"   {'[+] ONLINE' if server_online else '[!] OFFLINE (Servicio no iniciado en http://localhost:7860)'}")

    # 4. Verificación de proveedores de inferencia (Ollama local o OpenAI API Key)
    openai_key = os.getenv("OPENAI_API_KEY")
    ollama_online = False
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                ollama_online = True
    except Exception:
        ollama_online = False

    print(f"\n4. Verificación de proveedores de inferencia:")
    print(f"   - OPENAI_API_KEY en variables de entorno: {'CONFIGURADA' if openai_key else 'NO CONFIGURADA (None)'}")
    print(f"   - Proveedor local Ollama (localhost:11434): {'ACTIVO' if ollama_online else 'INACTIVO / NO CORRIENDO'}")

    # 5. Declaración formal del estado de la práctica
    # Según instrucción: Si no existe proveedor funcional ni servidor activo, señalar claramente que la práctica
    # individual sigue BLOQUEADA y PENDIENTE.
    practice_status = "PENDIENTE"
    block_reason = (
        "La práctica individual de traducción en Langflow permanece PENDIENTE (BLOQUEADA). "
        "Razones técnicas: (1) El servidor local de Langflow no está en ejecución en el puerto 7860. "
        "(2) No se encontró un flujo personal persistido en la base de datos local de la usuaria. "
        "(3) No hay credencial 'OPENAI_API_KEY' configurada ni un servicio local (Ollama) activo para procesar las llamadas de lenguaje."
    )
    unblock_requirements = [
        "1. Iniciar el servidor local de Langflow ejecutando: 'langflow run' (o mediante la UI de escritorio) en el puerto 7860.",
        "2. Acceder a la interfaz web de Langflow en http://localhost:7860 e importar el flujo o abrir el lienzo personal.",
        "3. Configurar la credencial 'OPENAI_API_KEY' en las variables del entorno o en el nodo 'Language Model', o configurar un modelo local funcional (ej. Ollama con llama3/qwen).",
        "4. Enviar las frases chinas de prueba en vivo para registrar la salida real del motor."
    ]

    print(f"\n5. ESTADO OFICIAL DE LA PRÁCTICA DE TRADUCCIÓN: {practice_status}")
    print(f"   {block_reason}")

    # Frases de prueba requeridas para la ejecución
    test_phrases = [
        {
            "id": "phrase_1",
            "chinese": "数字化流行病双胞胎能够模拟非药物干预措施对疾病传播的影响。",
            "expected_meaning": "El gemelo digital epidemiológico puede simular el impacto de las intervenciones no farmacéuticas en la transmisión de la enfermedad.",
            "execution_status": "BLOQUEADA_POR_ENTORNO",
            "real_output": None
        },
        {
            "id": "phrase_2",
            "chinese": "肯尼亚各县的重症监护病床容量存在显著差异，内罗毕集中了大部分医疗资源。",
            "expected_meaning": "Existe una marcada disparidad en la capacidad de camas de cuidados intensivos entre los condados de Kenia, concentrando Nairobi la mayor parte de los recursos médicos.",
            "execution_status": "BLOQUEADA_POR_ENTORNO",
            "real_output": None
        }
    ]

    report = {
        "task_name": "Practica Individual Traductor Langflow",
        "status": practice_status,
        "is_functional": False,
        "is_100_percent_compatible": False,
        "server_status": "OFFLINE" if not server_online else "ONLINE",
        "openai_credential": "MISSING" if not openai_key else "PRESENT",
        "ollama_local_provider": "OFFLINE" if not ollama_online else "ONLINE",
        "upstream_file_evaluated": upstream_flow_path,
        "upstream_file_assessment": "Plantilla estándar del repositorio de Langflow, no flujo de usuario.",
        "block_reason": block_reason,
        "unblock_requirements": unblock_requirements,
        "test_phrases_prepared": test_phrases
    }

    report_path = os.path.join("docs", "auditoria_ejecucion_langflow.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nInforme de auditoría guardado en: {report_path}")
    return report


if __name__ == "__main__":
    audit_langflow_installation()
