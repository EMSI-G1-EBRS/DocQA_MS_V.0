from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from config import EMBEDDING_MODEL

def preload_models():
    print(f"Préchargement du modèle d'embedding: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Modèle d'embedding chargé avec succès")
    
    print("Préchargement du tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    print("Tokenizer chargé avec succès")
    
    print("Tous les modèles sont prêts")

if __name__ == "__main__":
    preload_models()

