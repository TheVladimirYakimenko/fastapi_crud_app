from dataclasses import dataclass

from environs import Env


@dataclass
class Config:
    database_url: str
    secret_key: str
    algorithm: str = 'HS256'


def get_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        database_url=env('DATABASE_URL'),
        secret_key=env('SECRET_KEY')
    )
