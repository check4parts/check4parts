import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BMPARTS_BASE_URL = os.getenv("BMPARTS_BASE_URL", "")
BMPARTS_API_KEY = os.getenv("BMPARTS_API_KEY")
