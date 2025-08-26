import json
import asyncio
import time
from typing import Dict, Optional

# Core libraries
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, FieldCondition, Match, Range, MatchValue
)
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer

# Local imports
from data_ingestion import Config
from tools.prompt_tools import generate_filter_query_prompt
from tools.qdrant_tools import QdrantSearcher

class BookstoreRAGSystem:
    def __init__(self, config: Config):
        self.config = config
        self.client = QdrantClient(host=config.qdrant_url, port=config.qdrant_port)
        self.embedding_model = SentenceTransformer(config.embedding_model)
        self.openai_client = AsyncOpenAI()
        self.qdrant_searcher = QdrantSearcher(client=self.client, collection_name=config.collection_name)

    def collection_exists(self) -> bool:
        """Check if the Qdrant collection exists."""
        try:
            self.client.get_collection(collection_name=self.config.collection_name)
            return True
        except Exception:
            return False

    async def generate_filters(self, user_query: str) -> Dict:
        """Use GPT to generate Qdrant filters from natural language"""
        try:
            prompt = generate_filter_query_prompt(user_query)
            
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


    async def search(self, query: str, limit: int = 10) -> Dict:
        """Main search function"""
        print(f"\n🔍 Processing query: '{query}'")
        
        # Step 1: Generate filters using the agent
        start_time = time.time()
        filter_dict = await self.generate_filters(query)
        qdrant_filter = self.qdrant_searcher.build_qdrant_filter(filter_dict)
        end_time = time.time()
        print(f"⏱️ Filter generation took: {end_time - start_time:.2f} seconds")

        # Step 2: Create query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        # Step 3: Search Qdrant
        start_time = time.time()
        search_results = self.qdrant_searcher.search(
            query_embedding=query_embedding,
            qdrant_filter=qdrant_filter,
            limit=limit
        )
        end_time = time.time()
        print(f"⏱️ Qdrant search took: {end_time - start_time:.2f} seconds")
        
        # Step 4: Process and format results
        results = {
            "query": query,
            "filters_applied": filter_dict,
            "total_results": len(search_results.points),
            "results": []
        }
        
        for result in search_results.points:
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

    def get_all_books(self) -> list:
        """Fetch all books from the Qdrant collection."""
        return self.qdrant_searcher.scroll_all()
