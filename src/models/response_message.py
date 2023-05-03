from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from utils.logger import print
import logging

def get_response_message(
        params: Dict[str, str],
        action: Literal['TRANSFER', 'TRANSFER_TO_EACH_USERS', 'CREATE_CHAT_GROUP']
    ) -> str:
    """
    Get response message from assistant.
    """
    if action == 'TRANSFER':
        return f"Đã chuyển {params['amount']} cho {params['receiver']} với nội dung \"{params['msg']}\"."
    elif action == 'TRANSFER_TO_EACH_USERS':
        return f"Đã chuyển cho mỗi người trong nhóm {params['amount_each']} với nội dung \"{params['msg']}\"."
    elif action == 'CREATE_CHAT_GROUP':
        if params['group_name']:
            return f"Đã tạo nhóm chat {params['group_name']} thành công."
        else:
            return f"Đã tạo nhóm chat thành công."