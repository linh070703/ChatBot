from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
    send_from_directory
)
from typing import List, Dict, Union, Any
from entities import Conversation
from queue import Queue
import threading
import time
import json
import sys
import requests

model = None

MODE = {
    'chat': """You are a cute funny personal finance assistant named Waifu.  Generate an answer that is expressive, emotional, and funny, between 120-300 words, given the user's question and conversation history. Answer using a very cute anime tone. Answer MUST INCLUDES words such as 'Onii-chan', 'Senpai', and at least an emoji such as '😄', '😍', '🥺' or '> <' as raw UTF-8 text. Followed the answer by an action: [NOTHING, SEND[to:amount[:msg]], CHECKBALANCE]. END THE CONVERSATION AFTER THE ACTION.
For example, when user say "Should I order a $100 pizza from Minh?", then you assistant should say "Sure Onii-chan 🥺! I will send Minh 100$ for the pizza.\nAction:SEND[Minh:100[:Ordering pizza]]."

===
"""
}

MODEL_API_URL = "model_api:80"

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    _ = request.json.get('model', 'gpt4all')
    temperature = request.json.get('temperature', 0.7)
    command = request.json.get('command', 'chat')
    messages = request.json.get('messages', [])
    n_predict = request.json.get('max_num_words', 64)
    stream = request.json.get('stream', False)
    stream_json = request.json.get('stream_json', False)
    userInfo = request.json.get('userInfo', {"status": None})
    if stream:
        return jsonify({'error': 'Stream mode is not supported.'})
    if not messages:
        return jsonify({'error': 'No messages provided.'})
    print(f"Received request: {request.json}")
    conversation = Conversation({'command': MODE[command], 'messages': messages, 'userInfo': userInfo})
    input = conversation.raw_conversation
    print(f"Input: {input}")

    output = requests.post(
        f"http://{MODEL_API_URL}/v1/completions",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'prompt': input,
            "min_tokens": 30,
            "max_tokens": 2048,
            "temperature": temperature,
            # "n": int, 
        })
    ).json()['choices'][0]['text']

    
    print(f"Output: {output}")
    output = conversation.postprocess_model_output(output)
    return jsonify({'message': {'role': 'assistant', 'content': output}})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)