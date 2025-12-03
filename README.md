# Self-Contained RAG Prototype

A local Retrieval-Augmented Generation (RAG) system built with Python, ChromaDB, and Ollama. This prototype ingests FAQ data, retrieves relevant context, and answers user questions via a CLI or Web Interface.

## 1. Prerequisites & Setup

Before writing code, ensure you have the necessary tools:

-   **Python 3.9+**: The programming language used.
-   **Ollama**: A local tool to run LLMs.
    -   Install from [ollama.com](https://ollama.com).
    -   Run `ollama pull llama3` to download the model.

### Project Structure

Create a folder for your project and set up the following structure:

```text
rag_project/
├── app.py                 # Web server (Flask)
├── rag.py                 # Core RAG logic
├── requirements.txt       # Dependencies
├── faq_data/              # Folder for your text data
│   └── your_data.txt
├── templates/
│   └── index.html         # Frontend HTML
└── static/
    ├── style.css          # Styles
    └── script.js          # Frontend logic
```

### Dependencies (`requirements.txt`)

Create a `requirements.txt` file with these libraries:

```text
flask
chromadb
ollama
sentence-transformers
```

Install them:
```bash
pip install -r requirements.txt
```

## 2. Core RAG Logic (`rag.py`)

This is the "brain" of the application. It handles three main tasks:

1.  **Ingest**: Reading text files and saving them as vectors in a database.
2.  **Retrieve**: Finding relevant text chunks for a user's question.
3.  **Generate**: Sending the question + context to the LLM for an answer.

**Key Components:**

-   **ChromaDB**: A local vector database to store text embeddings.
-   **Sentence Transformers**: Converts text into numbers (vectors).
-   **Ollama**: The interface to the Llama 3 model.

(See `rag.py` in the codebase for the full implementation of the `SimpleRAG` class).

## 3. Web Server (`app.py`)

We use Flask to create a simple web server.

-   **Initialization**: When the app starts, it initializes the `SimpleRAG` class and ingests data from `faq_data/`.
-   **Routes**:
    -   `/`: Serves the `index.html` page.
    -   `/api/chat`: A POST endpoint that takes a JSON query, calls `rag.retrieve()` and `rag.generate()`, and returns the answer.

## 4. Frontend (`templates/index.html`)

The frontend is a simple chat interface.

-   **HTML**: Structure for the chat window and input box.
-   **JavaScript** (in `static/script.js`):
    -   Listens for the "Send" button click.
    -   Sends the user's message to `/api/chat`.
    -   Displays the loading state and then the bot's response.

## 5. Data Preparation

Place your knowledge base files (text or markdown) in the `faq_data/` folder. The system is designed to read these files, chunk them into paragraphs, and index them.

## 6. Running the Application

1.  **Start Ollama**: Ensure `ollama serve` is running in the background (or the desktop app is open).
2.  **Run the App**:
    ```bash
    python app.py
    ```
3.  **Access**: Open `http://localhost:8080` in your browser.

## Summary of Flow

1.  User types a question in the browser.
2.  Browser sends it to `app.py`.
3.  `app.py` asks `rag.py` to find relevant info.
4.  `rag.py` queries ChromaDB for similar text chunks.
5.  `rag.py` sends the Question + Chunks to Ollama.
6.  Ollama generates an answer.
7.  `app.py` sends the answer back to the Browser.
