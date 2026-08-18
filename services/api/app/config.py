from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_env: str = 'development'
    database_url: str = 'postgresql+psycopg://bim:bim@db:5432/bim'
    redis_url: str = 'redis://redis:6379/0'
    upload_dir: str = '/data/uploads'
    default_org_id: str = '11111111-1111-1111-1111-111111111111'
    log_level: str = 'INFO'


settings = Settings()
