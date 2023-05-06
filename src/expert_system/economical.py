import os
import sys

sys.path.append("/home/thaiminhpv/Workspace/Code/FUNiX-ChatGPT-Hackathon/Chatbot/Chatbot/src/")

from typing import Dict, List, Tuple, Union, Literal, Any
from utils.logger import print, setup_logging_display_only
from utils.model_api import generate_general_call_chatgpt_api
from utils.logger import print
from expert_system.utils.stage import get_current_stage
from expert_system.utils import calculator
from expert_system.utils import spreadsheet
import re
import logging

def is_economical_question(message: str) -> bool:
    return "tiết kiệm" in message

def economical_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Response (str): Response from the assistant.
        Suggestions (List[str]): List of suggestions for next user's message.
    
    Example:
    >>> money_management_suggestion([{"user": "user", "content": "Mình muốn được tư vấn về vấn đề tiết kiệm "}])
    ("Đối với tiết kiệm thì mình có thể giúp bạn tính xem bạn nên tích lũy trong bao lâu để có thể có được mức mong muốn, hoặc nếu bạn tiết kiệm trong 1 khoảng thời gian nhất định thì bạn có thể tiết kiệm được bao nhiêu.", [
        'Mình muốn được biết rằng trong bao lâu thì mình có thể tiết kiệm được 100 triệu đồng',
        'Mình muốn biết nếu mình tiết kiệm 20 năm thì sẽ có bao nhiêu'
    ])
    """
    messages = messages[-7:]
    
    conversation = "\n".join([f"- {' '.join(message['user'].split())}: {' '.join(message['content'].split())}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"""This is a Personal Finance Assistant system that can provide user advices based on the pre-defined script. English and Vietnamese are supported. There are 3 stages in total. After user's request, system will display the current stage of the conversation, followed by "Analyzing: " no more than 100 words. Finally, system will response to the user as in pre-defined script. If user's message intention is not match the response expectation in the pre-defined script, system will display the current stage of the conversation as "BREAK" and end the conversation. System can use calculator syntax as CALCULATE[30000*20/100] to calculate the result.

## Script:
### Stage 1:
Expectation: User ask about economical advice.
- User: Mình muốn được tư vấn về vấn đề tiết kiệm 
Analyzing: User is asking about how to save money.
Current stage: Stage 1
- Assistant: Đối với Tiết kiệm thì mình có thể giúp bạn tính xem bạn nên tích lũy trong bao lâu để có thể có được mức mong muốn, hoặc nếu bạn tiết kiệm trong 1 khoảng thời gian nhất định thì bạn có thể tiết kiệm được bao nhiêu.
### Stage 2:
Case 1:
    Expectation: User ask about how long to reach a certain amount of money.
    - User: Mình muốn được biết rằng trong bao lâu thì mình có thể tiết kiệm được 100 triệu đồng
    Analyzing: User is asking about how much time it takes to save 100 million VND.
    Current stage: Stage 2
    - Assistant: Thu nhập hàng tháng của bạn là bao nhiêu?
    - User: 8 triệu đồng
    Analyzing: User is telling their income SET_INCOME[8000000]. Recall that user's request is how much time it takes to save 100 million VND SET_TARGET_MONEY[100000000].
    Current stage: Stage 3
    - Assistant: Ok. Dựa trên những thông tin bạn đưa ra, nếu như mỗi tháng bạn dành 10% thu nhập để tiết kiệm, hàng năm bạn được tăng 5% lương và lãi suất tiết kiệm của ngân hàng là 8%. Thì sau khoảng {{time}} năm thì bạn có thể tiết kiệm được 100 triệu đồng. Bạn có thể tham khảo thêm tại bảng sau:
    {{INSERT_TABLE}}
