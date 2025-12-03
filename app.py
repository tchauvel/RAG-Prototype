from flask import Flask, render_template, request, jsonify
from rag import SimpleRAG
import os

app = Flask(__name__)

# --- Initialization ---
# We initialize the RAG system once when the app starts.
# It loads the database and prepares for queries.
rag = SimpleRAG()
rag.ingest("faq_data")

# --- Routes ---

@app.route('/')
def home():
    """Serves the chat interface (HTML)."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API Endpoint: Receives a question, finds the answer, and returns it.
    """
    # 1. Get the user's question
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # 2. Retrieve relevant information (Context)
        # We ask for the top 4 most relevant chunks
        context = rag.retrieve(query, n_results=4)
        
        # 3. Generate an answer using the LLM
        answer = rag.generate(query, context)
        
        # 4. Extract sources for display
        # We look at the metadata of the retrieved chunks
        sources = sorted(list(set(meta['source'] for _, meta in context)))
        
        # 5. Return the result as JSON
        return jsonify({
            'answer': answer,
            'sources': sources
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the server
    app.run(debug=True, port=8080)
