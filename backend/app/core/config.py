# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 计算项目根目录
# config.py 在 backend/app/core/ 下，向上 4 级到达项目根目录
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(_BACKEND_DIR)  # 项目根目录

load_dotenv()

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Database — 始终使用绝对路径
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

    # Chroma — 始终使用绝对路径
    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, 'data', 'chroma_data')

    # OpenAI-compatible
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

    # DeepSeek 别名
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        return self.OPENAI_API_KEY

    @property
    def DEEPSEEK_BASE_URL(self) -> str:
        return self.OPENAI_BASE_URL

    @property
    def DEEPSEEK_MODEL(self) -> str:
        return self.LLM_MODEL

    # Upload directory
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        os.path.join(BASE_DIR, 'backend', 'app', 'static', 'uploads')
    )

settings = Settings()