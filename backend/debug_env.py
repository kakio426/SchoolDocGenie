
import os
from dotenv import load_dotenv

print("--- Checking Environment Variables ---")
print(f"Current Working Directory: {os.getcwd()}")

# 1. Check before loading
print(f"GEMINI_API_KEY before load_dotenv: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not Set'}")

# 2. Try loading
loaded = load_dotenv()
print(f"load_dotenv() returned: {loaded}")

# 3. Check after loading
api_key = os.getenv('GEMINI_API_KEY')
print(f"GEMINI_API_KEY after load_dotenv: {'Set' if api_key else 'Not Set'}")

if api_key:
    # 보안을 위해 앞 5자리만 출력
    print(f"API Key start: {api_key[:5]}...")

# 4. Check file existence
env_path = os.path.join(os.getcwd(), '.env')
print(f".env existing at {env_path}: {os.path.exists(env_path)}")
