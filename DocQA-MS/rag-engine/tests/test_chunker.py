import pytest
from src.chunker import MedicalChunker

class TestMedicalChunker:
    def test_detect_sections(self):
        chunker = MedicalChunker()
        text = """
        ANAMNÈSE
        Le patient présente des symptômes.
        
        DIAGNOSTIC
        Diagnostic confirmé.
        
        TRAITEMENT
        Prescription médicamenteuse.
        """
        sections = chunker.detect_sections(text)
        assert len(sections) > 0
    
    def test_chunk_text(self):
        chunker = MedicalChunker(chunk_size=100, chunk_overlap=10)
        text = "Test content " * 50
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)

