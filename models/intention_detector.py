import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_action_chatgpt_api
from utils.logger import setup_logging_display_only

PROMPT = """This is a user's intention detecting system. This system is able to detect intention of users in conversation history and direct message. English and Vietnamese are supported. There are 5 possible user's intentions: CHECK_BALANCE, TRANSFER, CREATE_CHAT_GROUP, ASK_ASSISTANT, NO_SYSTEM_ACTION."""
# Minh: Tao muốn chuyển khoản cho Nam 300k.
# Minh's intention: TRANSFER"""

def dectect_user_intention(
        messages: List[Dict[str, str]],
    ) -> Literal["CHECK_BALANCE", "TRANSFER", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]:
    """
    Detect user's intention from conversation history.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "message". "user" is the name of user who sent the message. "message" is the message sent by the user.

    Returns:
        Literal["CHECK_BALANCE", "TRANSFER", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]: User's intention
    
    Example:
        >>> messages = [
        ...     {"user": "Minh", "message": "Hello, I want to check my account balance"},
        ... ]
        >>> dectect_user_intention(messages)
        "CHECK_BALANCE"
    """
    conversation = "\n".join([f"{message['user']}: {message['message']}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"{PROMPT}\n{conversation}\n{last_user}'s intention: "
    print("Model input: \n", model_input)
    output = generate_action_chatgpt_api(model_input)
    return output


if __name__ == "__main__":
    setup_logging_display_only()
    out = dectect_user_intention(messages=[
        {"user": "Minh", "message": "Hello, I want to check my account balance"},
        {"user": "Lan", "message": "Ready for a party?"},
        {"user": "Minh", "message": "Yes, I am ready."},
        {"user": "Hung", "message": "I want to create a chat group with Minh and Lan."},
    ])
    print("Output: ", out)
        