from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    GROQ_API_KEY: str
    WHISPER_MODEL: str = "whisper-large-v3-turbo"
    GROQ_MODEL: str = "qwen/qwen3.6-27b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8-sig"


settings = Settings()