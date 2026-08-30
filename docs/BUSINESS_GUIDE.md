# 📊 Business & Analytics Guide

This document defines the core business logic, use cases, and key performance indicators (KPIs) for the AI Legal Intelligence Platform (AILIP).

## 1. Core Use Cases (UCs)

The platform bridges the gap between complex legal jargons and everyday citizens/enterprises.

| Use Case ID | Description | Target User | Status |
|-------------|-------------|-------------|--------|
| **UC-01** | Search legal documents via natural language | General Public | ✅ Active |
| **UC-02** | Q&A with AI Assistant regarding specific legal issues | General Public | ✅ Active |
| **UC-03** | Upload and analyze contracts for risks (CoT) | Enterprise / Lawyers | ✅ Active |
| **UC-04** | Bookmark and manage legal document collections | Registered Users | ✅ Active |
| **UC-05** | View analytics dashboard (Trends, Clusters) | Admins / Researchers | ✅ Active |

## 2. Dataset Overview & Statistics

The platform runs on a robust, proprietary dataset curated specifically for this Scientific Research (NCKH) project.

- **Total Documents:** ~3,000 official Vietnamese legal documents (Laws, Decrees, Circulars).
- **Domain Coverage:** 6 primary fields (Labor Law, Civil Law, Criminal Law, Corporate Law, etc.).
- **Vector Scale:** Over 50,000 vector embeddings stored in PostgreSQL (`pgvector`), ensuring high granularity during semantic searches.

## 3. Key Business Metrics (KPIs)

- **Search Latency:** Target is `< 1s` for keyword search and `< 5s` for semantic search to ensure optimal User Experience (UX).
- **AI Accuracy:** Minimum threshold of 85% for Faithfulness (measured mathematically via RAGAs) to ensure legal safety.
- **Top Search Domains:** Analytics dashboard (using Recharts) tracks real-time trends to identify which legal topics are currently trending among users.

## 4. Advanced Data Mining

- **PageRank Algorithm:** Applied to the dataset to calculate the "influence" of each law. Laws heavily cited by other decrees rank higher in search results.
- **Louvain Clustering:** Used to detect community structures within the legal framework, automatically grouping related laws without manual tagging.

## 5. Data Privacy & Compliance

- **No Data Leakage:** User passwords are encrypted via `bcrypt`. 
- **LLM Privacy:** No personal user data is sent to the Gemini API; only the sanitized, public legal context is injected into the prompt.
