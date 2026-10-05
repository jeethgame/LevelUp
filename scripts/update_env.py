env_text = """FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json

# MiniMax-M3 / OpenAI-Compatible Configuration
OPENAI_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRlYWFhNjFjLWNmM2EtNGUzMi04ZDA1LWFiZTJkMTc0ZDBkMiIsInNjb3BlIjoiaWVfbW9kZWwiLCJwcm9kdWN0IjoiSUUiLCJvd25lcklkIjoiMDI2MmExMjktYmM3ZC00YjhiLTllMTgtZTdiY2Q1MmRiYzg0In0.TtfAR-A7MLCrQftXhpphakcB8RwouMAAHik55NhCTzI
OPENAI_BASE_URL=https://api.gmi-serving.com/v1
OPENAI_MODEL=MiniMaxAI/MiniMax-M3

# MiniMax Aliases
MINIMAX_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRlYWFhNjFjLWNmM2EtNGUzMi04ZDA1LWFiZTJkMTc0ZDBkMiIsInNjb3BlIjoiaWVfbW9kZWwiLCJwcm9kdWN0IjoiSUUiLCJvd25lcklkIjoiMDI2MmExMjktYmM3ZC00YjhiLTllMTgtZTdiY2Q1MmRiYzg0In0.TtfAR-A7MLCrQftXhpphakcB8RwouMAAHik55NhCTzI
MINIMAX_BASE_URL=https://api.gmi-serving.com/v1
MINIMAX_MODEL=MiniMaxAI/MiniMax-M3
"""
with open("backend/.env", "w", encoding="utf-8") as f:
    f.write(env_text)
print("backend/.env updated successfully")
