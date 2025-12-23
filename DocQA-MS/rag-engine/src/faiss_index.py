import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Tuple
from pathlib import Path
from config import FAISS_INDEX_PATH, EMBEDDING_DIMENSION, FAISS_NLIST, FAISS_NPROBE

class FAISSIndex:
    def __init__(self):
        self.index = None
        self.id_mapping = {}
        self.metadata_store = {}
        self.index_path = Path(FAISS_INDEX_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "faiss_index.idx"
        self.mapping_file = self.index_path / "id_mapping.pkl"
        self.metadata_file = self.index_path / "metadata.pkl"
    
    def initialize_index(self):
        quantizer = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
        self.index = faiss.IndexIVFFlat(quantizer, EMBEDDING_DIMENSION, FAISS_NLIST)
        self.index.nprobe = FAISS_NPROBE
        self.id_mapping = {}
        self.metadata_store = {}
    
    def load_index(self):
        if self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            self.index.nprobe = FAISS_NPROBE
            
            if self.mapping_file.exists():
                with open(self.mapping_file, 'rb') as f:
                    self.id_mapping = pickle.load(f)
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'rb') as f:
                    self.metadata_store = pickle.load(f)
        else:
            self.initialize_index()
    
    def save_index(self):
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))
            
            with open(self.mapping_file, 'wb') as f:
                pickle.dump(self.id_mapping, f)
            
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata_store, f)
    
    def train_index(self, embeddings: np.ndarray):
        if self.index is None:
            self.initialize_index()
        
        if not self.index.is_trained:
            self.index.train(embeddings.astype('float32'))
    
    def add_vectors(self, embeddings: np.ndarray, chunk_ids: List[int], metadata: List[Dict[str, Any]]):
        if self.index is None:
            self.load_index()
        
        if not self.index.is_trained:
            total_vectors_after = self.index.ntotal + len(embeddings) if hasattr(self.index, 'ntotal') else len(embeddings)
            if total_vectors_after < FAISS_NLIST:
                if not isinstance(self.index, faiss.IndexFlatL2):
                    self.index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
            else:
                self.train_index(embeddings)
        
        start_id = len(self.id_mapping)
        
        for i, (chunk_id, meta) in enumerate(zip(chunk_ids, metadata)):
            faiss_id = start_id + i
            self.id_mapping[faiss_id] = chunk_id
            self.metadata_store[chunk_id] = meta
        
        self.index.add(embeddings.astype('float32'))
        self.save_index()
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Dict[str, Any]]:
        if self.index is None:
            self.load_index()
        
        if self.index.ntotal == 0:
            return []
        
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            chunk_id = self.id_mapping.get(idx)
            if chunk_id is None:
                continue
            
            metadata = self.metadata_store.get(chunk_id, {})
            
            results.append({
                "chunk_id": chunk_id,
                "distance": float(distance),
                "score": float(1 / (1 + distance)),
                "metadata": metadata
            })
        
        return results
    
    def delete_document(self, document_id: int):
        chunks_to_remove = []
        
        for chunk_id, metadata in self.metadata_store.items():
            if metadata.get("document_id") == document_id:
                chunks_to_remove.append(chunk_id)
        
        if not chunks_to_remove:
            return
        
        faiss_ids_to_remove = [
            faiss_id for faiss_id, chunk_id in self.id_mapping.items()
            if chunk_id in chunks_to_remove
        ]
        
        if faiss_ids_to_remove:
            self.index.remove_ids(np.array(faiss_ids_to_remove, dtype=np.int64))
            
            for faiss_id in faiss_ids_to_remove:
                chunk_id = self.id_mapping.pop(faiss_id, None)
                if chunk_id:
                    self.metadata_store.pop(chunk_id, None)
            
            self.save_index()
    
    def get_stats(self) -> Dict[str, Any]:
        if self.index is None:
            self.load_index()
        
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": EMBEDDING_DIMENSION,
            "is_trained": self.index.is_trained if self.index else False,
            "nlist": FAISS_NLIST,
            "nprobe": FAISS_NPROBE
        }

faiss_index = FAISSIndex()

