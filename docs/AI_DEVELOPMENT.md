# 🤖 AI/ML Development Guide

This guide details the technical implementation of the AI features within the AILIP ecosystem, focusing on the Retrieval-Augmented Generation (RAG) pipeline and mathematical evaluation.

## 1. RAG Pipeline Architecture

The platform uses an advanced Hybrid-RAG pipeline to eliminate hallucinations (ảo giác) and guarantee factual accuracy based strictly on Vietnamese Law.

```text
User Query 
  ↓
Retriever (BM25 Keyword + pgvector HNSW Semantic)
  ↓
Reciprocal Rank Fusion (RRF) Re-ranking
  ↓
Context Formatting & Prompt Injection
  ↓
LLM (Gemini 2.5 Flash) via SSE Stream
  ↓
Citation Extraction & Grounding
  ↓
Client UI
```

## 2. Setting Up Local AI Models (Embeddings)

To maintain data privacy and speed, the platform uses a local bi-encoder for semantic vector generation before indexing into `pgvector`.

1. **Embedding Model Used:** `bkai-foundation-models/vietnamese-bi-encoder`
2. **Vector Dimension:** 768
3. **Run ETL Pipeline:**
   ```bash
   python backend/scripts/etl/embedder.py
   ```

## 3. Prompt Engineering & Anti-Hallucination

- **Strict System Prompt:** The LLM is instructed via `backend/app/services/rag_service.py` with a strict directive: *"Answer ONLY using the provided context."*
- **Temperature:** Set to `0.3` (Low creativity) to prevent the LLM from hallucinating legal facts.
- **Chain-of-Thought (CoT):** Enabled specifically for the Contract Analysis module to force the LLM to analyze risks step-by-step before outputting the final JSON response.

## 4. Evaluation Metrics (RAGAs)

To empirically prove the quality of the AI system, we run automated benchmarking scripts (`backend/scripts/benchmark_rag.py`) to calculate mathematical scores:

- **MRR@5 (Mean Reciprocal Rank):** Evaluates how high the correct legal document is ranked in the top 5 results.
- **Hit@5:** Percentage of queries where the correct document appears anywhere in the top 5.
- **Faithfulness (RAGAs):** Measures if the generated answer is strictly grounded in the retrieved context (0 hallucination).
- **Answer Relevancy (RAGAs):** Measures the semantic similarity between the user's question and the generated answer.
