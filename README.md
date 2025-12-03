# Self-Contained RAG Prototype

A local Retrieval-Augmented Generation (RAG) system built with Python, ChromaDB, and Ollama. This prototype ingests FAQ data, retrieves relevant context, and answers user questions via a CLI.

## Prerequisites

- **Python 3.9+**
- **Ollama**: Must be installed and running locally.
  - Install from [ollama.com](https://ollama.com).
  - Pull the `llama3` model: `ollama pull llama3`.

## Setup

1.  **Clone/Navigate to the directory**:
    ```bash
    cd rag_prototype
    ```

2.  **Create and Activate Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r rag_prototype/requirements.txt
    ```

4.  **Prepare Data**:
    - Ensure `faq_data/` contains `.txt` files with your knowledge base.
    - A sample `photoroom_faq.txt` is provided.

## Usage

### CLI Mode

Run the application in the terminal:

```bash
python rag.py
```

### Web Interface

Run the Flask web server:

```bash
python app.py
```

Open your browser and navigate to `http://localhost:8080`.

The system will:
1.  Ingest and chunk text files from `faq_data/`.
2.  Store embeddings in an in-memory ChromaDB collection.
3.  Start the selected interface.

**Example Interaction**:

```text
Enter your question: How is the API priced?
Retrieving context...
Found 3 relevant chunks. Generating answer...

Answer:
The Photoroom API uses a credit-based system where each successful call consumes one credit. Monthly plans start at $50 for 1,000 credits.
```

Type `exit` to quit.

## Design Decisions

### Vector Database: ChromaDB
We chose **ChromaDB** for its simplicity and developer-friendly API.
-   **Simplicity**: It runs in-memory (ephemeral mode) by default, requiring no external server setup (like Docker containers for Postgres/pgvector or Weaviate).
-   **Built-in Embeddings**: It handles embedding generation automatically using `sentence-transformers` (defaulting to `all-MiniLM-L6-v2`), reducing boilerplate code.

### LLM: Ollama
We chose **Ollama** to run the LLM locally.
-   **Privacy**: Data never leaves the local machine.
-   **Cost**: No API fees (unlike OpenAI/Anthropic).
-   **Ease of Use**: Provides a simple REST API and Python library to interact with powerful open-source models like Llama 3.

## Scaling for Enterprise

To scale this prototype into an Enterprise-grade search engine (like Glean), we would need to address several key areas:

### 1. Permissions & ACLs (Access Control Lists)
**Challenge**: In an enterprise, not everyone should see every document (e.g., HR salaries vs. Engineering docs).
**Solution**:
-   **Index-time**: Attach Access Control Lists (ACLs) to every document chunk in the vector DB (e.g., `allowed_groups: ['engineering', 'admin']`).
-   **Query-time**: Filter search results based on the authenticated user's identity. Chroma supports `where` filters that can be used to enforce these permissions before the retrieval step.

### 2. Hybrid Search (Vector + Keyword)
**Challenge**: Vector search is great for semantic meaning but can miss exact keyword matches (e.g., specific error codes like "ERR-505" or project codenames).
**Solution**:
-   Implement **Hybrid Search** by combining dense vector retrieval with sparse keyword retrieval (BM25).
-   Use a re-ranking step (Cross-Encoder) to merge and score the results from both streams to provide the most accurate context.

### 3. Data Freshness & Event-Driven Indexing
**Challenge**: Re-ingesting all data on every startup (as done in this prototype) is impossible at scale.
**Solution**:
-   **Event-Driven Architecture**: Listen to webhooks or change streams from data sources (Google Drive, Slack, Confluence).
-   **Incremental Indexing**: Only process created, updated, or deleted documents.
-   **Queue System**: Use a message queue (Kafka/Celery) to decouple ingestion from indexing, ensuring the system remains responsive under heavy load.
