import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Force Google SDK to use stable v1 endpoints
os.environ["GOOGLE_API_USE_V1"] = "true"


load_dotenv()


@dataclass(frozen=True)
class Config:
    """Centralized configuration for ai-dev-coach."""

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    SESSION_SAVE_PATH: str = os.getenv("SESSION_SAVE_PATH", "./data/sessions")

    # Settings
    MAX_REVIEW_LOOPS: int = int(os.getenv("MAX_REVIEW_LOOPS", 3))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        """Validate required configuration and ensure paths exist."""

        missing = []
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not self.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")

        if missing:
            formatted = ", ".join(missing)
            raise ValueError(
                f"Missing required environment variables: {formatted}. "
                "Set them in your .env file (see .env.example and README)."
            )

        Path(self.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.SESSION_SAVE_PATH).mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    config = Config()
    config.validate()
    return config


settings = load_config()
