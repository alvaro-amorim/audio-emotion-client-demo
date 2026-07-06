from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Audio Emotion Client Demo", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8020, alias="PORT")

    audio_emotion_api_base_url: str = Field(
        default="http://127.0.0.1:8014",
        alias="AUDIO_EMOTION_API_BASE_URL",
    )
    audio_emotion_api_key: str = Field(default="", alias="AUDIO_EMOTION_API_KEY")
    audio_emotion_api_key_header_name: str = Field(
        default="X-API-Key",
        alias="AUDIO_EMOTION_API_KEY_HEADER_NAME",
    )
    audio_emotion_api_timeout_seconds: float = Field(
        default=300,
        alias="AUDIO_EMOTION_API_TIMEOUT_SECONDS",
    )

    use_llm: bool = Field(default=True, alias="USE_LLM")
    llm_provider: str = Field(default="cohere", alias="LLM_PROVIDER")
    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")
    cohere_chat_model: str = Field(default="command-a-03-2025", alias="COHERE_CHAT_MODEL")

    default_assistant_profile: str = Field(default="support", alias="DEFAULT_ASSISTANT_PROFILE")
    show_raw_json: bool = Field(default=True, alias="SHOW_RAW_JSON")
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")
    allowed_audio_extensions: str = Field(
        default="mp3,wav,m4a,webm,ogg",
        alias="ALLOWED_AUDIO_EXTENSIONS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("audio_emotion_api_base_url")
    @classmethod
    def strip_base_url(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False
        return value

    @property
    def audio_emotion_api_key_configured(self) -> bool:
        return bool(self.audio_emotion_api_key.strip())

    @property
    def cohere_configured(self) -> bool:
        return bool(self.cohere_api_key.strip())

    @property
    def allowed_audio_extension_set(self) -> set[str]:
        return {
            extension.strip().lower().lstrip(".")
            for extension in self.allowed_audio_extensions.split(",")
            if extension.strip()
        }

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def safe_frontend_config(self) -> dict:
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "audio_emotion_api_base_url": self.audio_emotion_api_base_url,
            "use_llm": self.use_llm,
            "llm_provider": self.llm_provider,
            "default_assistant_profile": self.default_assistant_profile,
            "show_raw_json": self.show_raw_json,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
