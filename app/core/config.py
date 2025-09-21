from functools import lru_cache
from datetime import timedelta, timezone
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./booking.db"
    admin_username: str = "admin"
    admin_password: str = "secret"
    timezone_offset_hours: int = 2
    auto_confirm_hours: int = 48
    scheduler_enabled: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def local_timezone(self) -> timezone:
        return timezone(timedelta(hours=self.timezone_offset_hours))


@lru_cache()
def get_settings() -> Settings:
    return Settings()
