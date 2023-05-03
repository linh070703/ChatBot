from typing import Dict, List, Tuple, Union, Literal, Any
from utils.logger import print

STAGE_MESSAGE = [
    "Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?",
    "OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện."
]

PROMPT = """This is a Personal Finance Assistant system that can provide advices for user based on the pre-defined script. English and Vietnamese are supported. After user's response, system will display the current stage of the conversation. There are 3 stages in total. If user's message intention is not match the response expectation in the pre-defined script, system will display the current stage of the conversation as "BREAK"

# Script:
Stage 1:
Expectation: User ask about money management plan.
- User: Tạo kế hoạch ngân sách hàng tháng.
Current stage: Stage 1
Stage 2:
Expectation: User response with their income.
- Assistant: Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?
- User: 5 triệu
Current stage: Stage 2
Stage 3:
Expectation: User ask more detail about why.
- Assistant: OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện.
- User: Vì sao mình nên dành từng đó cho các chi tiêu cần thiết?
Current stage: Stage 3

# Real conversation:
- User: Tạo kế hoạch ngân sách hàng tháng.
- Assistant: Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?
"""
# - User: 
# Current stage: 
# """

def is_money_management_question(message: str) -> bool:
    """
    Lên kế hoạch tiết kiệm.

    Args:
        message (str): Message from user.
    
    Returns:
        bool: True if the message is about money management, False otherwise.
    
    Example:
    >>> is_money_management_question("Tôi muốn lên kế hoạch tiết kiệm.")
    True
    >>> is_money_management_question("Tính toán kế hoạch tiết kiệm mục tiêu của bạn.")
    True
    """

    return (
        "kế hoạch tiết kiệm" in message 
        or "kế hoạch ngân sách" in message
        or "kế hoạch chi tiêu" in message
        or "ngân sách chi tiêu" in message
    )


def money_management_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Response (str): Response from the assistant.
        Suggestions (List[str]): List of suggestions for next user's message.
    
    Example:
    >>> money_management_suggestion([{"user": "user", "content": "Tạo kế hoạch ngân sách hàng tháng."}])
    ("Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?", [])
    >>> money_management_suggestion([
    ...    {"user": "Alex", "content": "Tạo kế hoạch ngân sách hàng tháng."},
    ...    {"user": "assistant", "content": "Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
    ...    {"user": "Alex", "content": "5 triệu"}
    ... ])
    ("OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện.", [])
    >>> money_management_suggestion([
    ...    {"user": "Alex", "content": "Tạo kế hoạch ngân sách hàng tháng."},
    ...    {"user": "assistant", "content": "Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
    ...    {"user": "Alex", "content": "5 triệu"}
    ...    {"user": "assistant", "content": "OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện."},
    ...    {"user": "Alex", "content": "Vì sao mình nên dành từng đó cho các chi tiêu cần thiết?"}
    ... ])
    """
    ...

def get_current_stage(messages: List[Dict[str, str]]) -> Literal['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'BREAK']:
    ...
