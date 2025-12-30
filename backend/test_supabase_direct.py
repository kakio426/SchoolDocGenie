
import os
from dotenv import load_dotenv
from pathlib import Path
from services.supabase_service import SupabaseService

# Load env using the same logic as main.py
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

print(f"URL from env: {os.getenv('SUPABASE_URL')[:20]}...")

service = SupabaseService()
id = service.store_document(
    content="Direct test content",
    metadata={"filename": "direct_test.md", "title": "Direct Test"},
    summary="Testing Supabase connection directly"
)
print(f"Stored Document ID: {id}")
