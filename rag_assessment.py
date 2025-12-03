import json
import sys
from rag import SimpleRAG

def main():
    """
    Runs the RAG assessment:
    1. Ingests data.
    2. Answers a question.
    3. Prints result in JSON format.
    """
    # 1. Initialize (Silence output for clean JSON)
    rag = SimpleRAG(verbose=False)
    rag.ingest("faq_data")

    # 2. Get Question
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "How do I reset my password?"

    # 3. Retrieve Context
    context = rag.retrieve(query, n_results=4)

    # 4. Generate Answer
    answer = rag.generate(query, context)

    # 5. Format Output
    sources = sorted(list(set(meta['source'] for _, meta in context)))
    
    output = {
        "answer": answer,
        "sources": sources
    }
    
    # Print JSON
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
