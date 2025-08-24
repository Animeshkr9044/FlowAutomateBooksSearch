import json
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

# Core libraries
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, Match, Range, MatchValue
)
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
import pandas as pd

# Configuration
@dataclass
class Config:
    qdrant_url: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "bookstore_collection"
    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"  # Fast, good quality embeddings
    openai_model: str = "gpt-4o"
    vector_size: int = 1024  # Dimension for all-MiniLM-L6-v2

class BookstoreRAGSystem:
    def __init__(self, config: Config):
        self.config = config
        self.client = QdrantClient(host=config.qdrant_url, port=config.qdrant_port)
        self.embedding_model = SentenceTransformer(config.embedding_model)
        self.openai_client = AsyncOpenAI()
        
        # Schema information for the agent
        self.store_schemas = {
            "store_a": {
                "fields": ["book_id", "title", "author", "genre", "price", "rating", "description", "isbn", "publication_year"],
                "field_types": {
                    "book_id": "string", "title": "string", "author": "string", 
                    "genre": "string", "price": "float", "rating": "float",
                    "description": "string", "isbn": "string", "publication_year": "integer"
                },
                "filterable_fields": ["author", "genre", "price", "rating", "publication_year"]
            },
            "store_b": {
                "fields": ["product_id", "book_name", "writer", "category", "cost", "reviews_count", "summary", "publisher", "stock"],
                "field_types": {
                    "product_id": "string", "book_name": "string", "writer": "string",
                    "category": "array", "cost": "float", "reviews_count": "integer",
                    "summary": "string", "publisher": "string", "stock": "integer"
                },
                "filterable_fields": ["writer", "category", "cost", "reviews_count", "publisher", "stock"]
            }
        }

    async def setup_collection(self):
        """Initialize Qdrant collection"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(self.config.collection_name)
                print(f"Deleted existing collection: {self.config.collection_name}")
            except:
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
                    # Normalized fields for cross-store queries
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "publication_year": book["publication_year"],
                    "isbn": book.get("isbn", ""),
                    
                    # Store-specific fields
                    "book_id": book["book_id"],
                    "genre": book["genre"],
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
                    # Normalized fields for cross-store queries
                    "title": book["book_name"],
                    "author": book["writer"],
                    "price": book["cost"],
                    "publication_year": book.get("publication_year", 2020),  # Default if missing
                    "isbn": book.get("isbn", ""),
                    
                    # Store-specific fields
                    "product_id": book["product_id"],
                    "category": book["category"],
                    "reviews_count": book["reviews_count"],
                    "summary": book["summary"],
                    "publisher": book.get("publisher", ""),
                    "stock": book["stock"]
                }
            }
            documents.append(doc)
            
        return documents

    async def index_documents(self, documents: List[Dict]):
        """Create embeddings and index documents in Qdrant"""
        print(f"Creating embeddings for {len(documents)} documents...")
        
        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Prepare points for Qdrant
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
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.config.collection_name,
            points=points
        )
        print(f"Indexed {len(points)} documents in Qdrant")

    def generate_filter_query_prompt(self, user_query: str) -> str:
        """Generate prompt for the agent to create Qdrant filters"""
        schema_info = json.dumps(self.store_schemas, indent=2)
        
        prompt = f"""
You are an expert at converting natural language queries into Qdrant database filters for a bookstore search system.

AVAILABLE SCHEMAS:
{schema_info}

FIELD MAPPINGS BETWEEN STORES:
- title (store_a) ↔ book_name → title (normalized)  
- author (store_a) ↔ writer → author (normalized)
- genre (store_a) ↔ category → [use original field names]
- price (store_a) ↔ cost → price (normalized)  
- rating (store_a) ↔ reviews_count → [use original field names]
- description (store_a) ↔ summary → [embedded as text]

USER QUERY: "{user_query}"

Generate Qdrant filters based on this query. Return ONLY valid JSON that can be parsed.

FILTER FORMAT EXAMPLES:
1. Price filter: {{"must": [{{"key": "price", "range": {{"gte": 10, "lte": 20}}}}]}}
2. Author filter: {{"must": [{{"key": "author", "match": {{"value": "Stephen King"}}}}]}}
3. Store filter: {{"must": [{{"key": "store", "match": {{"value": "store_a"}}}}]}}
4. Genre filter: {{"must": [{{"key": "genre", "match": {{"value": "Science Fiction"}}}}]}}
5. Multiple filters: {{"must": [{{"key": "author", "match": {{"value": "Andy Weir"}}}}, {{"key": "price", "range": {{"lte": 20}}}}]}}
6. Category filter (store_b): {{"must": [{{"key": "category", "match": {{"any": ["Science Fiction"]}}}}]}}

RULES:
1. Use "price" for price comparisons (normalized field)
2. Use "author" for author searches (normalized field)  
3. Use "title" for title searches (normalized field)
4. Use "store" field to filter by store: "store_a" or "store_b"
5. For store-specific fields, use original names: "genre", "category", "rating", "reviews_count"
6. For "any store" queries, don't add store filter
7. For "cheaper/expensive" comparisons, create appropriate ranges
8. For "popular/highly-rated", use rating > 4.0 or reviews_count > 500

