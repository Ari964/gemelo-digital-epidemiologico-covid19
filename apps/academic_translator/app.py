import streamlit as st
import io
import os
import pypdf

from apps.academic_translator.security.file_validator import FileValidator, FileSecurityException
from apps.academic_translator.agents.translator_pipeline import AcademicTranslatorPipeline
from apps.academic_translator.utils.consolidator import TranslationConsolidator

st.set_page_config(
    page_title="Satélite de Traducción Académica | Gemelo Digital",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Satélite de Traducción Académica Especializada")
st.caption("Traducción Multilingüe de Papers Epidemiológicos con Preservación Terminológica y Procesamiento en Lote (≥10 Documentos)")

# Configuración de Ollama Local
ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")
pipeline = AcademicTranslatorPipeline(base_url=ollama_url, model=ollama_model)
is_ollama_healthy = pipeline.check_health()

with st.sidebar:
    st.header("⚙️ Configuración")
    target_lang = st.selectbox("Idioma Destino:", ["Español (es)", "English (en)", "Français (fr)"], index=0)
    lang_code = "es" if "Español" in target_lang else ("en" if "English" in target_lang else "fr")
    
    st.markdown("---")
    st.markdown("### 🤖 Motor de IA Local:")
    if is_ollama_healthy:
        st.success(f"🟢 **Ollama Conectado** ({ollama_model})")
    else:
        st.error(f"🔴 **Ollama Desconectado** ({ollama_url})")
    
    st.markdown("---")
    st.markdown("### 🛡️ Políticas de Seguridad:")
    st.write("- **Límite por Archivo**: 15 MB")
    st.write("- **Límite del Lote**: 100 MB")
    st.write("- **Formatos Permitidos**: PDF (`%PDF-`), TXT (UTF-8)")
    st.write("- **Protección**: Path Traversal y Zip Bombs")
    
    st.markdown("---")
    st.markdown(f"**Términos en Glosario Protegidos**: {len(pipeline.glossary)}")

st.markdown("""
### Carga de Manuscritos y Artículos Científicos
Sube documentos académicos individuales o en lotes masivos ($\ge 10$ archivos). El sistema validará la seguridad de cada archivo y ejecutará el pipeline multi-agente con Ollama.
""")

uploaded_files = st.file_uploader(
    "Selecciona archivos PDF o TXT:",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    total_bytes = sum(len(f.getvalue()) for f in uploaded_files)
    st.info(f"📁 **{len(uploaded_files)} archivos cargados** | Tamaño total del lote: {total_bytes / (1024*1024):.2f} MB")

    # Validación de seguridad de lote
    try:
        FileValidator.validate_batch_size(total_bytes, len(uploaded_files))
        st.success("✅ Validación de seguridad de lote superada satisfactoriamente.")
    except FileSecurityException as e:
        st.error(f"❌ Fallo de seguridad: {str(e)}")
        st.stop()

    if st.button("Iniciar Traducción Académica del Lote", type="primary"):
        if not is_ollama_healthy:
            st.error(
                f"❌ **Servicio de IA no disponible**: No se pudo conectar con Ollama en `{ollama_url}`. "
                "Por rigor científico y académico, **no se generan traducciones heurísticas simuladas**."
            )
            st.stop()

        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        translated_results = []

        for i, file in enumerate(uploaded_files):
            clean_name = FileValidator.sanitize_filename(file.name)
            file_bytes = file.getvalue()
            status_text.text(f"Procesando ({i+1}/{len(uploaded_files)}): {clean_name}...")

            try:
                # 1. Validar seguridad de archivo individual
                mime = FileValidator.detect_real_mime(file_bytes, clean_name)
                
                # 2. Extraer texto
                if mime == "application/pdf":
                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                    extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                else:
                    extracted_text = file_bytes.decode("utf-8", errors="replace")

                if not extracted_text.strip():
                    st.warning(f"⚠️ El archivo '{clean_name}' está vacío o no contiene texto extraíble.")
                    continue

                # 3. Traducir con el pipeline
                res = pipeline.translate_document(
                    text=extracted_text[:12000],  # Fragmento seguro
                    filename=clean_name,
                    target_lang=lang_code
                )
                translated_results.append(res)

            except Exception as e:
                st.error(f"Error procesando '{clean_name}': {str(e)}")

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("¡Traducción completada!")

        if translated_results:
            st.success(f"🎉 Se tradujeron exitosamente {len(translated_results)} documentos.")
            
            # Generar ZIP consolidado
            zip_data = TranslationConsolidator.create_consolidated_zip(translated_results)
            
            st.download_button(
                label="📦 Descargar Lote Traducido Consolidado (ZIP)",
                data=zip_data,
                file_name="traducciones_academicas_consolidadas.zip",
                mime="application/zip",
                type="primary"
            )

            # Previsualizar primera traducción
            with st.expander(f"Previsualizar traducción: {translated_results[0]['filename']}", expanded=True):
                st.text_area("Texto Traducido:", translated_results[0]["translated_text"], height=300)
