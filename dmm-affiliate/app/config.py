from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_env(path: str | Path | None = None) -> None:
    env_path = Path(path) if path else ROOT_DIR / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    dmm_api_id: str | None
    dmm_affiliate_id: str | None
    supabase_url: str | None
    supabase_service_role_key: str | None
    default_account_id: str
    default_reward_type: str


def get_settings() -> Settings:
    load_env()
    return Settings(
        dmm_api_id=os.getenv("DMM_API_ID") or None,
        dmm_affiliate_id=os.getenv("DMM_AFFILIATE_ID") or None,
        supabase_url=os.getenv("SUPABASE_URL") or None,
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY") or None,
        default_account_id=os.getenv("DEFAULT_ACCOUNT_ID", "sale_flash"),
        default_reward_type=os.getenv("DEFAULT_REWARD_TYPE", "direct"),
    )
