from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ---------- PostgreSQL ----------

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # ---------- Redis ----------

    REDIS_HOST: str
    REDIS_PORT: int
    QUEUE_NAME: str

    # ---------- Storage ----------

    STORAGE_ROOT: str
    MARKER_OUTPUT_FOLDER: str
    
    # ---------- Marker ----------
    LLAMA_CPP_BINARY: str
    CHUNK_MAX_CHARACTERS: int = 6000
    
    # =========================================================
    # Embeddings
    # =========================================================

    EMBEDDING_MODEL: str = (
        "BAAI/bge-base-en-v1.5"
    )

    EMBEDDING_DIMENSION: int = 768
    
    # llm service credentials
    
    GROQ_API_KEY: str
    GROQ_MODEL: str
    GROQ_BASE_MODEL: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()