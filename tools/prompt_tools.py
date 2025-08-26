import json

# Normalized schema for the vector store
NORMALIZED_SCHEMA = {
    "fields": ["title", "author", "price", "genre", "publication_year", "rating", "reviews_count", "store"],
    "field_types": {
        "title": "string",
        "author": "string",
        "price": "float",
        "genre": "string or array of strings",
        "publication_year": "integer",
        "rating": "float",
        "reviews_count": "integer",
        "store": "string"
    },
    "filterable_fields": ["author", "price", "genre", "publication_year", "rating", "reviews_count", "store"]
}

def generate_filter_query_prompt(user_query: str) -> str:
    """
    Generates a detailed prompt for an LLM to convert a natural language user query
    into a Qdrant filter JSON object.

    This function constructs a prompt that includes:
    - The available data schemas for different bookstores.
    - Mappings between similar fields across different stores (e.g., 'author' vs. 'writer').
    - The user's natural language query.
    - Examples of the expected Qdrant filter JSON format.
    - A set of rules for the LLM to follow to ensure consistent and accurate filter generation.

    Args:
        user_query: The natural language query from the user.

    Returns:
        A formatted string that serves as a prompt for the LLM.
    """
    schema_info = json.dumps(NORMALIZED_SCHEMA, indent=2)
    
    prompt = f"""
You are an expert at converting natural language queries into Qdrant database filters.

Here is the normalized schema of the data in the vector store:
{schema_info}

USER QUERY: "{user_query}"

Based on the user's query and the schema, generate a Qdrant filter. Return ONLY the valid JSON.

FILTER FORMAT EXAMPLES:
1. Price filter: {{"must": [{{"key": "price", "range": {{"gte": 10, "lte": 20}}}}]}}
2. Author filter: {{"must": [{{"key": "author", "match": {{"value": "Stephen King"}}}}]}}
3. Genre filter: {{"must": [{{"key": "genre", "match": {{"value": "Science Fiction"}}}}]}}
4. Multiple filters: {{"must": [{{"key": "author", "match": {{"value": "Andy Weir"}}}}, {{"key": "price", "range": {{"lte": 20}}}}]}}

RULES:
1. ONLY use the fields available in the `filterable_fields` list from the schema.
2. Do NOT invent fields. Do NOT use fields like 'category'. The only field for book category is 'genre'.
3. For genre queries, create a filter for the 'genre' field.
4. For price comparisons (e.g., 'cheaper', 'expensive'), create appropriate ranges for the 'price' field.
5. For popularity queries (e.g., 'popular', 'highly-rated'), use 'rating' > 4.0 or 'reviews_count' > 500.

If no specific filters are needed for the query, return: {{"must": []}}
"""
    return prompt
