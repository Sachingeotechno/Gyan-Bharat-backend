from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Gyan Bharat API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str
    SENDGRID_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "*"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mov,avi,mkv"
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    ALLOWED_DOCUMENT_EXTENSIONS: str = "pdf,doc,docx,ppt,pptx"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def video_extensions(self) -> List[str]:
        """Parse video extensions into a list."""
        return [ext.strip() for ext in self.ALLOWED_VIDEO_EXTENSIONS.split(",")]
    
    @property
    def image_extensions(self) -> List[str]:
        """Parse image extensions into a list."""
        return [ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",")]
    
    @property
    def document_extensions(self) -> List[str]:
        """Parse document extensions into a list."""
        return [ext.strip() for ext in self.ALLOWED_DOCUMENT_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
