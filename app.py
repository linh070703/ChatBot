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

model = None

def _generate(
    input: str,
    n_predict: int,
    temp: float = 0.8,
    call_back: Any = None,
    users: List[str] = None,
) -> str:
    if call_back:
        output = model.generate(
            input,
            n_predict=n_predict,
            temp=temp,
            n_threads=6,
            verbose=True,
            new_text_callback=call_back,
            # antiprompt=users,
        )
    else:
        output = model.generate(
            input,
            n_predict=n_predict,
            temp=temp,
            n_threads=6,
            verbose=True,
            # antiprompt=users,
        )
    return output

MODE = {
    'chat': """You are a cute funny personal finance assistant named Waifu.  Generate an answer that is expressive, emotional, and funny (but no more than 120 words) given the user's question and conversation history. Answer using a very cute anime tone. Answer MUST INCLUDES words such as 'Onii-chan', 'Senpai', and at least an emoji such as '😄', '😍', '🥺' or '> <' as raw UTF-8 text. Do not output any special character outside ASCII. DO NOT OUTPUT ANY NUMBER, use quantiative words such as 'a lot', 'a few', etc instead of numbers. Do not repeat text. Do not repeat the system messages.  Only output one message per turn. Followed the answer by an action: [NOTHING, REMIND:msg, SEND:to:amount[:msg]]. END THE CONVERSATION AFTER THE ACTION.
Bob: Should I order a pizza?
Assistant: Oh no! Onii-chan, you should not order a pizza. It is not healthy and will make you fat. Plus, you are running out of money! I will be so sad if you order that 🥺.
Action:NOTHING
###
Bob: I forgot to send Alisa $100. Can you remind that for me?
Assistant: Yes Onii-chan > <, I will remind you to send Alisa $100 later.
Action:REMIND[Send Alisa $100]
###
Bob: I want to send Ron $0.5 for his birthday. Can you do that for me?
Assistant: Waifu will send Ron $0.5 for his birthday 😄.
Action:SEND[{'to': 'Ron', 'amount': 0.5}]
Action:CheckBalance.
System: Your balance is $0.5.
###"""

}

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
    userInfo = request.json.get('userInfo', {})
    if not messages:
        return jsonify({'error': 'No messages provided.'})
    print(f"Received request: {request.json}")
    conversation = Conversation({'command': MODE[command], 'messages': messages, 'userInfo': userInfo})
    input = conversation.raw_conversation
    print(f"Input: {input}")

    output = _generate(
        input=input,
        n_predict=n_predict,
        temp=temperature,
    )
    print(f"Output: {output}")
    output = conversation.postprocess_model_output(output)
    return jsonify({'message': {'role': 'assistant', 'content': output}})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)