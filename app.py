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
import re
import logging
import firebase_admin
from firebase_admin import credentials

# Setup firebase
cred = credentials.Certificate("./firebase.json")
firebase_admin.initialize_app(cred)

from src.utils.logger import setup_logging, pprint, print
from src.models.action import ensemble_get_action_params
from src.models.intention_detector import dectect_user_intention
from src.models.ask_assistant import ask_assistant, match_question
from src.models.response_message import get_response_message
from src.models.translator import convert_answer_language_to_same_as_question, answer_I_dont_know_multilingual, batch_convert_answer_language_to_same_as_question

from src.charts.chart import chart

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.json.ensure_ascii = False
app.register_blueprint(chart, url_prefix='/chart')

CORS(app)
setup_logging('app.log')

# check health
@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

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
                    "category": "Food",
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
    {'action': {'command': 'TRANSFER', 'params': {'receiver': 'Minh', 'amount': '300000', 'msg': None, 'category': 'Food'}}}

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Cuong", "content": "Tao muốn chuyển mỗi đứa 800k tiền mừng năm mới."},
    ...     ]
    ... }).json()
    {'action': {'command': 'TRANSFER_TO_EACH_USERS', 'params': {'amount_each': '800000', 'msg': 'tiền mừng năm mới', 'category': 'Food'}}}

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

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "Compare Bank of America, Coca Cola, and Apple"},
    ...     ]
    ... }).json()
    {
        'action': {
            'command': 'ASK_ASSISTANT',
            'params': {
                'chart': {
                    'type': 'compare',
                    'code': ['BAC', 'KO', 'AAPL'],
                    'name': ['Bank of America', 'Coca Cola', 'Apple'],
                    'period': '1-year',
                    'iframeLink': '/iframe/chart/compare?code=BAC,KO,AAPL&period=1-year',
                },
            },
        },
        'message': {'role': 'assistant', 'content': 'I have done the research for you and compared these investments across Volatility and Returns over a 1-year period.'},
        'suggestions': []
    }

    >>> requests.post('http://localhost:5000/api/chat', json={
    ...     "messages": [
    ...         {"user": "Minh", "content": "I own Amazon. What is their earning per share?"},
    ...     ]
    ... }).json()
    {
        'action': {
            'command': 'ASK_ASSISTANT',
            'params': {
                'chart': {
                    'type': 'earnings',
                    'code': ['AMZN'],
                    'name': ['Amazon'],
                    'period': '1-year',
                    'iframeLink': '/iframe/chart/earnings?code=AMZN&period=1-year',
                },
            },
        },
        'message': {'role': 'assistant', 'content': 'Here is a chart that compares the estimated vs the reported earnings per share:'},
        'suggestions': []
    }
    """
    logging.info(f"Received request: {request.json}")
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
    if not messages or messages[-1]['content'].strip() == '':
        bot_response, suggestions = ask_assistant(messages)
        return jsonify({
            'message': {
                'role': 'assistant', 'content': bot_response
            },
            'action': {
                'command': 'ASK_ASSISTANT',
                'params': {}
            },
            'suggestions': suggestions
        })

    logging.info(f"All Messages: {messages}")
    print(f'====================')

    intention = dectect_user_intention(messages)

    logging.info(f"Intention: {intention}")

    if intention == 'NO_SYSTEM_ACTION':
        bot_response, suggestions = match_question(messages)

        if bot_response:
            return jsonify({
                'message': {
                    'role': 'assistant', 'content': bot_response
                },
                'action': {
                    'command': 'ASK_ASSISTANT',
                    'params': {}
                },
                'suggestions': suggestions
            })

        return jsonify({
            'action': {
                'command': 'NO_ACTION',
                'params': {}
            },
            'message': {
                'role': 'assistant',
                'content': answer_I_dont_know_multilingual(messages)
            }
        })
    
    elif intention == 'ASK_ASSISTANT':
        bot_response, suggestions = ask_assistant(messages)
        
        logging.info(f"Bot_response: {bot_response}")

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
        payload = ensemble_get_action_params(messages, action='TRANSFER')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'TRANSFER',
                    'params': payload
                },
                'message': {
                    'role': 'assistant', 'content': get_response_message(payload, action='TRANSFER')
                },
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
        payload = ensemble_get_action_params(messages, action='TRANSFER_TO_EACH_USERS')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'TRANSFER_TO_EACH_USERS',
                    'params': payload
                },
                'message': {
                    'role': 'assistant', 'content': get_response_message(payload, action='TRANSFER_TO_EACH_USERS')
                },
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
        payload = ensemble_get_action_params(messages, action='CREATE_CHAT_GROUP')
        if isinstance(payload, dict):
            res = {
                'action': {
                    'command': 'CREATE_CHAT_GROUP',
                    'params': payload
                },
                'message': {
                    'role': 'assistant', 'content': get_response_message(payload, action='CREATE_CHAT_GROUP')
                },
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
    elif intention == 'VIEW_USER_ACCOUNT_REPORT':
        res = {
            'action': {
                'command': 'VIEW_USER_ACCOUNT_REPORT',
                'params': {
                    'user': messages[-1]['user']
                }
            }
        }
    else:
        raise Exception(f"Unknown intention: {intention}")
    
    logging.info(f"Response: {res}")
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
