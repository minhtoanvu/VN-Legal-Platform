# 🏗️ Deployment & Infrastructure Guide

This guide is intended for DevOps Engineers and Solution Architects responsible for deploying, monitoring, and scaling the AI Legal Intelligence Platform (AILIP) in a production environment.

## 1. Production Deployment Checklist

Before taking the application live, ensure the following checklist is completed:

- [ ] **SSL/TLS Certificates:** Ensure HTTPS is enforced via an Nginx reverse proxy or Cloud Load Balancer.
- [ ] **Database Backups:** Configure daily snapshots for the PostgreSQL database.
- [ ] **Environment Secrets:** Ensure `.env` files (including `GEMINI_API_KEY` and `SECRET_KEY`) are securely injected via CI/CD secrets (e.g., GitHub Secrets) and never committed to the repo.
- [ ] **Rate Limiting:** Protect the FastAPI endpoints using `SlowAPI` or Cloudflare to mitigate DDoS and brute-force login attacks.

## 2. CI/CD Pipeline (GitHub Actions)

The platform is equipped with fully automated continuous integration pipelines (`.github/workflows/`):

- **Backend CI:** Triggers on Push/PR to `main`. Runs `pytest` in a fresh Python environment.
- **Frontend CI:** Triggers on Push/PR to `main`. Runs ESLint and Vite Build checks.

## 3. Scaling Strategy & Bottleneck Mitigation

### Current Known Bottleneck
During load testing (100+ concurrent users), the `bcrypt` password hashing mechanism causes CPU spikes, blocking the asynchronous event loop in FastAPI.

### Proposed Solutions
1. **Short-term:** Offload the `bcrypt.hashpw` function to a `ThreadPoolExecutor` to prevent blocking the main asyncio loop.
2. **Mid-term:** Introduce `Redis` to cache frequent read-heavy requests (e.g., fetching standard legal documents) to relieve Database I/O.
3. **Long-term:** Deploy the FastAPI backend across multiple containers using Kubernetes (K8s) or Docker Swarm, and implement Read-Replicas for PostgreSQL.

## 4. Resource Requirements

| Component | Minimum Spec | Recommended Spec |
|-----------|--------------|------------------|
| **PostgreSQL (pgvector)** | 2GB RAM, 1 CPU | 8GB RAM, 4 CPUs (SSD required) |
| **FastAPI Backend** | 1GB RAM, 1 CPU | 4GB RAM, 2 Replicas |
| **React Frontend** | Static Hosting | Vercel / Netlify CDN |

## 5. Resilience Pattern (Circuit Breaker)

To protect the system from third-party API outages (e.g., Google Gemini downtime), a **Circuit Breaker** state machine is implemented. 
If the LLM API fails consecutively, the circuit opens, instantly returning a fallback error to the user rather than holding the connection open and exhausting server resources.
