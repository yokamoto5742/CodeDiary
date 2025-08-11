import os
from dotenv import load_dotenv

load_dotenv()

print("=== API キー設定状況 ===")
print(f"OPENAI_API_KEY: {'設定済み' if os.environ.get('OPENAI_API_KEY') else '未設定'}")
print(f"GEMINI_API_KEY: {'設定済み' if os.environ.get('GEMINI_API_KEY') else '未設定'}")
print(f"CLAUDE_API_KEY: {'設定済み' if os.environ.get('CLAUDE_API_KEY') else '未設定'}")
print("========================")