Case 2:
    Expectation: User ask about how much money can be saved in a certain amount of time.
    - User: Mình muốn biết nếu mình tiết kiệm 20 năm thì sẽ có bao nhiêu
    Analyzing: User is asking about how much money can be saved in 20 years.
    Current stage: Stage 2
    - Assistant: Thu nhập hàng tháng của bạn là bao nhiêu?
    - User: 8 triệu đồng 
    Analyzing: User is telling their income SET_INCOME[8000000]. Recall that user's request is how much money can be saved in 20 years SET_TARGET_TIME[20].
    Current stage: Stage 3
    - Assistant: Ok. Dựa trên những thông tin bạn đưa ra, nếu như mỗi tháng bạn dành 10% thu nhập để tiết kiệm, hàng năm bạn được tăng 5% lương và lãi suất tiết kiệm của ngân hàng là 8%. Thì sau 20 năm bạn sẽ có {{money}}.
    {{INSERT_TABLE}}

## Real conversation:
...
{conversation}
Analyzing:"""
    logging.info(f"Model input: \n{model_input}")
    output = generate_general_call_chatgpt_api(
        inputs=model_input,
        temperature=0,
        max_tokens=256,
        stop=(f'- {last_user}:',)
    )
    logging.info(f"Model output: \n{output}")

    current_stage = get_current_stage(output)
    
    if current_stage == 'BREAK':
        return None, [] 
    
    response_message = output.split(current_stage)[-1].split('- Assistant:')[-1].split('Current stage:')[0].strip()
    response_message = " ".join(response_message.split())
    
    if current_stage == 'Stage 1':
        return response_message, [
            'Mình muốn được biết rằng trong bao lâu thì mình có thể tiết kiệm được 100 triệu đồng',
            'Mình muốn biết nếu mình tiết kiệm 20 năm thì sẽ có bao nhiêu'
        ]  
    if current_stage == 'Stage 2':
        return response_message, ['5 triệu']
    if current_stage == 'Stage 3':
        income = calculator.get_income(output)
        print(f"income: {income}")
        if not income:
            logging.warning(f"Cannot get income from model output: {output}")
        
        target_money = extract_target_money(output)
        print(f"target_money: {target_money}")
        target_time = extract_target_time(output)
        print(f"target_time: {target_time}")
        
        if target_money and target_time:
            logging.warning(f"Both target money and target time are extracted from model output: {output}")
            return response_message, []
        
        # case 1
        res, economical_table = spreadsheet.calculate_economical_table(income=income, target_money=target_money, target_time=target_time)
            
        if target_money:
            # replace '{{time}}' with res['time']
            response_message = response_message.replace('{time}', res['time'])
        if target_time:
            # replace '{{money}}' with res['money']
            response_message = response_message.replace('{money}', res['money'])
            
        # replace {{INSERT_TABLE}} with economical_table
        response_message = response_message.replace('{INSERT_TABLE}', economical_table)

        return response_message, []

def extract_target_money(output):
    target_money = re.search(r'SET_TARGET_MONEY\[(\d+)\]', output)
    if target_money:
        return target_money.group(1)
    return None

def extract_target_time(output):
    target_time = re.search(r'SET_TARGET_TIME\[(\d+)\]', output)
    if target_time:
        return target_time.group(1)
    return None
            

if __name__ == "__main__":
    setup_logging_display_only()
    out = economical_suggestion([
        {"user": "Alex", "content": "Tôi muốn được tư vấn về tài chính cá nhân."},
        {"user": "Assistant", "content": "Chào Alex, mình sẽ giúp bạn lên kế hoạch chi tiêu hàng tháng nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
        {"user": "Alex", "content": "12 triệu"},
        {"user": "Assistant", "content": "OK. Theo mình thì bạn nên dành 6 triệu 600 trăm cho các chi tiêu cần thiết, 1 triệu 200 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 600 nghìn cho việc từ thiện."},
        {"user": "Alex", "content": "Tạo sao lại để từ thiện nhỉ?"},
    ])
    print(f"Final output: {out}")