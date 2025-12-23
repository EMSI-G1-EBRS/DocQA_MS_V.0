import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "docqa_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "docqa_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "docqa_pass")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "rabbitmq_user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "rabbitmq_pass")
RABBITMQ_QUEUE_INDEXER = "indexer_queue"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis_pass")

SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8004"))

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/app/faiss_index")
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIMENSION = 768

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

FAISS_NLIST = 100
FAISS_NPROBE = 10

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

