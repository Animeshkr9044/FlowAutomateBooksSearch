# FlowAutomateBooksSearch
This project is a RAG (Retrieval-Augmented Generation) system designed to search across two different bookstore inventories with varying data schemas.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- You need an OpenAI API key for the agent's query generation.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY='your_api_key_here'
    ```

3.  **Create and activate the virtual environment:**
    This project uses a Python 3.10 virtual environment.

    ```bash
    # Create the virtual environment
    python3.10 -m venv .venv

    # Activate the environment
    source .venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

The application is now split into two main parts: the data ingestion pipeline and the search application.

1.  **Generate Synthetic Data:**
    This script creates the necessary JSON files in the `data/` directory.
    ```bash
    python synthetic_data_generation.py
    ```

2.  **Run the Data Ingestion Pipeline:**
    This script sets up the Qdrant vector database and indexes the book data. Run this once to set up the database.
    ```bash
    python data_ingestion.py
    ```

3.  **Run the Search Application:**
    This command starts the RAG system and runs the test queries. It will check if the database is ready before starting.
    ```bash
    python main.py
    ```
