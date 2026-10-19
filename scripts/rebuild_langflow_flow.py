import json
import os
import copy

FLOW_PATH = "docs/flujo_epidemiologico_langflow_exportado.json"

TOOL_CODE = '''import json
import urllib.request
from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.message import Message

class FastApiKenyaDataTool(Component):
    display_name = "Herramienta Consulta FastAPI Kenia"
    description = "Consulta la API REST local de FastAPI (puerto 8000) para obtener métricas reales de validación cruzada y pronóstico semanal."
    icon = "Database"

    inputs = [
        MessageTextInput(
            name="endpoint",
            display_name="Endpoint",
            value="/api/v1/validation/weekly-evaluation",
            info="Ruta del endpoint de FastAPI",
        ),
    ]

    outputs = [
        Output(display_name="Resultado API", name="result", method="query_backend"),
    ]

    def query_backend(self) -> Message:
        url = f"http://host.docker.internal:8000{self.endpoint}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Langflow-Agent"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return Message(text=json.dumps(data, indent=2))
        except Exception as e:
            return Message(text=f"Error consultando backend: {str(e)}")
'''

def rebuild_flow():
    with open(FLOW_PATH, "r", encoding="utf-8") as f:
        flow = json.load(f)

    nodes = flow["data"]["nodes"]
    edges = flow["data"]["edges"]

    # Filter out legacy/vocabulary/story nodes
    legacy_ids = {
        "CustomComponent-JXD11",
        "CustomComponent-csTUt",
        "CustomComponent-gzqgx",
        "Prompt Template-1JPny",
        "Agent-xC16O",
        "note-5r6R8"
    }

    clean_nodes = [n for n in nodes if n["id"] not in legacy_ids]

    # Find Agent node and update model to Ollama
    for n in clean_nodes:
        if n["id"] == "Agent-EXpSZ":
            tpl = n["data"]["node"]["template"]
            # Configure Ollama provider
            tpl["model"]["value"] = [{
                "name": "llama3.2:3b",
                "icon": "Ollama",
                "provider": "Ollama",
                "metadata": {
                    "icon": "Ollama",
                    "tool_calling": True,
                    "reasoning": False,
                    "search": False,
                    "preview": False,
                    "not_supported": False,
                    "deprecated": False,
                    "default": True,
                    "model_type": "llm",
                    "created": 1784592000,
                    "vision": False,
                    "context_window": 131072,
                    "cost_per_million_in": 0.0,
                    "cost_per_million_out": 0.0
                }
            }]
            if "api_key" in tpl:
                tpl["api_key"]["value"] = ""

    # Create the clean FastAPI Tool Custom Component Node
    tool_node = {
        "data": {
            "id": "CustomComponent-FastApiTool",
            "node": {
                "base_classes": ["Component", "Tool"],
                "beta": False,
                "category": "custom_components",
                "conditional_paths": [],
                "custom_fields": {},
                "description": "Consulta la API REST local de FastAPI (puerto 8000) para obtener métricas reales de validación cruzada y pronóstico semanal.",
                "display_name": "Herramienta Consulta FastAPI Kenia",
                "documentation": "",
                "edited": True,
                "field_order": ["endpoint"],
                "frozen": False,
                "icon": "Database",
                "key": "FastApiKenyaDataTool",
                "legacy": False,
                "metadata": {
                    "code_hash": "fastapi_kenya_tool_2026",
                    "dependencies": {"dependencies": [{"name": "lfx", "version": None}], "total_dependencies": 1},
                    "module": "custom_components.FastApiKenyaDataTool"
                },
                "minimized": False,
                "output_types": ["Tool", "Message"],
                "outputs": [
                    {
                        "allows_loop": False,
                        "cache": True,
                        "display_name": "Resultado API",
                        "group_outputs": False,
                        "method": "query_backend",
                        "name": "result",
                        "selected": "Message",
                        "tool_mode": True,
                        "types": ["Message"],
                        "value": "__UNDEFINED__"
                    },
                    {
                        "allows_loop": False,
                        "cache": True,
                        "display_name": "Component as Tool",
                        "group_outputs": False,
                        "method": "build_tool",
                        "name": "component_as_tool",
                        "selected": "Tool",
                        "tool_mode": True,
                        "types": ["Tool"],
                        "value": "__UNDEFINED__"
                    }
                ],
                "pinned": False,
                "template": {
                    "_type": "Component",
                    "code": {
                        "advanced": True,
                        "api_editable": False,
                        "dynamic": True,
                        "fileTypes": [],
                        "file_path": "",
                        "info": "",
                        "list": False,
                        "load_from_db": False,
                        "multiline": True,
                        "name": "code",
                        "password": False,
                        "placeholder": "",
                        "required": True,
                        "show": True,
                        "title_case": False,
                        "type": "code",
                        "value": TOOL_CODE
                    },
                    "endpoint": {
                        "_input_type": "MessageTextInput",
                        "advanced": False,
                        "display_name": "Endpoint",
                        "dynamic": False,
                        "info": "Ruta del endpoint de FastAPI",
                        "input_types": ["Message"],
                        "list": False,
                        "list_add_label": "Add More",
                        "load_from_db": False,
                        "name": "endpoint",
                        "placeholder": "/api/v1/validation/weekly-evaluation",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "tool_mode": False,
                        "trace_as_input": True,
                        "trace_as_metadata": True,
                        "type": "str",
                        "value": "/api/v1/validation/weekly-evaluation"
                    }
                },
                "tool_mode": True,
                "lf_version": "1.12.2"
            },
            "selected_output": "component_as_tool",
            "showNode": True,
            "type": "CustomComponent"
        },
        "dragging": False,
        "id": "CustomComponent-FastApiTool",
        "position": {
            "x": 1238.0,
            "y": 450.0
        },
        "selected": False,
        "type": "genericNode",
        "measured": {"width": 320, "height": 220}
    }

    clean_nodes.append(tool_node)

    # Rebuild clean edges
    clean_edges = [
        # ChatInput -> Agent
        {
            "animated": False,
            "className": "",
            "data": {
                "sourceHandle": {"dataType": "ChatInput", "id": "ChatInput-tKQ4d", "name": "message", "output_types": ["Message"]},
                "targetHandle": {"fieldName": "input_value", "id": "Agent-EXpSZ", "inputTypes": ["Message"], "type": "str"}
            },
            "id": "edge_chatinput_agent",
            "selected": False,
            "source": "ChatInput-tKQ4d",
            "sourceHandle": '{"dataType":"ChatInput","id":"ChatInput-tKQ4d","name":"message","output_types":["Message"]}',
            "target": "Agent-EXpSZ",
            "targetHandle": '{"fieldName":"input_value","id":"Agent-EXpSZ","inputTypes":["Message"],"type":"str"}'
        },
        # Tool -> Agent
        {
            "animated": False,
            "className": "",
            "data": {
                "sourceHandle": {"dataType": "FastApiKenyaDataTool", "id": "CustomComponent-FastApiTool", "name": "component_as_tool", "output_types": ["Tool"]},
                "targetHandle": {"fieldName": "tools", "id": "Agent-EXpSZ", "inputTypes": ["Tool"], "type": "other"}
            },
            "id": "edge_fastapitool_agent",
            "selected": False,
            "source": "CustomComponent-FastApiTool",
            "sourceHandle": '{"dataType":"FastApiKenyaDataTool","id":"CustomComponent-FastApiTool","name":"component_as_tool","output_types":["Tool"]}',
            "target": "Agent-EXpSZ",
            "targetHandle": '{"fieldName":"tools","id":"Agent-EXpSZ","inputTypes":["Tool"],"type":"other"}'
        },
        # Agent -> ChatOutput
        {
            "animated": False,
            "className": "",
            "data": {
                "sourceHandle": {"dataType": "Agent", "id": "Agent-EXpSZ", "name": "response", "output_types": ["Message"]},
                "targetHandle": {"fieldName": "input_value", "id": "ChatOutput-KxTA8", "inputTypes": ["Data", "JSON", "DataFrame", "Table", "Message"], "type": "other"}
            },
            "id": "edge_agent_chatoutput",
            "selected": False,
            "source": "Agent-EXpSZ",
            "sourceHandle": '{"dataType":"Agent","id":"Agent-EXpSZ","name":"response","output_types":["Message"]}',
            "target": "ChatOutput-KxTA8",
            "targetHandle": '{"fieldName":"input_value","id":"ChatOutput-KxTA8","inputTypes":["Data","JSON","DataFrame","Table","Message"],"type":"other"}'
        }
    ]

    flow["data"]["nodes"] = clean_nodes
    flow["data"]["edges"] = clean_edges

    with open(FLOW_PATH, "w", encoding="utf-8") as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)

    print("Rebuilt flujo_epidemiologico_langflow_exportado.json successfully.")
    print(f"Nodes: {[n['id'] for n in clean_nodes]}")
    print(f"Edges: {len(clean_edges)}")

if __name__ == "__main__":
    rebuild_flow()
