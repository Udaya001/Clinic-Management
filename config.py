from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    PROJECT_NAME: str = "Clinic Backend"

    # API settings
    API_V1_STR: str = "/api"
    API_VERSION: str = "1.0.0"

    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True

    # JWT settings
    JWT_SECRET_KEY: str 
    JWT_REFRESH_SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str

    # MongoDB settings
    MONGODB_URL: str 
    MONGODB_DB_NAME: str 



settings = Settings()