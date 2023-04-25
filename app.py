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
from prompt_factory import MODE
from queue import Queue
import threading
import time
import json
import sys
import requests

model = None

MODEL_API_URL = "model_api:80"

def generate(inputs: str, temperature: float) -> str:
    return requests.post(
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

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    _ = request.json.get('model', 'gpt4all')
    temperature = request.json.get('temperature', 0.7)
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

    # Get chat answer
    conversation = Conversation({'command': MODE['chat'], 'messages': messages, 'userInfo': userInfo})
    input = conversation.raw_conversation
    print(f"Input: {input}")

    assistant_answer = generate(input, temperature)
    
    print(f"Assistant_answer: {assistant_answer}")

    conversation.command = MODE['action']

    next_input = conversation.prepare_model_input() + assistant_answer

    print(f"Next_input: {next_input}")

    raw_action = generate(next_input, temperature)

    action = conversation.extract_action(raw_action)

    return jsonify({
        'message': {
            'role': 'assistant', 'content': assistant_answer
        },
        'action': action
    })

@app.route('/api/detect-intent', methods=['POST'])
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

    raw_intent = generate(input, temperature)
    
    print(f"Raw_intent: {raw_intent}")
    intent = conversation.extract_intent(raw_intent)

    if intent != 'CANNOT_EXTRACT_INTENT':
        return jsonify({
            'intent': intent, 
        })
    else:
        print(f"Cannot extract intent from the conversation: {raw_intent}")
        return jsonify({
            'intent': 'CANNOT_EXTRACT_INTENT', 
            'error': 'Cannot extract intent from the conversation.'
        })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
