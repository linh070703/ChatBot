import requests
import json

MODEL_API_URL = "model_api:80"

def generate(inputs: str, temperature: float) -> str:
    return requests.post(
        f"http://{MODEL_API_URL}/v1/completions",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'prompt': inputs,
            "min_tokens": 30,
            "max_tokens": 2048,
            "temperature": temperature,
            # "n": int, 
        })
    ).json()['choices'][0]['text']