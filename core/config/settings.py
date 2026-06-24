from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    SECCRET_KEY: str

    ACCESS_TOKEN_EXPIRATION: int
    REFRESH_TOKEN_EXPIRATION: int
    REFRESH_TOKEN_COOKIE_NAME: str
    ACCESS_TOKEN_COOKIE_NAME: str

    REDIS_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
