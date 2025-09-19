import os
from dotenv import load_dotenv

load_dotenv()


def _get_bool_env(var_name: str, default: bool) -> bool:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BM_PARTS_TOKEN = os.getenv("BM_PARTS_TOKEN")
ASG_TOKEN = os.getenv("ASG_TOKEN")
OMEGA_KEY = os.getenv("OMEGA_KEY")
UNIQTRADE_EMAIL = os.getenv("UNIQTRADE_EMAIL")
UNIQTRADE_PASSWORD = os.getenv("UNIQTRADE_PASSWORD")
UNIQTRADE_FINGERPRINT = os.getenv("UNIQTRADE_FINGERPRINT")
INTERCARS_CLIENT_ID = os.getenv("INTERCARS_CLIENT_ID")
INTERCARS_CLIENT_SECRET = os.getenv("INTERCARS_CLIENT_SECRET")

ENABLE_MUTATING_GET_ROUTES = _get_bool_env("ENABLE_MUTATING_GET_ROUTES", False)