If no specific filters are needed (general search), return: {{"must": []}}
"""
        return prompt

    async def generate_filters(self, user_query: str) -> Dict:
        """Use GPT to generate Qdrant filters from natural language"""
        try:
            prompt = self.generate_filter_query_prompt(user_query)
            
            print("📞 Calling OpenAI to generate filters...")
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a database query expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            filter_json = response.choices[0].message.content.strip()
            
            # Clean up the response
            if filter_json.startswith("```json"):
                filter_json = filter_json.replace("```json", "").replace("```", "").strip()
            
            filters = json.loads(filter_json)
            print(f"Generated filters: {filters}")
            return filters
            
        except Exception as e:
            print(f"Error generating filters: {e}")
            return {"must": []}  # Return empty filter on error

    def build_qdrant_filter(self, filter_dict: Dict) -> Optional[Filter]:
        """Convert filter dictionary to Qdrant Filter object"""
        try:
            if not filter_dict.get("must"):
                return None
                
            conditions = []
            for condition in filter_dict["must"]:
                key = condition["key"]
                
                if "match" in condition:
                    match_condition = condition["match"]
                    if "value" in match_condition:
                        # Single value match
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=match_condition["value"]))
                        )
                    elif "any" in match_condition:
                        # Array match (for categories)
                        for value in match_condition["any"]:
                            conditions.append(
                                FieldCondition(key=key, match=MatchValue(value=value))
                            )
                
                elif "range" in condition:
                    range_condition = condition["range"]
                    conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(
                                gte=range_condition.get("gte"),
                                lte=range_condition.get("lte"),
                                gt=range_condition.get("gt"),
                                lt=range_condition.get("lt")
                            )
                        )
                    )
            
            return Filter(must=conditions) if conditions else None
            
        except Exception as e:
            print(f"Error building Qdrant filter: {e}")
            return None

    async def search(self, query: str, limit: int = 10) -> Dict:
        """Main search function"""
        print(f"\n🔍 Processing query: '{query}'")
        
        # Step 1: Generate filters using the agent
        filter_dict = await self.generate_filters(query)
        qdrant_filter = self.build_qdrant_filter(filter_dict)
        
        # Step 2: Create query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Step 3: Search Qdrant
        search_results = self.client.search(
            collection_name=self.config.collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=limit,
            with_payload=True
        )
        
        # Step 4: Process and format results
        results = {
            "query": query,
            "filters_applied": filter_dict,
            "total_results": len(search_results),
            "results": []
        }
        
        for result in search_results:
            payload = result.payload
            formatted_result = {
                "score": round(result.score, 4),
                "store": payload["store"],
                "title": payload["title"],
                "author": payload["author"],
                "price": payload["price"],
                "text_snippet": payload["text"][:200] + "..." if len(payload["text"]) > 200 else payload["text"],
                "metadata": {k: v for k, v in payload.items() if k not in ["text", "title", "author", "price", "store"]}
            }
            results["results"].append(formatted_result)
        
        return results

    def print_results(self, results: Dict):
        """Pretty print search results"""
        print(f"\n{'='*60}")
        print(f"QUERY: {results['query']}")
        print(f"FILTERS APPLIED: {json.dumps(results['filters_applied'], indent=2)}")
        print(f"TOTAL RESULTS: {results['total_results']}")
        print(f"{'='*60}")
        
        for i, result in enumerate(results["results"], 1):
            print(f"\n{i}. 📚 {result['title']}")
            print(f"   Author: {result['author']}")
            print(f"   Store: {result['store'].upper()}")
            print(f"   Price: ${result['price']}")
            print(f"   Relevance: {result['score']}")
            print(f"   Text: {result['text_snippet']}")
            
            # Show store-specific metadata
            metadata = result['metadata']
            if result['store'] == 'store_a':
                print(f"   Genre: {metadata.get('genre', 'N/A')}")
                print(f"   Rating: {metadata.get('rating', 'N/A')}/5.0")
            else:
                print(f"   Categories: {metadata.get('category', 'N/A')}")
                print(f"   Reviews: {metadata.get('reviews_count', 'N/A')}")
                print(f"   Stock: {metadata.get('stock', 'N/A')}")
            print("-" * 50)

# Demo and testing functions
async def main():
    """Main function to demonstrate the system"""
    
    # Initialize system
    config = Config()
    rag_system = BookstoreRAGSystem(config)
    
    print("🚀 Setting up Bookstore RAG System...")
    
    # Setup collection
    await rag_system.setup_collection()
    
    # Load data (you need to run the dataset generator first)
    print("📚 Loading bookstore data...")
    try:
        with open('data/store_a_books.json', 'r') as f:
            store_a_data = json.load(f)
        with open('data/store_b_books.json', 'r') as f:
            store_b_data = json.load(f)
    except FileNotFoundError:
        print("❌ Please run the dataset generator first to create the JSON files!")
        return
    
    # Prepare and index documents
    documents = rag_system.prepare_documents(store_a_data, store_b_data)
    await rag_system.index_documents(documents)
    
    print("✅ System setup complete!")
    
    # Test queries
    test_queries = [
        "Find books about space exploration",
        "Show me Stephen King books under $20",
        "Which store has cheaper science fiction books?",
        "Find highly rated books in store A",
        "Books by Andy Weir available in both stores",
        "Fantasy books with good reviews",
        "Books published after 2015 under $15"
    ]
    
    print(f"\n🧪 Running test queries...")
    for query in test_queries:
        try:
            results = await rag_system.search(query)
            rag_system.print_results(results)
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"❌ Error processing query '{query}': {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())