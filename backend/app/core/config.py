from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/legal_db"

    # JWT
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # LLM
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Embedding
    embedding_model: str = "bkai-foundation-models/vietnamese-bi-encoder"
    embedding_batch_size: int = 32

    # pgvector / Search
    hnsw_m: int = 16
    hnsw_ef_construction: int = 128  # Theo PhanTichHeThong_v2_Fixed.docx mục 10.2
    top_k_retrieve: int = 20
    top_k_rerank: int = 5
    rrf_k: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
