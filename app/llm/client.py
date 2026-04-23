import requests

def ask_llm(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model":"qwen2.5:7b",
            "prompt":prompt,
            "stream":False
        },
        timeout=120
    )

    return response.json()["response"].strip()
