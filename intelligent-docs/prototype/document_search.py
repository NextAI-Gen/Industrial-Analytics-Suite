"""
My RAG System - Learning RAG from Scratch
Author: [Your Name]
Date: Sep 29, 2025

I'm trying to build a document query system. This is my first time
working with embeddings and vector search, so I'm starting simple.

The idea is:
1. Take some technical documents 
2. Split them into chunks
3. Create embeddings (vectors) for each chunk
4. When someone asks a question, find similar chunks
5. Use those chunks to answer the question
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict

# I'll try to use sentence-transformers for embeddings
# This seemed like a good choice from my research
try:
    from sentence_transformers import SentenceTransformer
    import faiss  # For vector search
    print("Great! All libraries loaded successfully")
except ImportError as e:
    print(f"Missing library: {e}")
    print("You might need: pip install sentence-transformers faiss-cpu")
    exit()

class MySimpleRAG:
    """
    My attempt at building a RAG system
    
    I'm keeping this simple to start - just basic functionality
    """
    
    def __init__(self):
        print("Initializing my RAG system...")
        
        # Load the embedding model - I chose this one after some research
        # It's small but supposedly good for general text
        print("Loading embedding model (this might take a minute)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # This model outputs 384-dimensional vectors
        
        # Set up vector search - using FAISS because it's popular
        # IndexFlatIP means "flat index with inner product" - simple but works
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Storage for the actual text chunks and their metadata
        self.chunks = []
        self.chunk_metadata = []
        
        print("RAG system initialized!")
    
    def add_document(self, text, doc_name):
        """
        Add a document to my knowledge base
        
        My approach:
        1. Split the text into chunks (paragraphs for now)
        2. Create embeddings for each chunk
        3. Add to the vector index
        """
        print(f"Processing document: {doc_name}")
        
        # Simple chunking: split by double newlines (paragraphs)
        # This is pretty basic but should work for well-formatted docs
        paragraphs = text.split('\n\n')
        document_chunks = [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        print(f"  Found {len(document_chunks)} chunks")
        
        if not document_chunks:
            print("  No chunks found, skipping this document")
            return
        
        # Create embeddings for all chunks at once (more efficient)
        chunk_embeddings = self.embedder.encode(document_chunks)
        
        # Normalize embeddings - this helps with cosine similarity
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)
        
        # Add to FAISS index
        self.index.add(chunk_embeddings.astype('float32'))
        
        # Store the chunks and metadata
        for i, chunk in enumerate(document_chunks):
            self.chunks.append(chunk)
            self.chunk_metadata.append({
                'doc_name': doc_name,
                'chunk_id': len(self.chunks) - 1,
                'chunk_in_doc': i
            })
        
        print(f"  Added {len(document_chunks)} chunks to knowledge base")
    
    def search(self, query, num_results=3):
        """
        Search for relevant chunks given a query
        
        Steps:
        1. Convert query to embedding
        2. Search for similar chunks using FAISS
        3. Return the most similar ones
        """
        if len(self.chunks) == 0:
            print("No documents in knowledge base yet!")
            return []
        
        # Convert query to embedding
        query_embedding = self.embedder.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search using FAISS
        similarities, indices = self.index.search(query_embedding.astype('float32'), num_results)
        
        # Package results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.chunks):  # Valid result
                results.append({
                    'rank': i + 1,
                    'similarity': float(similarity),
                    'text': self.chunks[idx],
                    'metadata': self.chunk_metadata[idx]
                })
        
        return results
    
    def answer_question(self, question):
        """
        Try to answer a question using the knowledge base
        
        My simple approach:
        1. Search for relevant chunks
        2. If similarity is good enough, use the text to answer
        3. Always show which documents the answer came from
        """
        print(f"\nQuestion: {question}")
        
        # Search for relevant information
        results = self.search(question, num_results=3)
        
        if not results:
            return {
                'answer': "I don't have any documents to search through yet.",
                'confidence': 0.0,
                'sources': []
            }
        
        # Check if the best result is good enough
        best_similarity = results[0]['similarity']
        
        # My threshold for "good enough" - this is a guess, might need tuning
        if best_similarity < 0.3:
            return {
                'answer': "I couldn't find relevant information in the available documents.",
                'confidence': best_similarity,
                'sources': [r['metadata']['doc_name'] for r in results]
            }
        
        # Combine the top results to form an answer
        context_pieces = []
        source_docs = set()
        
        for result in results:
            context_pieces.append(result['text'])
            source_docs.add(result['metadata']['doc_name'])
        
        # For now, just concatenate the context - not very sophisticated
        combined_context = '\n\n'.join(context_pieces[:2])  # Top 2 results
        
        answer = f"Based on the available documentation:\n\n{combined_context}"
        
        return {
            'answer': answer,
            'confidence': best_similarity,
            'sources': list(source_docs)
        }

def create_sample_documents():
    """
    Create some sample technical documents for testing
    
    I'll make up some realistic-sounding industrial docs
    """
    docs = {}
    
    docs['Cyclone Operations Manual'] = """
