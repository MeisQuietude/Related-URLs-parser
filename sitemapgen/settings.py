import pydantic


class PostgresSettings(pydantic.BaseSettings):
    hostname: str = pydantic.Field(default="db")
    port: int = pydantic.Field(default=5432)
    database: str = pydantic.Field(default="parser")
    username: str = pydantic.Field(default="parser")
    password: str = pydantic.Field(default="parser")

    class Config:
        env_prefix = "POSTGRES_"


class Settings(pydantic.BaseSettings):
    postgres: PostgresSettings = pydantic.Field(default_factory=PostgresSettings)
