import requests
from flask import jsonify, request
from utils.entities import Conversation
from utils.prompt_factory import MODE
from utils.model_api import generate

def mock_app(app):
    @app.route('/mock/chat', methods=['POST'])
    def chat_mock():
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

        assistant_answer = "Sure Onii-chan 🥺! I will send Minh 100$ for the pizza."
        
        print(f"Assistant_answer: {assistant_answer}")

        conversation.command = MODE['action']

        next_input = conversation.prepare_model_input() + assistant_answer

        print(f"Next_input: {next_input}")

        raw_action = "Action:TRANSFER_MONEY[amount=100, from=Alex, to=Minh]"

        action = conversation.extract_action(raw_action)

        return jsonify({
            'message': {
                'role': 'assistant', 'content': assistant_answer
            },
            'action': action
        })

    @app.route('/mock/detect-intent', methods=['POST'])
    def detect_intent_mock():
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