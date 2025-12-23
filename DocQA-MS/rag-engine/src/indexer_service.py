from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
import numpy as np

from src.database import get_db, SessionLocal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "DocQA-MS-Backend" / "database"))
from models import Document, Chunk
from chunker import chunker
from embedder import embedder
from faiss_index import faiss_index
from config import EMBEDDING_DIMENSION

class IndexerService:
    def __init__(self):
        self.chunker = chunker
        self.embedder = embedder
        self.faiss_index = faiss_index
    
    def index_document(
        self,
        document_id: int,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        
        db = SessionLocal()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} non trouvé")
            
            existing_chunks = db.query(Chunk).filter(Chunk.document_id == document_id).all()
            for chunk in existing_chunks:
                db.delete(chunk)
            db.commit()
            
            chunks_data = self.chunker.chunk_text(content, metadata or {})
            print(f"Document {document_id}: Content length={len(content)} chars. Generated {len(chunks_data)} chunks.", flush=True)
            
            if not chunks_data:
                return {"status": "error", "message": "Aucun chunk généré"}
            
            chunk_texts = [chunk["text"] for chunk in chunks_data]
            embeddings = self.embedder.embed_batch(chunk_texts)
            
            chunk_ids = []
            for i, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings)):
                chunk = Chunk(
                    document_id=document_id,
                    texte=chunk_data["text"],
                    embedding_vector=embedding.tolist(),
                    position=chunk_data["position"],
                    chunk_metadata=chunk_data["metadata"]
                )
                db.add(chunk)
                db.flush()
                chunk_ids.append(chunk.id)
            
            db.commit()
            
            chunk_metadata = [
                {
                    **chunk_data["metadata"],
                    "document_id": document_id,
                    "chunk_id": chunk_id
                }
                for chunk_data, chunk_id in zip(chunks_data, chunk_ids)
            ]
            
            self.faiss_index.add_vectors(embeddings, chunk_ids, chunk_metadata)
            
            return {
                "status": "success",
                "document_id": document_id,
                "chunks_count": len(chunks_data),
                "chunk_ids": chunk_ids
            }
        
        finally:
            db.close()
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        query_embedding = self.embedder.embed_text(query)
        
        results = self.faiss_index.search(query_embedding, k=top_k * 2)
        
        if filters:
            results = self._apply_filters(results, filters)
        
        results = results[:top_k]
        
        db = SessionLocal()
        try:
            for result in results:
                chunk = db.query(Chunk).filter(Chunk.id == result["chunk_id"]).first()
                if chunk:
                    result["text"] = chunk.texte
                    result["document_id"] = chunk.document_id
        finally:
            db.close()
        
        return results
    
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
    
    def delete_document(self, document_id: int) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            chunks = db.query(Chunk).filter(Chunk.document_id == document_id).all()
            
            self.faiss_index.delete_document(document_id)
            
            for chunk in chunks:
                db.delete(chunk)
            db.commit()
            
            return {
                "status": "success",
                "document_id": document_id,
                "chunks_deleted": len(chunks)
            }
        finally:
            db.close()

indexer_service = IndexerService()

