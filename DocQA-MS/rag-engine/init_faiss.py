import os
import faiss
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

faiss_index_path = os.getenv("FAISS_INDEX_PATH", "/app/faiss_index")
dimension = 768
nlist = 100

index_dir = Path(faiss_index_path)
index_dir.mkdir(parents=True, exist_ok=True)

index = faiss.IndexIVFFlat(faiss.IndexFlatL2(dimension), dimension, nlist)
index.nprobe = 10

index_file = index_dir / "faiss_index.idx"
faiss.write_index(index, str(index_file))

print(f"FAISS index initialized at {index_file}")
print(f"Dimension: {dimension}, nlist: {nlist}")

