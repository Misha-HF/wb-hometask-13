from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = 'postgresql+psycopg2://user:password@host:port/db'
    postgres_user: str = 'secret_key'
    postgres_password: str = '123456'
    postgres_port: int = 1234
    sqlalchemy_database_url: str = "sqlite:///./my.db"
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    mail_username: str = 'mail@mail.com'
    mail_password: str = 'password'
    mail_from: str = mail_username
    mail_port: int = 465
    mail_server: str = 'mail.server.com'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: str = 'api'
    cloudinary_api_secret: str = 'api_secret'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
