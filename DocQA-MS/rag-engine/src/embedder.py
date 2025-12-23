import numpy as np
import threading
from sentence_transformers import SentenceTransformer
from typing import List, Union
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSION

class Embedder:
    def __init__(self):
        self.model = None
        self.model_name = EMBEDDING_MODEL
        self._lock = threading.Lock()
    
    def load_model(self):
        with self._lock:
            if self.model is None:
                self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if self.model is None:
            self.load_model()
        
        if isinstance(text, str):
            text = [text]
        
        max_chars = 1500
        text = [t[:max_chars] if len(t) > max_chars else t for t in text]
        
        embeddings = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        if self.model is None:
            self.load_model()
        
        max_chars = 1500
        texts = [t[:max_chars] if len(t) > max_chars else t for t in texts]
        
        print(f"Embedding batch of {len(texts)} texts...", flush=True)
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        print("Embedding complete.", flush=True)
        
        return embeddings

embedder = Embedder()

