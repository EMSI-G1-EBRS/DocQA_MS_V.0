import pytest
import numpy as np
from src.embedder import Embedder

class TestEmbedder:
    def test_embed_text_single(self):
        embedder = Embedder()
        text = "Test document"
        embedding = embedder.embed_text(text)
        assert embedding.shape == (1, 768)
        assert isinstance(embedding, np.ndarray)
    
    def test_embed_text_multiple(self):
        embedder = Embedder()
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = embedder.embed_text(texts)
        assert embeddings.shape == (3, 768)
    
    def test_embed_normalized(self):
        embedder = Embedder()
        text = "Test"
        embedding = embedder.embed_text(text)
        norm = np.linalg.norm(embedding[0])
        assert abs(norm - 1.0) < 0.01

