from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini API (이미지 분석 - 무료)
    # https://aistudio.google.com/app/apikey
    gemini_api_key: str = ""

    # Groq API (스크립트 생성 - 무료)
    # https://console.groq.com/keys
    groq_api_key: str = ""

    # Replicate API (영상 생성 - Minimax video-01)
    # https://replicate.com/account/api-tokens
    # 무료: 카드 없이 제한된 횟수 무료 사용 가능
    replicate_api_key: str = ""

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "ap-northeast-2"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Database
    database_url: str = ""

    # App
    secret_key: str = "dev-secret-key"
    debug: bool = True

    # CORS - Render 프론트엔드 URL
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
