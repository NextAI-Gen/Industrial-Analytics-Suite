# Task 2: RAG + LLM System Design

**Author:** Ankit Choudhary  
**Assignment:** Exactspace Technologies Data Science Role  
**Date:** September 30, 2025

## System Architecture Overview

The proposed RAG system is designed to handle 50+ technical PDFs with natural language querying capabilities, emphasizing reliability, scalability, and robustness against common LLM failure modes.

### Core Components

1. **Document Ingestion Pipeline**
   - PDF processing with PyPDF2/pdfplumber
   - Text extraction with OCR fallback for scanned documents
   - Metadata extraction (title, sections, page numbers)

2. **Chunking Strategy**
   - **Approach:** Semantic chunking with paragraph boundaries
   - **Chunk Size:** 512 tokens with 64-token overlap
   - **Rationale:** Balances context preservation with retrieval precision
   - **Enhancement:** Section-aware chunking for technical manuals

3. **Embeddings & Indexing**
   - **Model:** `sentence-transformers/all-MiniLM-L6-v2`
   - **Vector Database:** FAISS (local) → Pinecone/Weaviate (production)
   - **Dimension:** 384-dimensional embeddings
   - **Indexing:** IVF-Flat with 100 centroids for efficient search

4. **Retrieval Layer**
   - **Primary:** Dense vector search (cosine similarity)
   - **Enhancement:** Hybrid approach with BM25 for keyword matching
   - **Reranking:** Cross-encoder reranker for relevance refinement
   - **Top-K:** Retrieve 5 chunks, rerank to top 3

5. **LLM Layer**
   - **Model:** Llama-2-7B-Chat (quantized for efficiency)
   - **Fallback:** Flan-T5-Large for lighter deployment
   - **Context Window:** 4096 tokens maximum
   - **Temperature:** 0.1 for factual responses

6. **Guardrails & Safety**
   - **Citation Enforcement:** Source attribution mandatory
   - **Confidence Scoring:** Retrieval similarity thresholds
   - **Fallback Responses:** Graceful handling of low-confidence queries
   - **Content Filtering:** Block inappropriate or unsafe queries

## Design Trade-offs

### Chunking Strategy
- **Decision:** 512 tokens with 64-token overlap
- **Trade-off:** Larger chunks preserve context but may dilute relevance
- **Alternative Considered:** Sentence-based chunking (rejected due to technical content fragmentation)

### Embedding Model Selection
- **Decision:** all-MiniLM-L6-v2
- **Rationale:** Best balance of performance, speed, and memory usage
- **Trade-off:** Smaller model may miss domain-specific nuances
- **Future Enhancement:** Fine-tune on technical documentation corpus

### Vector Database Choice
- **Local Development:** FAISS (simplicity, no external dependencies)
- **Production:** Weaviate (better metadata filtering, hybrid search)
- **Trade-off:** FAISS lacks advanced filtering but offers better performance

## Retrieval Strategy Details

### Multi-Stage Retrieval
1. **Stage 1:** Dense vector search (top-20 candidates)
2. **Stage 2:** BM25 keyword matching (top-20 candidates)
3. **Stage 3:** Fusion ranking of combined results
4. **Stage 4:** Cross-encoder reranking (final top-5)

### Query Enhancement
- **Query Expansion:** Add technical synonyms for domain terms
- **Intent Classification:** Distinguish between factual vs. procedural queries
- **Context Preservation:** Maintain conversation history for follow-up questions

## Guardrails & Failure Modes

### 1. No Relevant Answers
- **Detection:** Similarity score < 0.3 threshold
- **Response:** "I couldn't find relevant information in the available documentation. Please try rephrasing your question or contact technical support."
- **Logging:** Track low-confidence queries for system improvement

### 2. Hallucination Prevention
- **Enforcement:** All responses must include source citations
- **Validation:** Cross-reference generated content with retrieved chunks
- **Template:** "Based on [Document Name, Page X]: [Answer with source quotes]"

### 3. Sensitive Query Handling
- **Filter Keywords:** Safety-critical operations, regulatory compliance
- **Response:** "This query requires direct consultation with technical experts. Please contact [support contact]."
- **Escalation:** Log sensitive queries for human review

### 4. Context Window Overflow
- **Detection:** Token count exceeding model limits
- **Mitigation:** Chunk summarization or priority-based selection
- **Graceful Degradation:** Reduce retrieved context while maintaining quality

## Monitoring & Evaluation Metrics

### Retrieval Quality
- **Precision@K:** Percentage of relevant documents in top-K results
- **Recall@K:** Coverage of relevant information
- **MRR (Mean Reciprocal Rank):** Ranking quality assessment
- **Target:** Precision@3 > 0.85, Recall@5 > 0.90

### Response Quality
- **Faithfulness Score:** Generated content alignment with sources
- **Citation Accuracy:** Percentage of properly attributed statements
- **User Satisfaction:** Thumbs up/down feedback collection

### System Performance
- **Response Time:** < 3 seconds for 95th percentile
- **Throughput:** > 100 concurrent queries
- **Availability:** 99.5% uptime target

## Scalability Considerations

### 10x Document Increase (500+ PDFs)
- **Vector Storage:** Migrate to distributed vector database (Pinecone/Weaviate)
- **Indexing Strategy:** Hierarchical clustering with document-level metadata
- **Preprocessing:** Batch processing with parallel document ingestion
- **Estimated Cost:** $200-400/month for managed vector DB

### 100+ Concurrent Users
- **Load Balancing:** Multiple LLM inference servers behind load balancer
- **Caching:** Redis cache for common queries (30% hit rate expected)
- **Rate Limiting:** 10 queries/minute per user to prevent abuse
- **Auto-scaling:** Kubernetes deployment with HPA

### Cost-Efficient Deployment
- **Primary Strategy:** Serverless functions (AWS Lambda/Azure Functions)
- **LLM Hosting:** Quantized models on GPU instances with auto-scaling
- **Vector Search:** Managed service for consistency and reliability
- **Estimated Monthly Cost:** $800-1200 for 100 concurrent users

## Implementation Phases

### Phase 1: MVP (Current Prototype)
- Local FAISS index with basic retrieval
- Simple chunking and embedding
- Flan-T5 for answer generation
- Basic citation enforcement

### Phase 2: Production Beta
- Hybrid search with reranking
- Improved chunking strategy
- Better LLM integration (Llama-2)
- Comprehensive guardrails

### Phase 3: Enterprise Deployment
- Distributed architecture
- Advanced monitoring
- User management and analytics
- Integration with existing systems

## Risk Mitigation

### Technical Risks
- **Model Degradation:** Regular evaluation with test queries
- **Index Corruption:** Automated backup and recovery procedures
- **Dependency Updates:** Controlled update cycle with testing

### Operational Risks
- **Data Privacy:** Local deployment option for sensitive documents
- **Compliance:** Audit logging for regulatory requirements
- **Disaster Recovery:** Multi-region deployment for critical applications

---

*System design completed: September 30, 2025*  
*Architecture optimized for reliability, scalability, and cost-effectiveness*