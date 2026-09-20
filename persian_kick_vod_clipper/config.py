from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    kick_cookie_file: Path | None = None
    google_service_account_file: Path | None = None
    google_drive_folder_id: str | None = None
    whisper_model: str = "medium"
    temp_dir: Path = Path("tmp")
    output_dir: Path = Path("outputs")
    log_level: str = "INFO"

    def prepare(self) -> None:
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

