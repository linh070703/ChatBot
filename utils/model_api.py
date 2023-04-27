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

def generate_torchserve(inputs: str, temperature: float) -> str:
    data = requests.post(
        f"http://{MODEL_API_URL}/predictions/bloomz-3b",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'prompt': inputs,
            'echo': True,
        })
    ).json()
    print(f'generate_torchserve: {data}')
    return data['text']

def generate_mock(inputs: str, temperature: float) -> str:
    return "Intent:TRANSFER_MONEY\nAction:TRANSFER_MONEY[amount=100, from=Minh, to=test9]\nAssistant: Sure Onii-chan 🥺! I will send Minh 100$ for the pizza."