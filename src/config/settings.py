from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Ponte Nexus"
    database_url: str = Field(default="sqlite:///data/ponte_nexus.db")


settings = Settings()
