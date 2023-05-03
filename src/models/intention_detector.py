import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_action_chatgpt_api
from utils.logger import setup_logging_display_only, print
import logging

PROMPT = """This is a user's intention detecting system. This system is able to detect intention of users in conversation history and direct message. English and Vietnamese are supported. There are 6 possible user's intentions: CHECK_BALANCE, TRANSFER, TRANSFER_TO_EACH_USERS, CREATE_CHAT_GROUP, ASK_ASSISTANT, NO_SYSTEM_ACTION."""
# Minh: Tao muốn chuyển khoản cho Nam 300k.
# Minh's intention: TRANSFER"""

def dectect_user_intention(
        messages: List[Dict[str, str]],
    ) -> Literal["CHECK_BALANCE", "TRANSFER", "TRANSFER_TO_EACH_USERS", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]:
    """
    Detect user's intention from conversation history.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Literal["CHECK_BALANCE", "TRANSFER", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]: User's intention
    
    Example:
        >>> messages = [
        ...     {"user": "Minh", "content": "Hello, I want to check my account balance"},
        ... ]
        >>> dectect_user_intention(messages)
        "CHECK_BALANCE"
    """
    assert len(messages) > 0, "Conversation history must not be empty."
    messages = messages[-5:]
    conversation = "\n".join([f"{' '.join(message['user'].split())}: {' '.join(message['content'].split())}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"{PROMPT}\n{conversation}\n{last_user}'s intention: "
    logging.info(f"Model input: \n{model_input}")
    output = generate_action_chatgpt_api(model_input)
    intent = " ".join(output.split()).strip()
    assert intent in ["CHECK_BALANCE", "TRANSFER", "TRANSFER_TO_EACH_USERS", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"], f"Invalid intent: {intent}"
    return intent


if __name__ == "__main__":
    setup_logging_display_only()
    out = dectect_user_intention(messages=[
        {"user": "Cường", "content": "Tôi muốn được tư vấn về việc trả nợ."},
    ])
    logging.info(f"Output: {out}")
        