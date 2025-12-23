import time
from typing import List, Dict, Any
from indexer_service import indexer_service
from hybrid_search import hybrid_search

class Benchmark:
    def __init__(self):
        self.results = []
    
    def benchmark_embedding(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        
        total_chunks = 0
        for doc in documents:
            result = indexer_service.index_document(
                document_id=doc["document_id"],
                content=doc["content"],
                metadata=doc.get("metadata")
            )
            total_chunks += result.get("chunks_count", 0)
        
        elapsed_time = time.time() - start_time
        
        return {
            "operation": "embedding",
            "documents_count": len(documents),
            "total_chunks": total_chunks,
            "elapsed_time": elapsed_time,
            "chunks_per_second": total_chunks / elapsed_time if elapsed_time > 0 else 0
        }
    
    def benchmark_search(self, queries: List[str], top_k: int = 10) -> Dict[str, Any]:
        start_time = time.time()
        
        total_results = 0
        for query in queries:
            results = hybrid_search.search(query, top_k=top_k)
            total_results += len(results)
        
        elapsed_time = time.time() - start_time
        
        return {
            "operation": "search",
            "queries_count": len(queries),
            "total_results": total_results,
            "elapsed_time": elapsed_time,
            "queries_per_second": len(queries) / elapsed_time if elapsed_time > 0 else 0,
            "avg_results_per_query": total_results / len(queries) if queries else 0
        }
    
    def benchmark_recall_at_k(
        self,
        queries: List[Dict[str, Any]],
        k: int = 10
    ) -> Dict[str, Any]:
        
        correct_results = 0
        total_queries = len(queries)
        
        for query_data in queries:
            query = query_data["query"]
            expected_docs = set(query_data.get("expected_documents", []))
            
            results = hybrid_search.search(query, top_k=k)
            retrieved_docs = {r.get("document_id") for r in results if r.get("document_id")}
            
            if expected_docs and retrieved_docs:
                intersection = expected_docs & retrieved_docs
                if intersection:
                    correct_results += 1
        
        recall = correct_results / total_queries if total_queries > 0 else 0
        
        return {
            "metric": f"recall@{k}",
            "total_queries": total_queries,
            "correct_results": correct_results,
            "recall": recall
        }

benchmark = Benchmark()

