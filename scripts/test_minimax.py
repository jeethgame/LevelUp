import json
import requests
import time

api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRlYWFhNjFjLWNmM2EtNGUzMi04ZDA1LWFiZTJkMTc0ZDBkMiIsInNjb3BlIjoiaWVfbW9kZWwiLCJwcm9kdWN0IjoiSUUiLCJvd25lcklkIjoiMDI2MmExMjktYmM3ZC00YjhiLTllMTgtZTdiY2Q1MmRiYzg0In0.TtfAR-A7MLCrQftXhpphakcB8RwouMAAHik55NhCTzI"

# Test 1: OpenAI-compatible endpoint
url1 = "https://api.gmi-serving.com/v1/chat/completions"
headers1 = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
payload1 = {
    "model": "MiniMaxAI/MiniMax-M3",
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant with strong reasoning and coding ability."},
        {"role": "user", "content": "Hello! Explain briefly in 2 bullet points how MiniMax-M3 works."}
    ],
    "max_tokens": 512
}

print("--- Testing OpenAI-compatible endpoint (https://api.gmi-serving.com/v1/chat/completions) ---")
start_time = time.time()
try:
    res1 = requests.post(url1, headers=headers1, json=payload1, timeout=30)
    elapsed = time.time() - start_time
    print(f"Status Code: {res1.status_code} (took {elapsed:.2f}s)")
    print("Response:")
    print(json.dumps(res1.json(), indent=2))
except Exception as e:
    print(f"Error testing endpoint 1: {e}")

# Test 2: Structured JSON learning plan generation test
print("\n--- Testing Structured JSON Generation for LevelUP Learning Path ---")
payload_json = {
    "model": "MiniMaxAI/MiniMax-M3",
    "messages": [
        {"role": "system", "content": "You are an expert AI Career Coach. Return ONLY valid JSON with keys: 'roadmap_title', 'match_score', 'recommended_milestones' (list of 3 milestone strings)."},
        {"role": "user", "content": "Goal: Become an AI Engineer specializing in LLMs and FastAPI."}
    ],
    "max_tokens": 512
}
start_time = time.time()
try:
    res2 = requests.post(url1, headers=headers1, json=payload_json, timeout=30)
    elapsed = time.time() - start_time
    print(f"Status Code: {res2.status_code} (took {elapsed:.2f}s)")
    print("Response:")
    print(json.dumps(res2.json(), indent=2))
except Exception as e:
    print(f"Error testing JSON: {e}")
