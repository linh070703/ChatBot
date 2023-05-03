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
from queue import Queue
import threading
import time
import json
import sys
import requests
import logging
from src.utils.logger import setup_logging, pprint, print
from src.models.action import get_action_params
from src.models.intention_detector import dectect_user_intention
from src.models.ask_assistant import ask_assistant
import re

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.json.ensure_ascii = False

CORS(app)
setup_logging('app.log')

# check health
@app.route('/health', methods=['POST'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint: /api/chat
    Content-Type: application/json
    Method: POST
    Request:
        Body: {
            messages: [
                {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."},
            ]
        }
    Response:
        {
            action: {
                command: "TRANSFER",
                params: {
                    "receiver": "Minh",
                    "amount": "300000",
                    "msg": null
                }
            }
        }
    ---
    Example:
    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Cuong", "content": "Hi, I want to transfer 300k to Minh."},
    ...     ]
    ... }).json()
    {'action': {'command': 'TRANSFER', 'params': {'receiver': 'Minh', 'amount': '300000', 'msg': None}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Cuong", "content": "Tao muốn chuyển mỗi đứa 800k tiền mừng năm mới."},
    ...     ]
    ... }).json()
    {'action': {'command': 'TRANSFER_TO_EACH_USERS', 'params': {'amount_each': '800000', 'msg': 'tiền mừng năm mới'}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "Tao muốn tạo nhóm chat với Nam và Lan."},
    ...     ]
    ... }).json()
    {'action': {'command': 'CREATE_CHAT_GROUP', 'params': {'members': ['Nam', 'Lan']}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "Tài khoản của tao còn bao nhiêu tiền?"},
    ...     ]
    ... }).json()
    {'action': {'command': 'CHECK_BALANCE', 'params': {'user': 'Minh'}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "Ủa mày thích ăn đấm không?"},
    ...     ]
    ... }).json()
    {'action': {'command': 'NO_ACTION', 'params': {}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "Tôi muốn được tư vấn về việc lên kế hoạch quản lý tài chính."},
    ...     ]
    ... }).json()
    {
        'action': {
            'command': 'ASK_ASSISTANT',
            'params': {},
        },
        'message': {'role': 'assistant', 'content': 'Ok, thu nhập mỗi tháng của bạn là bao nhiêu?'},
        'suggestions': []
    }

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "I want to ask for financial advice"},
    ...     ]
    ... }).json()
    {
        'action': {
            'command': 'ASK_ASSISTANT',
            'params': {},
        },
        'message': {'role': 'assistant', 'content': 'Sure, I can help you with that. What do you want to ask?'},
        'suggestions': ['Help me create a monthly budget plan', 'Help me calculate my target saving plan', 'Help me detect if a loan is usury or not', 'Help me invest my money', 'Help me pay off my debt']
    }
    """
    print(f"Received request: {request.json}")
    _ = request.json.get('model', 'gpt4all')
    messages = request.json.get('messages', [])
    stream = request.json.get('stream', False)
    userInfo = request.json.get('userInfo', {"status": None})
    for message in messages:
        if 'role' in message:
            return jsonify({'error': 'Role is not allowed. Deprecated.'}), 400
        if 'message' in message:
            return jsonify({'error': 'Message is not allowed. Deprecated.'}), 400
        if 'user' not in message:
            return jsonify({'error': 'User is not provided.'}), 400
        if 'content' not in message:
            return jsonify({'error': 'Content is not provided.'}), 400
        

    
    if stream:
        return jsonify({'error': 'Stream mode is not supported.'}), 400
    if not messages:
        bot_response, suggestions = ask_assistant(messages)
        return jsonify({
            'message': {
                'role': 'assistant', 'content': bot_response
            },
            'suggestions': suggestions
        })

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

        bot_response, suggestions = ask_assistant(messages)

        bot_response = re.sub("(?i)chatGPT", "your personal assistant", bot_response)

        print(f"Answer: {bot_response}")

        res = {
            'message': {
                'role': 'assistant', 'content': bot_response
            },
            'action': {
                'command': 'ASK_ASSISTANT',
                'params': {}
            },
            'suggestions': suggestions,
        }
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
        payload = get_action_params(messages, action='TRANSFER')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'TRANSFER',
                    'params': payload
                }
            }
        else:
            res = {
                'action': {
                    'command': 'ASK_ASSISTANT',
                    'params': {}
                },
                'message': {
                    'role': 'assistant', 'content': payload
                },
                'suggestions': []
            }
    elif intention == 'TRANSFER_TO_EACH_USERS':
        payload = get_action_params(messages, action='TRANSFER_TO_EACH_USERS')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'TRANSFER_TO_EACH_USERS',
                    'params': payload
                }
            }
        else:
            res = {
                'action': {
                    'command': 'ASK_ASSISTANT',
                    'params': {}
                },
                'message': {
                    'role': 'assistant', 'content': payload
                },
                'suggestions': []
            }
    elif intention == 'CREATE_CHAT_GROUP':
        payload = get_action_params(messages, action='CREATE_CHAT_GROUP')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'CREATE_CHAT_GROUP',
                    'params': payload
                }
            }
        else:
            res = {
                'action': {
                    'command': 'ASK_ASSISTANT',
                    'params': {}
                },
                'message': {
                    'role': 'assistant', 'content': payload
                },
                'suggestions': []
            }
    else:
        raise Exception(f"Unknown intention: {intention}")
    
    logging.info(f"Response: {res}")
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
