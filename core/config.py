
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
            env_file=".env",
            extra="ignore",
            env_file_encoding="utf-8",
            case_sensitive=True
        )

    PROJECT_NAME: str = "Blog API"
    BASE_URL: str = "http://localhost:8000"  # public URL of this API
    FRONTEND_URL: str = "http://localhost:3000"  # frontend used for redirects
    VERSION: str = "1.0.0"
    DEBUG: bool 

    # Database
    DATABASE_URL: str 


    #files
    ALLOWED_MEDIA_TYPES: list = ["application/wps-office.docx", "application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    MAX_MEDIA_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB

    # Redis
    REDIS_URL: str 
 
    # JWT
    SECRET_KEY: SecretStr 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_VERIFICATION_EXPIRE_HOURS: int= 1
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAILS_FROM: str = "Joshua's Blog"
    SMTP_USER: str 
    SMTP_PASSWORD: SecretStr 
    
    #Admin
    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: SecretStr
    
    # CORS
    ALLOWED_ORIGINS: list[str] 
    ALLOWED_HOSTS: list[str]

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    # Rate limiting
    RATE_LIMIT_TIMES: int = 5
    RATE_LIMIT_SECONDS: int = 60

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: SecretStr
    CLOUDINARY_API_SECRET: SecretStr
    
        


@lru_cache
def get_setting():
    return Settings()

settings = get_setting()


