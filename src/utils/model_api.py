import requests
import json
import os
import openai
from functools import lru_cache
from itertools import cycle

MODEL_API_URL = "model_api:80"
api_keys = os.getenv("OPENAI_API_KEYS").split(',')
print(f"api_keys: {api_keys}")
api_keys_cycle = cycle(api_keys)

def generate(inputs: str, temperature: float) -> str:
    return requests.post(
        f"http://{MODEL_API_URL}/v1/completions",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'prompt': inputs,
            "min_tokens": 30,
            "max_tokens": 96,
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

@lru_cache(maxsize=1024)
def generate_conversation_chatgpt_api(inputs: str) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=inputs,
        # temperature=1,
        max_tokens=512,
        top_p=0.95,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["User:"],
        api_key=next(api_keys_cycle),
    )['choices'][0]['text']
    return response

@lru_cache(maxsize=1024)
def generate_action_chatgpt_api(inputs: str) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=inputs,
        temperature=0,
        max_tokens=12,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[r"]"],
        api_key=next(api_keys_cycle),
    )['choices'][0]['text']
    return response

@lru_cache(maxsize=1024)
def generate_action_params_chatgpt_api(inputs: str) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=inputs,
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[r"]"],
        api_key=next(api_keys_cycle),
    )['choices'][0]['text']
    return response
    

def generate_mock(inputs: str, temperature: float) -> str:
    return "Intent:TRANSFER_MONEY\nAction:TRANSFER_MONEY[amount=100, from=Minh, to=test9]\nAssistant: Sure Onii-chan 🥺! I will send Minh 100$ for the pizza."
