import os
import zipfile
from typing import Tuple, List, Dict, Any

MAX_SINGLE_FILE_MB = 15
MAX_BATCH_MB = 100

class FileSecurityException(Exception):
    pass

class FileValidator:
    """
    Validador de Seguridad para Archivos Académicos.
    Garantiza:
    1. Verificación de magic bytes (MIME real).
    2. Límites estrictos: 15 MB por archivo, 100 MB por lote.
    3. Mitigación contra Path Traversal (sanitización de rutas).
    4. Mitigación contra Zip Bombs (revisión de ratio de descompresión).
    """

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # Prevenir Path Traversal eliminando secuencias ../ o ..\\
        clean_name = os.path.basename(filename)
        clean_name = clean_name.replace("..", "").replace("/", "").replace("\\", "")
        return clean_name or "document_unnamed"

    @classmethod
    def validate_file_size(cls, file_bytes: bytes, filename: str) -> None:
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_SINGLE_FILE_MB:
            raise FileSecurityException(
                f"El archivo '{filename}' ({size_mb:.2f} MB) excede el límite máximo permitido de {MAX_SINGLE_FILE_MB} MB."
            )

    @classmethod
    def validate_batch_size(cls, total_bytes: int, count: int) -> None:
        total_mb = total_bytes / (1024 * 1024)
        if total_mb > MAX_BATCH_MB:
            raise FileSecurityException(
                f"El lote de {count} archivos ({total_mb:.2f} MB) excede el límite global de {MAX_BATCH_MB} MB."
            )

    @classmethod
    def detect_real_mime(cls, file_bytes: bytes, filename: str) -> str:
        """
        Inspecciona los magic bytes del archivo.
        """
        cls.validate_file_size(file_bytes, filename)
        
        # PDF magic bytes
        if file_bytes.startswith(b"%PDF-"):
            return "application/pdf"

        # Verificación de texto plano UTF-8 o ASCII
        try:
            # Intento de decodificación de muestra de 4KB
            sample = file_bytes[:4096].decode("utf-8")
            # Verificar si contiene bytes nulos (indicativo de binario)
            if "\x00" in sample:
                raise FileSecurityException(f"El archivo '{filename}' contiene bytes binarios no permitidos.")
            return "text/plain"
        except UnicodeDecodeError:
            raise FileSecurityException(
                f"El archivo '{filename}' no es un PDF válido ni un texto plano UTF-8 compatible."
            )

    @classmethod
    def inspect_zip_safety(cls, zip_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Inspecciona un archivo ZIP para prevenir Zip Bombs antes de extraerlo.
        """
        import io
        safe_files = []
        total_uncompressed = 0

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            infolist = zf.infolist()
            for info in infolist:
                # Detección de path traversal en el ZIP
                if ".." in info.filename or info.filename.startswith("/") or info.filename.startswith("\\"):
                    raise FileSecurityException(f"Detección de Path Traversal en el archivo interno: {info.filename}")

                total_uncompressed += info.file_size
                compressed_size = max(1, info.compress_size)
                ratio = info.file_size / compressed_size

                # Si el ratio de compresión es sospechosamente alto (> 15x) y archivo > 10MB
                if ratio > 15.0 and info.file_size > 10 * 1024 * 1024:
                    raise FileSecurityException(
                        f"Alerta de Zip Bomb: '{info.filename}' tiene un ratio de compresión de {ratio:.1f}x."
                    )

            if total_uncompressed > MAX_BATCH_MB * 1024 * 1024:
                raise FileSecurityException(
                    f"El contenido descomprimido del ZIP ({total_uncompressed / (1024*1024):.1f} MB) supera el límite de {MAX_BATCH_MB} MB."
                )

        return [{"total_uncompressed_bytes": total_uncompressed, "entries": len(infolist)}]
