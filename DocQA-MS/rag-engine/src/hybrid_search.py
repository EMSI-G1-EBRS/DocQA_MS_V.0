from typing import List, Dict, Any
import numpy as np
from indexer_service import indexer_service
from bm25_search import bm25_search
from src.database import SessionLocal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "DocQA-MS-Backend" / "database"))
from models import Chunk

class HybridSearch:
    def __init__(self, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        vector_results = indexer_service.search(query, top_k=top_k * 2, filters=filters)
        
        db = SessionLocal()
        try:
            all_chunks = db.query(Chunk).all()
            chunks_data = [
                {
                    "chunk_id": chunk.id,
                    "text": chunk.texte,
                    "metadata": chunk.chunk_metadata or {}
                }
                for chunk in all_chunks
            ]
        finally:
            db.close()
        
        if chunks_data:
            bm25_search.build_index(chunks_data)
            bm25_results = bm25_search.search(query, top_k=top_k * 2)
        else:
            bm25_results = []
        
        combined_results = self._combine_results(vector_results, bm25_results)
        
        if filters:
            combined_results = self._apply_filters(combined_results, filters)
        
        combined_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        return combined_results[:top_k]
    
    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        
        vector_scores = {r["chunk_id"]: r["score"] for r in vector_results}
        bm25_scores = {r["chunk_id"]: r["bm25_score"] for r in bm25_results}
        
        max_vector = max(vector_scores.values()) if vector_scores else 1.0
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        
        all_chunk_ids = set(vector_scores.keys()) | set(bm25_scores.keys())
        
        combined = []
        for chunk_id in all_chunk_ids:
            vector_score = (vector_scores.get(chunk_id, 0) / max_vector) if max_vector > 0 else 0
            bm25_score = (bm25_scores.get(chunk_id, 0) / max_bm25) if max_bm25 > 0 else 0
            
            hybrid_score = (
                self.vector_weight * vector_score +
                self.bm25_weight * bm25_score
            )
            
            result = {
                "chunk_id": chunk_id,
                "hybrid_score": hybrid_score,
                "vector_score": vector_score,
                "bm25_score": bm25_score,
                "metadata": {}
            }
            
            for r in vector_results:
                if r["chunk_id"] == chunk_id:
                    result.update(r)
                    break
            
            combined.append(result)
        
        return combined
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered = []
        for result in results:
            metadata = result.get("metadata", {})
            match = True
            
            if "document_id" in filters and metadata.get("document_id") != filters["document_id"]:
                match = False
            if "section_type" in filters and metadata.get("section_type") != filters["section_type"]:
                match = False
            
            if match:
                filtered.append(result)
        
        return filtered

hybrid_search = HybridSearch()

