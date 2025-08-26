# Problem Description

This document outlines the core problem this project is designed to solve: enabling natural language queries across two distinct bookstore datasets with different data schemas.

## Quick Links

- [**Architecture Documentation**](https://github.com/Animeshkr9044/FlowAutomateBooksSearch/blob/main/Documentation/ARCHITECTURE.md)
- [**Architecture Diagram**](https://github.com/Animeshkr9044/FlowAutomateBooksSearch/blob/main/Documentation/Mermaid%20Chart%20-%20Create%20complex%2C%20visual%20diagrams%20with%20text.%20A%20smarter%20way%20of%20creating%20diagrams.-2025-08-26-143337.svg)
- [**View Sample Output**](https://docs.google.com/spreadsheets/d/1wkfJ_YKZfi1W-Y9snWLxRmZG1CqQGtS32tNfjXDjNJE/edit?usp=sharing)

## Problem Statement

The primary goal is to build a unified system that can understand and answer natural language questions from a user, even when the underlying data comes from multiple sources with inconsistent structures. The system must be able to handle queries such as:

- **Semantic Search**: Find the most relevant book based on a descriptive user query (e.g., "a book about a stranded astronaut").
- **Data Analysis**: Identify trends and insights from the data (e.g., "what is the most popular genre per store?").
- **Comparative Analysis**: Compare data across the two stores (e.g., "which bookstore is cheaper for science fiction?").

## Simulating the Problem

To replicate a real-world scenario where a business might integrate data from different partners or legacy systems, we have created two synthetic bookstore datasets:

- `data/store_a_books.json`
- `data/store_b_books.json`

These datasets contain overlapping book titles but use intentionally different field names and data structures, forcing the system to resolve these inconsistencies to answer queries accurately.

## Schema Differences

The core challenge lies in mapping the different schemas. The system needs to understand that `title` in Store A is equivalent to `book_name` in Store B, and so on.

Here is a detailed comparison of the schemas:

| Feature           | Store A (`store_a_books.json`) | Store B (`store_b_books.json`) | Notes                                      |
| ----------------- | ------------------------------ | ------------------------------ | ------------------------------------------ |
| **Book Title**    | `title` (string)               | `book_name` (string)           | Different field names for the same concept.|
| **Author**        | `author` (string)              | `writer` (string)              | Different field names for the same concept.|
| **Genre/Category**| `genre` (string)               | `category` (array of strings)  | Different data types and naming.           |
| **Price**         | `price` (float)                | `cost` (float)                 | Different field names for the same concept.|
| **Unique ID**     | `book_id` (string)             | `product_id` (string)          | Different field names for the same concept.|
| **Description**   | `description` (string)         | `summary` (string)             | Different field names for the same concept.|
| **User Feedback** | `rating` (float)               | `reviews_count` (integer)      | Represents different metrics for feedback. |
| **Stock Level**   | _Not Available_                | `stock` (integer)              | Store B has stock info; Store A does not.  |
| **Publisher**     | _Not Available_                | `publisher` (string)           | Store B has publisher info; Store A does not.|

By addressing these differences, the AI agent can perform complex queries that span both datasets, providing a seamless experience for the user.

## The Solution: Schema Normalization

The problem of inconsistent schemas is solved during the data ingestion phase, as detailed in the `data_ingestion.py` script. The solution involves creating a unified, clean schema and mapping the fields from both data sources to this common structure before indexing them into the vector database.

This process involves several key steps:

1.  **Unified Schema Definition**: A common schema is defined within the `prepare_documents` function. This ensures that every book record, regardless of its origin, conforms to a single, predictable structure. All downstream components, like the AI agent and its tools, interact only with this clean schema.

2.  **Field Mapping**: The script explicitly maps the different field names from each store to the unified schema. For example:
    *   Store A's `title` and Store B's `book_name` are both mapped to the `title` field.
    *   Store A's `author` and Store B's `writer` are both mapped to the `author` field.
    *   Store A's `price` and Store B's `cost` are both mapped to the `price` field.

3.  **Data Transformation**: The script handles differences in data types and structures. For instance, the `genre` in Store A is a single string, while `category` in Store B is an array. The ingestion script normalizes this so that the final `genre` field is consistent for all records.

4.  **Centralized Indexing**: Once the data is normalized, it is indexed into the Qdrant vector database. This creates a single, queryable source of truth for the entire application.

By implementing this normalization layer, the complexity of the disparate data sources is abstracted away. The AI agent can then perform its tasks on a clean, reliable, and unified dataset, allowing it to answer complex queries without needing to handle the schema differences itself.

## Solution: Intelligent Query Processing with an AI Agent

To address the challenge of understanding and processing complex, conversational user queries, we have implemented an intelligent system powered by a CrewAI agent. This system follows a sophisticated workflow to deliver accurate and context-aware responses:

1.  **Intent Recognition**: The agent first analyzes the user's natural language query to understand its intent. It determines whether the user is asking a question that requires a direct book search or one that needs data analysis (e.g., "What is the average price of a fantasy book?").

2.  **Tool Selection**: Based on the recognized intent, the agent selects the appropriate tool for the job. It might choose the `BookSearchTool` for finding specific books or the `BookAnalyticsTool` for analytical questions.

3.  **Tool Execution**: The selected tool then processes the query. For a search, this involves generating metadata filters from the query and using them to perform a filtered semantic search in the Qdrant vector database. For analytics, it might involve querying the entire dataset to compute a result.

4.  **Response Synthesis**: The agent receives the structured data or analysis from the tool. It then combines this information with the original user query to generate a final, human-readable response. This ensures the user receives not just raw data, but a helpful and complete answer.

This agent-based architecture allows the system to deconstruct complex user intent, execute the right actions, and synthesize the results into a coherent and useful response.

## Core Technologies

The implementation of this solution relies on a set of powerful, open-source technologies:

*   **Agent Framework**: `CrewAI` is used to orchestrate the AI agent, its tools, and the overall task execution flow.
*   **Vector Database**: `Qdrant` serves as the vector database, chosen for its efficiency and advanced filtering capabilities.
*   **Embedding Model**: `Qwen/Qwen3-Embedding-0.6B` is used to convert book descriptions and user queries into high-dimensional vectors for semantic search.

## Final Output: Batch Query Results

To evaluate the agent's performance across a range of queries, the system generates a `batch_query_results.csv` file. This file serves as a log of the agent's interactions and contains the following columns:

*   **query**: The original natural language query sent to the agent.
*   **response**: The final, human-readable answer generated by the agent after processing the query and its tool outputs.

### Example

Below is a sample from the `batch_query_results.csv` file, which demonstrates the agent's ability to provide conversational and accurate responses to various queries. You can view the complete output file [here](https://docs.google.com/spreadsheets/d/1wkfJ_YKZfi1W-Y9snWLxRmZG1CqQGtS32tNfjXDjNJE/edit?usp=sharing).

For a deeper dive into how the system is designed, please refer to the [**Architecture Documentation**](https://github.com/Animeshkr9044/FlowAutomateBooksSearch/blob/main/Documentation/ARCHITECTURE.md) and view the [**Architecture Diagram**](https://github.com/Animeshkr9044/FlowAutomateBooksSearch/blob/main/Documentation/Mermaid%20Chart%20-%20Create%20complex%2C%20visual%20diagrams%20with%20text.%20A%20smarter%20way%20of%20creating%20diagrams.-2025-08-26-143337.svg).

```csv
query,response
"find me some books by Stephen King","I found a few great books by Stephen King for you! Here is what I discovered: 'The Shining' which is a classic horror novel, and 'It', another terrifying read. I hope one of these is what you're looking for!"
"what is the most popular genre in each bookstore?","That's an interesting question! Based on the data, it looks like Store A's most popular genre is Science Fiction, while Store B has a lot of Fantasy titles. It seems both stores have great options for speculative fiction fans!"
```



