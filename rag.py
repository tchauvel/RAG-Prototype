import os
import glob
import chromadb
from chromadb.utils import embedding_functions
import ollama

class SimpleRAG:
    """
    A simple RAG system.
    1. Ingest: Reads text files and stores them in a Vector Database (ChromaDB).
    2. Retrieve: Finds relevant text chunks for a question.
    3. Generate: Uses an LLM (Llama 3) to answer based on the chunks.
    """
    def __init__(self, collection_name="faq_collection", persist_directory="chroma_db", verbose=True):
        self.verbose = verbose
        if self.verbose: print("Initializing RAG system...")
        
        # 1. Setup Vector Database
        # We use a persistent client so data is saved to disk ('chroma_db' folder)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 2. Setup Embedding Function
        # This converts text into numbers (vectors) so we can compare meanings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 3. Get or Create Collection
        # A collection is like a table in a database
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        if self.verbose: print("RAG system initialized.")

    def ingest(self, directory_path):
        """
        Reads all .md/.txt files in the directory and saves them to the database.
        """
        # If we already have data, don't do it again (saves time)
        if self.collection.count() > 0:
            if self.verbose: print(f"Collection has {self.collection.count()} docs. Skipping ingest.")
            return

        if self.verbose: print(f"Ingesting data from {directory_path}...")
        
        # Find all files
        files = glob.glob(os.path.join(directory_path, "*.md")) + glob.glob(os.path.join(directory_path, "*.txt"))
        
        documents = []
        metadatas = []
        ids = []
        
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple Chunking: Split by double newlines (paragraphs)
            # This keeps related text together
            chunks = content.split('\n\n')
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Ignore very short/empty chunks
                    documents.append(chunk.strip())
                    # Metadata helps us cite the source later
                    metadatas.append({"source": os.path.basename(file_path)})
                    ids.append(f"{os.path.basename(file_path)}_{i}")

        if documents:
            # Save to ChromaDB (it handles the embedding automatically)
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            if self.verbose: print(f"Ingested {len(documents)} chunks.")

    def retrieve(self, query, n_results=4):
        """
        Finds the most relevant chunks for the query.
        Uses a 'Hybrid' approach: Vector Search + Keyword Matching.
        """
        # 1. Vector Search (Semantic Meaning)
        results = self.collection.query(query_texts=[query], n_results=n_results * 2) # Get extra candidates
        
        if not results['documents']:
            return []

        # Flatten results (Chroma returns a list of lists)
        candidates = zip(results['documents'][0], results['metadatas'][0])
        
        # 2. Keyword Boosting (Exact Matches)
        # If a chunk contains the exact words from the query, we boost its score.
        query_words = set(query.lower().split())
        scored_candidates = []
        
        for doc, meta in candidates:
            score = 0
            # Simple point system: +1 for each keyword found
            for word in query_words:
                if word in doc.lower():
                    score += 1
            scored_candidates.append((doc, meta, score))
            
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Return top N
        return [(item[0], item[1]) for item in scored_candidates[:n_results]]

    def generate(self, query, context_items):
        """
        Asks the LLM to answer the question using the retrieved context.
        """
        # 1. Prepare Context String
        context_text = ""
        for i, (text, meta) in enumerate(context_items):
            context_text += f"Source {i+1} ({meta['source']}):\n{text}\n\n"
        
        # 2. Construct Prompt
        # We tell the LLM exactly how to behave and how to cite sources
        prompt = f"""You are a helpful assistant. Answer the question using ONLY the context below.
If you don't know, say "I don't know".
Cite the source filename (e.g., faq_auth.md) for every claim.

Context:
{context_text}

Question: {query}

Answer:"""

        # 3. Call LLM (Ollama)
        try:
            response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Initialize RAG
    rag = SimpleRAG()
    rag.ingest("faq_data")
    
    print("\n--- RAG Prototype CLI ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("Enter your question: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            print("Retrieving context...")
            context = rag.retrieve(user_input, n_results=4)
            
            print(f"Found {len(context)} relevant chunks. Generating answer...\n")
            answer = rag.generate(user_input, context)
            
            print("Answer:")
            print(answer)
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
