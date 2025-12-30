
import os
from dotenv import load_dotenv
from pathlib import Path

print("--- Checking Environment Variables ---")
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
print(f"Target .env path: {env_path}")
print(f"File exists: {env_path.exists()}")

loaded = load_dotenv(dotenv_path=env_path)
print(f"load_dotenv() result: {loaded}")

keys = ["GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
for key in keys:
    val = os.getenv(key)
    status = "SET" if val else "NOT SET"
    preview = f"({val[:10]}...)" if val else ""
    print(f"{key}: {status} {preview}")
