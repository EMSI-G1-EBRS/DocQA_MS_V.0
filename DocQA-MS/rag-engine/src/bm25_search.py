from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import re

class BM25Search:
    def __init__(self):
        self.bm25_index = None
        self.chunks = []
        self.chunk_ids = []
    
    def build_index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        
        tokenized_corpus = [
            self._tokenize(chunk["text"]) for chunk in chunks
        ]
        
        self.bm25_index = BM25Okapi(tokenized_corpus)
    
    def _tokenize(self, text: str) -> List[str]:
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        return tokens
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.bm25_index is None:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25_index.get_scores(tokenized_query)
        
        scored_chunks = [
            {
                "chunk_id": self.chunk_ids[i],
                "bm25_score": float(score),
                "metadata": self.chunks[i].get("metadata", {})
            }
            for i, score in enumerate(scores)
        ]
        
        scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)
        
        return scored_chunks[:top_k]

bm25_search = BM25Search()