CYCLONE SEPARATOR OPERATIONS

NORMAL OPERATING CONDITIONS
The cyclone separator should operate within the following parameters:
- Inlet gas temperature: 850-950°C
- Material outlet temperature: maximum 800°C
- Draft pressure: -150 to -200 mmH2O

STARTUP PROCEDURE
1. Verify all instrumentation is calibrated
2. Start combustion air fans
3. Gradually increase fuel flow
4. Monitor temperature rise carefully
5. Normal operating temperature should be reached within 2 hours

TROUBLESHOOTING
If inlet temperature drops suddenly:
- Check fuel supply system
- Verify combustion air flow
- Inspect burner condition

If draft pressure increases:
- Check for blockages in cyclone
- Inspect downstream equipment
- Verify fan operation
    """
    
    docs['Maintenance Guide'] = """
PREVENTIVE MAINTENANCE SCHEDULE

DAILY CHECKS
- Record temperature readings from all sensors
- Check pressure readings
- Visual inspection of equipment
- Verify alarm systems are operational

WEEKLY MAINTENANCE
- Calibrate temperature instruments
- Inspect refractory lining condition
- Check for unusual vibrations or noises
- Review alarm and trend data

MONTHLY MAINTENANCE
- Detailed internal inspection
- Analysis of performance trends
- Spare parts inventory check
- Update maintenance records

COMMON PROBLEMS
Temperature instability usually indicates fuel system issues.
Pressure variations often point to blockages or structural problems.
Always investigate gradual changes in performance - they often signal developing issues.
    """
    
    docs['Safety Procedures'] = """
SAFETY OPERATING PROCEDURES

PERSONAL PROTECTIVE EQUIPMENT
All personnel must wear:
- Heat resistant clothing
- Safety glasses
- Hard hat
- Steel-toed safety boots
- Hearing protection in high noise areas

EMERGENCY PROCEDURES
In case of equipment malfunction:
1. Activate emergency shutdown
2. Isolate fuel supply
3. Notify control room immediately
4. Evacuate area if necessary
5. Do not attempt repairs without proper authorization

TEMPERATURE SAFETY
- Inlet gas temperature alarm at 1000°C
- Material temperature warning at 850°C
- Emergency shutdown at 1100°C inlet temperature

DRAFT PRESSURE MONITORING
Normal operation: -150 to -200 mmH2O
Warning level: -250 mmH2O
Emergency shutdown: -300 mmH2O
    """
    
    return docs

def test_my_rag():
    """Test my RAG system with some sample queries"""
    print("=== Testing My RAG System ===")
    
    # Initialize the system
    rag = MySimpleRAG()
    
    # Add sample documents
    print("\nAdding sample documents...")
    docs = create_sample_documents()
    
    for doc_name, content in docs.items():
        rag.add_document(content, doc_name)
    
    print(f"\nKnowledge base now contains {len(rag.chunks)} chunks from {len(docs)} documents")
    
    # Test with some questions
    test_questions = [
        "What is the normal operating temperature?",
        "What should I do if the temperature drops suddenly?",
        "How often should I do maintenance?",
        "What safety equipment do I need?",
        "What causes pressure variations?"
    ]
    
    print("\n" + "="*60)
    print("TESTING QUESTIONS")
    print("="*60)
    
    for question in test_questions:
        result = rag.answer_question(question)
        
        print(f"\nQ: {question}")
        print(f"A: {result['answer'][:200]}..." if len(result['answer']) > 200 else f"A: {result['answer']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Sources: {', '.join(result['sources'])}")
        print("-" * 40)

if __name__ == "__main__":
    print("My RAG System - First Implementation")
    print("This is my attempt to build a document query system from scratch")
    print()
    
    test_my_rag()
    
    print("\n=== Lessons Learned ===")
    print("1. Chunking by paragraphs works okay but could be better")
    print("2. Similarity threshold of 0.3 seems reasonable for these docs")
    print("3. The system finds relevant info but answer quality could improve")
    print("4. Next steps: better chunking, maybe try different embedding models")
    print()
    print("Overall: It works! Not perfect, but it's a solid start.")