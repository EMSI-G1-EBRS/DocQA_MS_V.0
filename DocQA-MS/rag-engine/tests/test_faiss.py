import pytest
import numpy as np
from src.faiss_index import FAISSIndex

class TestFAISSIndex:
    def test_initialize_index(self):
        index = FAISSIndex()
        index.initialize_index()
        assert index.index is not None
        assert not index.index.is_trained
    
    def test_add_vectors(self):
        index = FAISSIndex()
        index.initialize_index()
        
        embeddings = np.random.rand(10, 768).astype('float32')
        chunk_ids = list(range(10))
        metadata = [{"chunk_id": i} for i in range(10)]
        
        index.train_index(embeddings)
        index.add_vectors(embeddings, chunk_ids, metadata)
        
        assert index.index.ntotal == 10
    
    def test_search(self):
        index = FAISSIndex()
        index.initialize_index()
        
        embeddings = np.random.rand(10, 768).astype('float32')
        chunk_ids = list(range(10))
        metadata = [{"chunk_id": i} for i in range(10)]
        
        index.train_index(embeddings)
        index.add_vectors(embeddings, chunk_ids, metadata)
        
        query = np.random.rand(1, 768).astype('float32')
        results = index.search(query, k=5)
        
        assert len(results) <= 5
        assert all("chunk_id" in r for r in results)

