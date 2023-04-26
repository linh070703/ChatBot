from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
    send_from_directory
)
from flask_cors import CORS
from typing import List, Dict, Union, Any
from queue import Queue
import threading
import time
import json
import sys
import requests
import logging
from utils.entities import Conversation
from utils.prompt_factory import MODE
from utils.mock import mock_app
from utils.model_api import generate_mock, generate_torchserve
from utils.logger import setup_logging

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)
setup_logging('app.log')
print = logging.info

@app.route('/api/chat', methods=['POST'])
def chat():
    _ = request.json.get('model', 'gpt4all')
    temperature = request.json.get('temperature', 0.7)
    messages = request.json.get('messages', [])
    n_predict = request.json.get('max_num_words', 64)
    stream = request.json.get('stream', False)
    stream_json = request.json.get('stream_json', False)
    userInfo = request.json.get('userInfo', {"status": None})
    generate = generate_mock if request.json.get('mock', False) else generate_torchserve
    
    if stream:
        return jsonify({'error': 'Stream mode is not supported.'})
    if not messages:
        return jsonify({'error': 'No messages provided.'})
    print(f"Received request: {request.json}")

    # get intent
    conversation = Conversation({'command': MODE['detect-intent'], 'messages': messages, 'userInfo': userInfo})
    input = conversation.prepare_model_input()
    input_for_model = input + 'Intent: '
    print(f"Input: {input_for_model}")

    assistant_answer = generate(input_for_model, temperature)
    
    print(f"Assistant_answer: {assistant_answer}")

    intent = conversation.extract_intent(assistant_answer)

    print(f"Intent: {intent}")

    if intent == 'NO_BOT_ACTION':
        return jsonify({
            'intent': intent,
        })
    elif intent == 'ASK_ASSISTANT':
        conversation.command = MODE['response']
        next_input = conversation.prepare_model_input() + "Intent: " + intent + "\nAssistant: "
        print(f"Next_input for response: {next_input}")
        assistant_answer = generate(next_input, temperature)
        print(f"Assistant_answer: {assistant_answer}")
        bot_response = conversation.extract_response(assistant_answer)
        print(f"Bot_response: {bot_response}")
        return jsonify({
            'message': {
                'role': 'assistant', 'content': bot_response
            },
            'intent': intent,
        })

    conversation.command = MODE['action']

    next_input = conversation.prepare_model_input() + "Intent: " + intent + "\nAction: "

    print(f"Next_input for action: {next_input}")

    raw_action = generate(next_input, temperature)
    
    print(f"Raw_action: {raw_action}")

    action = conversation.extract_action(raw_action)
    r_action = conversation.extract_action(raw_action, get_raw=True)

    print(f"Action: {action}")

    conversation.command = MODE['response']

    next_input = conversation.prepare_model_input() + "Intent: " + intent + "\nAction:" + r_action + "\nAssistant: "

    print(f"Next_input for response: {next_input}")
    
    assistant_answer = generate(next_input, temperature)

    print(f"Assistant_answer: {assistant_answer}")
    
    bot_response = conversation.extract_response(assistant_answer)

    print(f"Bot_response: {bot_response}")

    return jsonify({
        'message': {
            'role': 'assistant', 'content': bot_response
        },
        'intent': intent,
        'action': action
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
