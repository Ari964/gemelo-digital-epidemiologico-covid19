import io
import zipfile
import json
from datetime import datetime
from typing import List, Dict, Any

class TranslationConsolidator:
    """
    Consolidador de Traducciones Académicas en Lote.
    Empaqueta los textos traducidos en un archivo ZIP con informe de trazabilidad.
    """

    @staticmethod
    def create_consolidated_zip(translations: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            index_lines = ["# ÍNDICE DE TRADUCCIONES ACADÉMICAS CONSOLIDADAS\n", f"Fecha de consolidación UTC: {datetime.utcnow().isoformat()}\n\n"]
            
            for item in translations:
                fname = item["filename"]
                base_name = fname.rsplit(".", 1)[0]
                translated_name = f"translated_{base_name}.txt"
                content = item.get("translated_text", "")
                
                # Agregar archivo traducido al ZIP
                zf.writestr(translated_name, content.encode("utf-8"))
                
                index_lines.append(f"- **{fname}** -> `{translated_name}` ({len(content)} caracteres)")

            # Agregar índice Markdown
            zf.writestr("INDICE_TRADUCCIONES.md", "\n".join(index_lines).encode("utf-8"))
            
            # Agregar metadatos JSON
            meta = {
                "generated_at": datetime.utcnow().isoformat(),
                "total_documents": len(translations),
                "documents": [{"original": t["filename"], "status": t.get("status")} for t in translations]
            }
            zf.writestr("metadata.json", json.dumps(meta, indent=2).encode("utf-8"))

        zip_bytes = buffer.getvalue()
        buffer.close()
        return zip_bytes
