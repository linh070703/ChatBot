import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_general_call_chatgpt_api
from utils.logger import setup_logging_display_only, print
import logging
import re

PROMPT = """This is a user's intention detecting system. This system is able to detect intention of users in conversation history and direct message. English and Vietnamese are supported. There are 6 possible user's intentions: CHECK_BALANCE, VIEW_USER_ACCOUNT_REPORT, TRANSFER, TRANSFER_TO_EACH_USERS, CREATE_CHAT_GROUP, ASK_ASSISTANT, NO_SYSTEM_ACTION"""
# Minh: Tao muốn chuyển khoản cho Nam 300k.
# Minh's intention: TRANSFER"""

def dectect_user_intention(
        messages: List[Dict[str, str]],
    ) -> Literal["CHECK_BALANCE", "VIEW_USER_ACCOUNT_REPORT", "TRANSFER", "TRANSFER_TO_EACH_USERS", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]:
    """
    Detect user's intention from conversation history.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Literal["CHECK_BALANCE", "VIEW_USER_ACCOUNT_REPORT", "TRANSFER", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"]: User's intention
    
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
    output = generate_general_call_chatgpt_api(
        inputs=model_input,
        temperature=0,
        top_p=1.0,
        max_tokens=12,
        stop=(r"]",),
    )
    intent = " ".join(output.split()).strip()
    assert intent in ["CHECK_BALANCE", "VIEW_USER_ACCOUNT_REPORT", "TRANSFER", "TRANSFER_TO_EACH_USERS", "CREATE_CHAT_GROUP", "ASK_ASSISTANT", "NO_SYSTEM_ACTION"], f"Invalid intent: {intent}"

    if intent == "VIEW_USER_ACCOUNT_REPORT":
        conversation = "\n".join([f"{' '.join(message['user'].split())}: {' '.join(message['content'].split())}" for message in messages])
        last_user = messages[-1]['user']
        model_input = f"""{conversation}
{last_user}'s intention: {intent}

Critique Request: 
Is {last_user} want to view his/her own account report? []
Is {last_user} want to view other user's account report? []
Is {last_user} want to view external report about any companies in the world? []

After ticking above checkboxes, system should followed by "Reason: " and then conclude the revision by "Conclusion: " + "Correct" or "Incorrect"

--- System's Analyzing ---
Critique:
Is {last_user} want to view his/her account report?"""
        logging.info(f"Model input: \n{model_input}")
        output = generate_general_call_chatgpt_api(
            inputs=model_input,
            temperature=0,
            top_p=1.0,
            max_tokens=512,
        )
        logging.info(f"Model output: \n{output}")
        out = " ".join(output.split()).strip()
        conclusion = re.search(r"Conclusion: (.*)", out)
        tick1 = True
        if out.startswith("[ ]") or out.startswith("[]"):
            tick1 = False
        tick2 = True
        tick2_context = re.search(r"Is (.*) want to view other user's account report\? \[(.*)\]", out)
        if tick2_context:
            tick2 = False if tick2_context.group(2) == " " or tick2_context.group(2) == "" else True
        tick3 = True
        tick3_context = re.search(r"Is (.*) want to view external report about any companies in the world\? \[(.*)\]", out)
        if tick3_context:
            tick3 = False if tick3_context.group(2) == " " or tick3_context.group(2) == "" else True
        logging.info(f"tick1: {tick1}, tick2: {tick2}, tick3: {tick3}")
        if tick1 and not tick2 and not tick3:
            logging.info(f"Ticked 1st checkbox, unticked 2nd and 3rd checkboxes, conclusion: Correct")
            intent = "VIEW_USER_ACCOUNT_REPORT"
        else:
            intent = "NO_SYSTEM_ACTION"
            
    return intent


if __name__ == "__main__":
    setup_logging_display_only()
    out = dectect_user_intention(messages=[
        {"user": "Cường", "content": "Tôi muốn được tư vấn về việc trả nợ."},
    ])
    logging.info(f"Output: {out}")
        