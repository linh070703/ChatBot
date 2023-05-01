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
from utils.entities import Conversation, get_all_upper_triangle
from utils.prompt_factory import MODE
from utils.mock import mock_app
from utils.model_api import generate_mock, generate_torchserve, generate_chatgpt_api
from utils.logger import setup_logging, pprint, print
from models.action import get_action_params
from models.intention_detector import dectect_user_intention
from models.ask_assistant import ask_assistant
import re

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)
setup_logging('app.log')

# check health
@app.route('/health', methods=['POST'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/chat', methods=['POST'])
def chat():
    _ = request.json.get('model', 'gpt4all')
    temperature = request.json.get('temperature', 0.7)
    messages = request.json.get('messages', [])
    n_predict = request.json.get('max_num_words', 64)
    stream = request.json.get('stream', False)
    stream_json = request.json.get('stream_json', False)
    userInfo = request.json.get('userInfo', {"status": None})
    generate = generate_chatgpt_api
    for message in messages:
        assert 'role' not in message, 'Role is not allowed. Deprecated.'
        assert 'user' in message, 'User is not provided.'
        assert 'message' in message, 'Message is not provided.'
    
    if stream:
        return jsonify({'error': 'Stream mode is not supported.'})
    if not messages:
        return jsonify({'error': 'No messages provided.'})
    print(f"Received request: {request.json}")

    print(f"All Messages: {messages}")
    print(f'====================')

    intention = dectect_user_intention(messages)

    print(f"Intention: {intention}")

    if intention == 'NO_SYSTEM_ACTION':
        return jsonify({
            'action': {
                'command': 'NO_ACTION',
                'params': {}
            }
        })
    
    elif intention == 'ASK_ASSISTANT':
        print(f"Bot_response: {bot_response}")

        bot_response = ask_assistant(messages, userInfo)

        bot_response = re.sub("(?i)chatGPT", "your personal assistant", bot_response)
        print(f"Answer: {bot_response}")

        res = jsonify({
            'message': {
                'role': 'assistant', 'content': bot_response
            },
            'action': {
                'command': 'ASK_ASSISTANT',
                'params': {}
            }
        })
    elif intention == 'CHECK_BALANCE':
        res = {
            'action': {
                'command': 'CHECK_BALANCE',
                'params': {
                    'user': messages[-1]['user']
                }
            }
        }
    elif intention == 'TRANSFER':
        action_params = get_action_params(messages, action='TRANSFER')
        res = {
            'action': {
                'command': 'TRANSFER',
                'params': action_params
            }
        }
    elif intention == 'TRANSFER_TO_EACH_USERS':
        action_params = get_action_params(messages, action='TRANSFER_TO_EACH_USERS')
        res = {
            'action': {
                'command': 'TRANSFER_TO_EACH_USERS',
                'params': action_params
            }
        }
    elif intention == 'CREATE_CHAT_GROUP':
        action_params = get_action_params(messages, action='CREATE_CHAT_GROUP')
        res = {
            'action': {
                'command': 'CREATE_CHAT_GROUP',
                'params': action_params
            }
        }
    else:
        raise Exception(f"Unknown intention: {intention}")
    
    logging.info(f"Response: {res}")
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
