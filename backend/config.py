"""All settings come from environment variables / `.env` (see `.env.example`).

Only typed, validated values leave this module: a typo such as `CHECK_INTERVAL_HOURS=abc`
stops the app at startup with a clear message instead of failing later at runtime.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Rivalscope"
    public_url: str = "http://localhost:3000"  # used in links inside notifications
    database_url: str = f"sqlite:///{(ROOT_DIR / 'data' / 'rivalscope.db').as_posix()}"

    # --- AI & search ---------------------------------------------------------------
    openai_api_key: SecretStr | None = None
    tavily_api_key: SecretStr | None = None
    model_fast: str = "gpt-6-luna"  # extraction, classification, query planning
    model_smart: str = "gpt-6.1-sol"  # human-readable insights
    reasoning_effort_fast: str = "low"  # empty string = don't send the parameter
    reasoning_effort_smart: str = "medium"
    # USD per 1M tokens as (input, output). Only used to show the cost of each agent run.
    model_prices: dict[str, tuple[float, float]] = {
        "gpt-6-luna": (0.10, 0.50),
        "gpt-6.1-sol": (2.00, 10.00),
    }

    # --- Monitoring ----------------------------------------------------------------
    scheduler_enabled: bool = True
    check_interval_hours: float = 12
    alert_min_change_pct: float = 1.0  # smaller price moves are recorded but don't alert
    review_jump_pct: float = 60.0  # bigger jumps are flagged for review instead of trusted
    max_products_per_user: int = 25
    max_offers_per_product: int = 6
    fetch_timeout_seconds: float = 15
    fetch_max_bytes: int = 3_000_000

    # --- Access --------------------------------------------------------------------
    session_days: int = 30
    cookie_secure: bool = False  # set to true behind HTTPS
    contact_email: str | None = None  # shown in the "Request access" dialog
    contact_telegram: str | None = None  # e.g. "your_username" (without @)

    # --- Notifications -------------------------------------------------------------
    telegram_bot_token: SecretStr | None = None
    telegram_bot_username: str | None = None  # without @, used for the "Connect" deep link
    owner_telegram_chat_id: str | None = None  # access requests are forwarded here
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from: str | None = None
    smtp_ssl: bool = False  # true for port 465, false = STARTTLS

    @property
    def llm_configured(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.get_secret_value())

    @property
    def search_configured(self) -> bool:
        return bool(self.tavily_api_key and self.tavily_api_key.get_secret_value())

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_bot_token.get_secret_value())

    @property
    def email_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)


@lru_cache
def get_settings() -> Settings:
    return Settings()
