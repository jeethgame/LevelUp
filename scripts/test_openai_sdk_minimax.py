import asyncio
from openai import AsyncOpenAI

api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRlYWFhNjFjLWNmM2EtNGUzMi04ZDA1LWFiZTJkMTc0ZDBkMiIsInNjb3BlIjoiaWVfbW9kZWwiLCJwcm9kdWN0IjoiSUUiLCJvd25lcklkIjoiMDI2MmExMjktYmM3ZC00YjhiLTllMTgtZTdiY2Q1MmRiYzg0In0.TtfAR-A7MLCrQftXhpphakcB8RwouMAAHik55NhCTzI"

async def test_openai_sdk():
    client = AsyncOpenAI(
        base_url="https://api.gmi-serving.com/v1",
        api_key=api_key
    )
    res = await client.chat.completions.create(
        model="MiniMaxAI/MiniMax-M3",
        messages=[
            {"role": "system", "content": "You are a software architect. Return JSON."},
            {"role": "user", "content": "Generate a short JSON object with 'status': 'connected', 'model': 'MiniMax-M3'."}
        ],
        temperature=0.2
    )
    print("AsyncOpenAI SDK Output:")
    print(res.choices[0].message.content)

asyncio.run(test_openai_sdk())
