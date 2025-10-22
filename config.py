from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
ENV_FILES = [str(ENV_PATH)] if ENV_PATH.exists() else None

class BaseConfig(BaseSettings):
    DB_URL: str
    DB_NAME: str
    CLOUDINARY_SECRET_KEY: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_CLOUD_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",           # .env가 있을 때만 로드
        env_file_encoding="utf-8",
        extra="ignore",
    )

def load_settings() -> "BaseConfig":
    try:
        s = BaseConfig()
    except Exception as e:
        # pydantic이 "field required"를 내면 친절하게 변환
        raise RuntimeError(
            "환경 설정 누락: DB_URL, DB_NAME 을 환경변수로 넣거나 "
            ".env 파일을 생성하세요. (Render에서는 Settings→Environment에 등록)"
        ) from e
    return s

settings = load_settings()