import unittest
import io
import zipfile
from apps.academic_translator.security.file_validator import FileValidator, FileSecurityException
from apps.academic_translator.agents.translator_pipeline import AcademicTranslatorPipeline
from apps.academic_translator.utils.consolidator import TranslationConsolidator

class TestAcademicTranslatorSatellite(unittest.TestCase):
    def test_file_validator_pdf_and_text(self):
        # Valid PDF header
        pdf_bytes = b"%PDF-1.4\n%test academic manuscript"
        mime = FileValidator.detect_real_mime(pdf_bytes, "paper.pdf")
        self.assertEqual(mime, "application/pdf")

        # Valid text
        txt_bytes = "Epidemiological digital twin in Kenya".encode("utf-8")
        mime_txt = FileValidator.detect_real_mime(txt_bytes, "notes.txt")
        self.assertEqual(mime_txt, "text/plain")

        # Binary with null bytes should be rejected
        bad_bytes = b"Hello\x00World\x00Binary"
        with self.assertRaises(FileSecurityException):
            FileValidator.detect_real_mime(bad_bytes, "binary.txt")

    def test_file_size_limits(self):
        # 16 MB bytes should fail
        large_bytes = b"0" * (16 * 1024 * 1024)
        with self.assertRaises(FileSecurityException):
            FileValidator.validate_file_size(large_bytes, "large.pdf")

        # 101 MB batch should fail
        with self.assertRaises(FileSecurityException):
            FileValidator.validate_batch_size(101 * 1024 * 1024, 15)

    def test_path_traversal_sanitization(self):
        malicious_name = "../../../etc/passwd"
        clean = FileValidator.sanitize_filename(malicious_name)
        self.assertEqual(clean, "passwd")
        self.assertNotIn("..", clean)
        self.assertNotIn("/", clean)

    def test_glossary_loaded(self):
        pipeline = AcademicTranslatorPipeline(api_key="")
        self.assertGreater(len(pipeline.glossary), 10)
        self.assertIn("SEIR", pipeline.glossary)
        self.assertIn("DALYs", pipeline.glossary)
        self.assertIn("ICER", pipeline.glossary)

    def test_pipeline_raises_when_ollama_unreachable(self):
        pipeline = AcademicTranslatorPipeline(base_url="http://127.0.0.1:59999")
        with self.assertRaises(RuntimeError) as ctx:
            pipeline.translate_document("Test paper", "paper.txt")
        self.assertIn("No se pudo conectar con el servicio local Ollama", str(ctx.exception))

    def test_consolidator_creates_valid_zip(self):
        dummy_translations = [
            {"filename": "study1.txt", "translated_text": "Estudio epidemiológico 1", "status": "COMPLETED"},
            {"filename": "study2.pdf", "translated_text": "Estudio epidemiológico 2", "status": "COMPLETED"}
        ]
        zip_bytes = TranslationConsolidator.create_consolidated_zip(dummy_translations)
        self.assertTrue(len(zip_bytes) > 100)

        # Verify ZIP can be read
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            files = zf.namelist()
            self.assertIn("translated_study1.txt", files)
            self.assertIn("translated_study2.txt", files)
            self.assertIn("INDICE_TRADUCCIONES.md", files)
            self.assertIn("metadata.json", files)

if __name__ == "__main__":
    unittest.main()
