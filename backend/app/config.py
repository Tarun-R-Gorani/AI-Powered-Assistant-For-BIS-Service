import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "BIS Smart Assistant API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    GROQ_API_KEY: str = ""

    LLM_MODEL: str = "llama-3.1-8b-instant"

    BASE_DIR: str = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    DATA_DIR: str = os.path.join(
        BASE_DIR,
        "data"
    )

    FAISS_INDEX_PATH: str = os.path.join(
        DATA_DIR,
        "faiss_index"
    )

    EMBEDDING_MODEL_NAME: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()