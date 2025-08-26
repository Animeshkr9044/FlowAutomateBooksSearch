import asyncio
import json
from typing import Type, Any

from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool

import pandas as pd
from book_agent import BookstoreRAGSystem
from data_ingestion import Config

class BookSearchInput(BaseModel):
    """Input model for the BookSearchTool."""
    query: str = Field(description="The natural language query for searching books.")

class BookAnalyticsInput(BaseModel):
    """Input model for the BookAnalyticsTool."""
    query: str = Field(description="The analytical query, e.g., 'most popular genre per store'.")

class BookAnalyticsTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = "Book Analytics Tool"
    description: str = "Performs data analysis on book data to answer analytical queries like 'most popular genre'."
    args_schema: Type[BaseModel] = BookAnalyticsInput
    rag_system: BookstoreRAGSystem = None
    last_result: str = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        config = Config()
        self.rag_system = BookstoreRAGSystem(config)
        self.last_result = None

    def _run(self, query: str) -> str:
        """Use the RAG system to fetch all books and analyze them based on the query."""
        all_books = self.rag_system.get_all_books()
        if not all_books:
            self.last_result = json.dumps({"error": "Could not retrieve any books to analyze."})
            return self.last_result

        df = pd.DataFrame([book.payload for book in all_books])
        print(f"df: {df}")
        
        # More specific routing for complex queries
        if "cheapest" in query.lower() and "genre" in query.lower():
            # Extract genre from query, simple approach
            words = query.lower().split()
            try:
                genre_index = words.index("genre") - 1
                genre = words[genre_index]
                result = self._analyze_cheapest_by_genre(df, genre)
            except (ValueError, IndexError):
                result = json.dumps({"error": "Could not determine genre from query."})
        elif any(keyword in query.lower() for keyword in ["price", "cheaper", "compare"]):
            result = self._analyze_prices(df)
        elif any(keyword in query.lower() for keyword in ["popular", "genre"]):
            result = self._analyze_popular_genres(df)
        else:
            result = self._analyze_popular_genres(df)
        
        self.last_result = result
        return result

    def _analyze_cheapest_by_genre(self, df: pd.DataFrame, genre: str) -> str:
        """Finds the cheapest books in a specific genre."""
        if 'genre' not in df.columns or 'price' not in df.columns:
            return json.dumps({"error": "Dataframe must contain 'genre' and 'price' columns."})

        # Handle both string and list of strings for genre
        df_exploded = df.explode('genre')
        genre_books = df_exploded[df_exploded['genre'].str.lower() == genre.lower()]

        if genre_books.empty:
            return json.dumps({"message": f"No books found for genre: {genre}"})

        cheapest_books = genre_books.sort_values(by='price', ascending=True).head(5)
        return cheapest_books.to_json(orient='records')

    def _analyze_prices(self, df: pd.DataFrame) -> str:
        """Analyzes the average price of books per store."""
        if 'price' not in df.columns or 'store' not in df.columns:
            return json.dumps({"error": "Dataframe must contain 'price' and 'store' columns for price analysis."})

        avg_prices = df.groupby('store')['price'].mean().reset_index()
        avg_prices = avg_prices.rename(columns={'price': 'average_price'})
        
        return avg_prices.to_json(orient='records')

    def _analyze_popular_genres(self, df: pd.DataFrame) -> str:
        """Analyzes the most popular genre per store."""
        if 'genre' not in df.columns or 'store' not in df.columns:
            return json.dumps({"error": "Dataframe must contain 'genre' and 'store' columns for genre analysis."})

        # Explode genre lists into separate rows if necessary
        if any(isinstance(g, list) for g in df['genre']):
            df = df.explode('genre')
        
        # Group by store and genre, then count occurrences
        genre_counts = df.groupby(['store', 'genre']).size().reset_index(name='count')

        # Find the most popular genre for each store
        most_popular = genre_counts.loc[genre_counts.groupby('store')['count'].idxmax()]

        return most_popular.to_json(orient='records')

class BookSearchTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = "Book Search Tool"
    description: str = "Searches for books in a vector database based on a user's query. It can handle natural language queries with filters."
    args_schema: Type[BaseModel] = BookSearchInput
    rag_system: BookstoreRAGSystem = None
    last_result: str = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        config = Config()
        self.rag_system = BookstoreRAGSystem(config)
        self.last_result = None

    def _run(self, query: str) -> str:
        """Use the RAG system to search for books."""
        # CrewAI's _run method is synchronous, so we run the async search method from our RAG system.
        results = asyncio.run(self.rag_system.search(query))
        json_results = json.dumps(results, indent=2)
        self.last_result = json_results
        return json_results
