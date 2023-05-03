import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_action_params_chatgpt_api, generate_general_call_chatgpt_api
from utils.logger import setup_logging_display_only, pprint, print
import re

def get_action_params(
        messages: List[Dict[str, str]],
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
    ) -> Union[Dict[str, str], str]:
    """
    Get action parameters from conversation history and user's intention.
    If the action parameters are not enough, then return normal message (str)
    If the action parameters are enough, then return action parameters (Dict[str, str])

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.
        action (Literal["TRANSFER", "CREATE_CHAT_GROUP"]): User's intention, which is one of "TRANSFER" or "CREATE_CHAT_GROUP".
    
    Returns:
        Dict[str, str]: Action parameters. If action is "TRANSFER", then the returned dictionary should have 2 keys: "receiver" and "amount". If action is "CREATE_CHAT_GROUP", then the returned dictionary should have 1 key: "members".
        request_message (str): Normal message. This message is returned when the action parameters are not enough.

    Example:
        >>> messages = [
        ...     {"user": "Minh", "content": "Tao muốn chuyển khoản cho Nam 6966 k VND tiền bún đậu"},
        ... ]
        >>> get_action_params(messages, action="TRANSFER")
        {
            "receiver": "Nam",
            "amount": "6966000",
            "msg": "bún đậu",
        }
        >>> messages = [    
        ...     {"user": "Minh", "content": "Chuyển mỗi người 100k."},
        ... ]
        >>> get_action_params(messages, action="TRANSFER_TO_EACH_USERS")
        Nội dung chuyển khoản là gì bạn nhỉ?
        >>> messages = [
        ...     {"user": "Minh", "content": "Tao muốn tạo nhóm chat với Nam và Lan."},
        ... ]
        >>> get_action_params(messages, action="CREATE_CHAT_GROUP")
        {
            "members": [
                "Nam",
                "Lan",
            ],
            "group_name": None, # group name can be None
        }
    """
    assert action in ["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"], f"Invalid action: {action}"
    messages = messages[-5:]
    params = {}
    if action == "TRANSFER":
        conversation = "\n".join([f"{message['user']}: {message['content']}" for message in messages])
        last_user = messages[-1]['user']
        model_input = f"""This is a financial assistant system that can TRANSFER money when user request. English and Vietnamese are supported. System's action syntax is: TRANSFER[<receiver>,<amount>|<message>]. Note that money abbreviation should be expanded without comma or dot. E.g. (30k=30000, 24tr=24000000, 5 nghìn=5000, tám chục nghìn=80000).
System will first output "REASONING: <thinking about user's intention, between 3 to 5 sentences, and analyze each param 'receiver', 'amount', and 'message'>". Then, system will output "CHECKLIST: " and then tick a checklist (using [x]) for each param:
[ ] receiver (need to be real username)
[ ] amount (need to be number)
[ ] message (at least 2 words, same language as User's request)
Then, if any of the param is missing, e.g. user did not explicitly mention receiver's username, then system will follows with "RESULT: NOT_ENOUGH_PARAMS". "ENOUGH_PARAMS" otherwise.
If RESULT is NOT_ENOUGH_PARAMS, then system will output a response "RESPONSE: ..." asking user to provide more information. Note that system should response in the same language as User's question.
If RESULT is ENOUGH_PARAMS, then system will output the system action "ACTION: TRANSFER[...]"
-- Conversation --
{conversation}
-- System analyzing {last_user}'s request --
REASONING:"""
        print("Model input: \n", model_input)
        output = generate_general_call_chatgpt_api(
            inputs=model_input,
            temperature=1,
            max_tokens=256,
        )
        print("Model output: \n", output)

        result = re.search(r"RESULT: (.*)", output).group(1)
        if result == "NOT_ENOUGH_PARAMS":   
            return output.split("RESPONSE: ")[1].strip()

        assert result == "ENOUGH_PARAMS", f"Invalid result: {result}"
        action_params = output.split("ACTION: ")[1].strip()
        params["receiver"] = action_params.split("|")[0].split("[")[1].split(",")[0].strip()
        params["amount"] = action_params.split("|")[0].split("[")[1].split(",")[1].strip()
        msg = action_params.split("[")[1].split("|")[1:]
        msg = "|".join(msg).split("]")[0].strip()
        if msg.lower() == "null" or msg.lower() == "none" or msg == "":
            raise Exception("Message is empty")
        else:
            params["msg"] = msg

    elif action == "CREATE_CHAT_GROUP":
        conversation = "\n".join([f"{message['user']}: {message['content']}" for message in messages])
        last_user = messages[-1]['user']
        model_input = f"""This is an assistant system that can CREATE_CHAT_GROUP when user request. English and Vietnamese are supported. System's action syntax is: CREATE_CHAT_GROUP[<user_comma_separated>|<group_name (nullable)>]. System will first output "REASONING: <thinking about user's intention, between 30-50 words, and analyze each param 'user_comma_separated' and 'group_name'>". Then, system will output "CHECKLIST: " and then tick a checklist (using [x]) for each param:
[ ] user_comma_separated (need to be a list of username with comma separated)
[ ] group_name (Did user explicitly mention the group name?)
Then, if user did not explicitly mention the list of users, then system will follows with "RESULT: NO_USERS". "OK" otherwise.
If RESULT is NO_USERS, then system will output a response "RESPONSE: ..." asking user to provide user list. Note that system should response in the same language as User's question.
If RESULT is OK, then system will output the system action "ACTION: CREATE_CHAT_GROUP[...]"
-- Conversation --
{conversation}
-- System analyzing {last_user}'s request --
REASONING:"""
        print("Model input: \n", model_input)
        output = generate_general_call_chatgpt_api(
            inputs=model_input,
            temperature=1,
            max_tokens=256,
        )
        print("Model output: \n", output)

        result = re.search(r"RESULT: (.*)", output).group(1)
        if result == "NO_USERS":   
            return output.split("RESPONSE: ")[1].strip()

        assert result == "OK", f"Invalid result: {result}"
        action_params = output.split("ACTION: ")[1].strip()
        params["members"] = action_params.split("|")[0].split("[")[1].split(",")
        group_name = action_params.split("[")[1].split("|")[1:]
        group_name = "|".join(group_name).split("]")[0].strip()
        if group_name.lower() == "null" or group_name.lower() == "none" or group_name == "":
            raise Exception("Group name is empty")
        else:
            params["group_name"] = group_name

    elif action == "TRANSFER_TO_EACH_USERS":
        conversation = "\n".join([f"{message['user']}: {message['content']}" for message in messages])
        last_user = messages[-1]['user']
        model_input = f"""This is a financial assistant system that can TRANSFER_TO_EACH_USERS money when user request. English and Vietnamese are supported. System's action syntax is: TRANSFER_TO_EACH_USERS[<amount>|<message>]. Note that money abbreviation should be expanded without comma or dot. E.g. (30k=30000, 24tr=24000000, 5 nghìn=5000, tám chục nghìn=80000).
System will first output "REASONING: <thinking about user's intention, between 30-50 words, and analyze each param 'amount' and 'message'>". Then, system will output "CHECKLIST: " and then tick a checklist (using [x]) for each param:
[ ] amount (need to be number)
[ ] message (Is the purpose of the transaction specified?)
Then, if any of the param is missing, e.g. user did not explicitly mention the transaction purpose, then system will follows with "RESULT: NOT_ENOUGH_PARAMS". "ENOUGH_PARAMS" otherwise.
If RESULT is NOT_ENOUGH_PARAMS, then system will output a response "RESPONSE: ..." asking user to provide more information. Note that system should response in the same language as User's question.
If RESULT is ENOUGH_PARAMS, then system will output the system action "ACTION: TRANSFER_TO_EACH_USERS[...]"
REASONING:-- Conversation --
{conversation}
-- System analyzing {last_user}'s request --
REASONING:"""
        print("Model input: \n", model_input)
        output = generate_general_call_chatgpt_api(
            inputs=model_input,
            temperature=1,
            max_tokens=256,
        )
        print("Model output: \n", output)

        result = re.search(r"RESULT: (.*)", output).group(1)
        if result == "NOT_ENOUGH_PARAMS":   
            return output.split("RESPONSE: ")[1].strip()

        assert result == "ENOUGH_PARAMS", f"Invalid result: {result}"
        action_params = output.split("ACTION: ")[1].strip()
        params["amount_each"] = action_params.split("|")[0].split("[")[1].split(",")[0].strip()
        msg = action_params.split("[")[1].split("|")[1:]
        msg = "|".join(msg).split("]")[0].strip()
        if msg.lower() == "null" or msg.lower() == "none" or msg == "":
            raise Exception("Transaction message is empty")
        else:
            params["msg"] = msg
    return params


if __name__ == "__main__":
    setup_logging_display_only()
    out = get_action_params(messages=[
        {"user": "Minh", "content": "Hello, I want to check my account balance"},
        {"user": "Lan", "content": "Ready for a party?"},
        {"user": "Minh", "content": "Yes, I am ready."},
        {"user": "Minh", "content": "I want to transfer 3289723 VND to Hung."},
        {"user": "Cường", "content": "Chuyển quà sinh nhật mỗi cháu 400k"},
        {"user": "Minh", "content": "Chuyển Alisa ba chục nghìn tiền bún đậu"},
        {"user": "Minh", "content": "I want to transfer 3289723 VND to Hung với lời nhắn là 'Chúc mừng sinh nhật nhé, nhớ học giỏi'."},
        {"user": "Hung", "content": "I want to create a chat group for Minh, me, Lan, and Cường named 'Party| this sunday'."},
    ], action="CREATE_CHAT_GROUP")
    print("Output: ", out)
        