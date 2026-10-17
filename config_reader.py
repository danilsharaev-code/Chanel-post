from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr

    db_url: PostgresDsn

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
