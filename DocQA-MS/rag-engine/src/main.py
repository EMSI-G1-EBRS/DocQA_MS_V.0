from fastapi import FastAPI, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import threading

from src.database import get_db
from indexer_service import indexer_service
from hybrid_search import hybrid_search
from faiss_index import faiss_index
from rabbitmq_consumer import rabbitmq_consumer
from embedder import embedder
from config import SERVICE_PORT
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IndexeurSémantique API",
    description="Service d'indexation vectorielle et recherche sémantique",
    version="1.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmbedRequest(BaseModel):
    document_id: int
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    use_hybrid: bool = True

@app.get("/")
def read_root():
    return {"service": "IndexeurSémantique", "status": "operational"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/index/embed")
async def embed_document(
    request: EmbedRequest,
    db: Session = Depends(get_db)
):
    try:
        result = indexer_service.index_document(
            document_id=request.document_id,
            content=request.content,
            metadata=request.metadata
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation: {str(e)}")

@app.post("/index/search")
async def search_documents(request: SearchRequest):
    try:
        if request.use_hybrid:
            results = hybrid_search.search(
                query=request.query,
                top_k=request.top_k,
                filters=request.filters
            )
        else:
            results = indexer_service.search(
                query=request.query,
                top_k=request.top_k,
                filters=request.filters
            )
        
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")

@app.delete("/index/document/{document_id}")
async def delete_document(document_id: int):
    try:
        result = indexer_service.delete_document(document_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@app.get("/index/stats")
def get_stats():
    return {
        "faiss_stats": faiss_index.get_stats(),
        "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
        "embedding_dimension": 768
    }

@app.on_event("startup")
async def startup_event():
    print("Starting RabbitMQ consumer...", flush=True)
    consumer_thread = threading.Thread(target=rabbitmq_consumer.start_consuming, daemon=True)
    consumer_thread.start()
    
    print("Loading FAISS index...", flush=True)
    faiss_index.load_index()

    print("Startup complete!", flush=True)

@app.on_event("shutdown")
async def shutdown_event():
    rabbitmq_consumer.stop_consuming()
    rabbitmq_consumer.close()
    faiss_index.save_index()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
