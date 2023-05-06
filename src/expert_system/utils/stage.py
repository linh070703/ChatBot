from typing import Literal, Dict, List, Tuple, Union, Any, Optional
from utils.logger import setup_logging_display_only, print
import logging
import re

def get_current_stage(model_output: str) -> Literal['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'BREAK']:
    """
    Get current stage of the conversation.
    
    Args:
        model_output (str): Model output.
        
    Returns:
        current_stage (str): Current stage of the conversation.
    
    Examples:
    >>> get_current_stage(" User is asking about the reason why they should spend that amount of money on each category, which is still in the scope of money management.\nCurrent stage: Stage 3\n- Assistant: Việc dành 55% cho chi tiêu cần thiết là để đảm bảo rằng bạn có đủ tiền để chi trả các chi phí cố định hàng tháng và đảm bảo cuộc sống hàng ngày của mình không bị ảnh hưởng bởi thiếu hụt tài chính. Nếu bạn không thể đáp ứng các chi phí cơ")
    'Stage 3'
    """
    current_stage = re.search(r"Current stage: (Stage \d)", model_output).group(1)
    current_stage = " ".join(current_stage.split())
    logging.info(f"Current stage: {current_stage}")
    if current_stage == "Stage 4":
        return "BREAK"
    
    # catch BREAK
    if "BREAK" in model_output:
        return "BREAK"

    return current_stage