import requests, json, os

token = os.environ.get("HF_TOKEN", "")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Test the new HF Inference API (v2) - chat completions format with free models
models = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/gemma-2-9b-it",
]

for model in models:
    url = f"https://api-inference.huggingface.co/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
        "max_tokens": 50
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"{model}: HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            ans = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"  SUCCESS: {ans[:80]}")
        else:
            print(f"  Error: {r.text[:120]}")
    except Exception as e:
        print(f"{model}: {e}")
