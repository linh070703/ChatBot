import requests
import json
import os
import openai
from functools import lru_cache, wraps
from itertools import cycle
from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from time import sleep
import logging
from dotenv import load_dotenv
load_dotenv()

MODEL_API_URL = "model_api:80"
api_keys = os.getenv("OPENAI_API_KEYS").split(',')
logging.info(f"api_keys: {api_keys}")
api_keys_cycle = cycle(api_keys)

def handle_api_errors(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except openai.error.APIError as e:
                    if e.status == 429:
                        print("Error: ", e)
                        print("API usage limit reached. Switching to the next API key.")
                        return wrapper(*args, **kwargs)
                    raise e
            sleep(5)
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except openai.error.APIError as e:
                    if e.status == 429:
                        print("Error: ", e)
                        print("API usage limit reached. Switching to the next API key.")
                        return wrapper(*args, **kwargs)
                    raise e
            raise Exception(f"API usage limit reached. Tried {max_retries * 2} times.")
        return wrapper
    return decorator

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
@handle_api_errors(max_retries=len(api_keys))
def generate_general_call_chatgpt_api(
        inputs: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: int = 64,
        stop: Optional[Tuple[str]] = None,
    ) -> str:
    params = {}
    # either of temperature or top_p must be specified
    if temperature is not None:
        params['temperature'] = temperature
    if top_p is not None:
        params['top_p'] = top_p
    if len(params) == 0:
        raise ValueError("Either of temperature or top_p must be specified.")
    if stop is not None:
        params['stop'] = stop

    params['max_tokens'] = max_tokens
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=inputs,
        **params,
        api_key=next(api_keys_cycle),
    )['choices'][0]['text']
    return response
