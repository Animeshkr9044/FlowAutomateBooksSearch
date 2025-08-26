import json
import uuid
from typing import List, Dict
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configuration
@dataclass
class Config:
    qdrant_url: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "bookstore_collection"
    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    openai_model: str = "gpt-4o"
    vector_size: int = 1024

class DataIngestion:
    def __init__(self, config: Config):
        self.config = config
        self.client = QdrantClient(host=config.qdrant_url, port=config.qdrant_port)
        self.embedding_model = SentenceTransformer(config.embedding_model)

    def setup_collection(self):
        """Initialize Qdrant collection"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(self.config.collection_name)
                print(f"Deleted existing collection: {self.config.collection_name}")
            except Exception:
                pass

            # Create new collection
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {self.config.collection_name}")
            
        except Exception as e:
            print(f"Error setting up collection: {e}")

    def prepare_documents(self, store_a_data: List[Dict], store_b_data: List[Dict]) -> List[Dict]:
        """Prepare documents for embedding with normalized schemas"""
        documents = []
        
        # Process Store A data
        for book in store_a_data:
            doc = {
                "id": str(uuid.uuid4()),
                "text": book["description"],  # This will be embedded
                "store": "store_a",
                "metadata": {
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "publication_year": book["publication_year"],
                    "isbn": book.get("isbn", ""),
                    "book_id": book["book_id"],
                    "genre": book["genre"].lower(),
                    "rating": book["rating"],
                    "description": book["description"]
                }
            }
            documents.append(doc)
        
        # Process Store B data
        for book in store_b_data:
            doc = {
                "id": str(uuid.uuid4()),
                "text": book["summary"],  # This will be embedded
                "store": "store_b", 
                "metadata": {
                    "title": book["book_name"],
                    "author": book["writer"],
                    "price": book["cost"],
                    "publication_year": book.get("publication_year", 2020),
                    "isbn": book.get("isbn", ""),
                    "product_id": book["product_id"],
                    "genre": [g.lower() for g in book["category"]],
                    "reviews_count": book["reviews_count"],
                    "summary": book["summary"],
                    "publisher": book.get("publisher", ""),
                    "stock": book["stock"]
                }
            }
            documents.append(doc)
            
        return documents

    def index_documents(self, documents: List[Dict]):
        """Create embeddings and index documents in Qdrant"""
        print(f"Creating embeddings for {len(documents)} documents...")
        
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            point = PointStruct(
                id=doc["id"],
                vector=embedding.tolist(),
                payload={
                    "store": doc["store"],
                    "text": doc["text"],
                    **doc["metadata"]
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.config.collection_name,
            points=points
        )
        print(f"Indexed {len(points)} documents in Qdrant")

def run_ingestion():
    """Main function to run the data ingestion process"""
    config = Config()
    ingestion_system = DataIngestion(config)
    
    print("🚀 Starting data ingestion...")
    
    ingestion_system.setup_collection()
    
    print("📚 Loading bookstore data...")
    try:
        with open('data/store_a_books.json', 'r') as f:
            store_a_data = json.load(f)
        with open('data/store_b_books.json', 'r') as f:
            store_b_data = json.load(f)
    except FileNotFoundError:
        print("❌ Please run the dataset generator first to create the JSON files!")
        return
    
    documents = ingestion_system.prepare_documents(store_a_data, store_b_data)
    ingestion_system.index_documents(documents)
    
    print("✅ Data ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
