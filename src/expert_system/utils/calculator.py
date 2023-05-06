from typing import Literal, Dict, List, Tuple, Union, Any, Optional
import re

def get_income(model_output: str) -> Optional[float]:
    """
    Get income from model output.
    
    Args:
        model_output (str): Model output.
        
    Returns:
        income (float): Income.
        
    Examples:
    >>> get_income("User income is SET_INCOME[5000000] so that blah")
    5000000.0
    """
    income = re.search(r"SET_INCOME\[(\d+)\]", model_output)
    # remove all non-digit characters, e.g. 5,000,000 -> 5000000
    if income:
        income = income.group(1)
        income = re.sub(r"\D", "", income)
        income = float(income)
        return income
    return None

def calculate(model_output: str, income: Optional[float]) -> str:
    """
    Calculate money management.
    
    Args:
        model_output (str): Model output.
        income (float): Income.
        
    Returns:
        result (str): Result.
        
    Examples:
    >>> calculate("Theo mình thì bạn nên dành CALCULATE[income*55/100] cho các chi tiêu cần thiết", income=5000000)
    'Theo mình thì bạn nên dành 2750000.0 cho các chi tiêu cần thiết'
    """

    if income:
        result = model_output
        result = re.sub(r"CALCULATE\[(\d+)\]", lambda match: format_vnd(float(match.group(1))), result)
        result = re.sub(r"CALCULATE\[(\d+)([+-/*])(\d+)\]", lambda match: format_vnd(eval(f"{match.group(1)}{match.group(2)}{match.group(3)}")), result)
        result = re.sub(r"CALCULATE\[income\*(\d+)([+-/*])(\d+)\]", lambda match: format_vnd(eval(f"{income}*{match.group(1)}{match.group(2)}{match.group(3)}")), result)
        return result
    else:
        result = model_output
        result = re.sub(r"CALCULATE\[(\d+)\]", lambda match: format_vnd(float(match.group(1))), result)
        result = re.sub(r"CALCULATE\[(\d+)([+-/*])(\d+)\]", lambda match: format_vnd(eval(f"{match.group(1)}{match.group(2)}{match.group(3)}")), result)
        result = re.sub(r"CALCULATE\[income\*(\d+)([+-/*])(\d+)\]", lambda match: f"{match.group(1)}%", result)
        return result
        

def format_vnd(number: float) -> str:
    if number >= 1000000000:
        return '{:.1f} tỷ'.format(number / 1000000000)
    elif number >= 1000000:
        return '{:.1f} triệu'.format(number / 1000000)
    elif number >= 1000:
        return '{:.0f} nghìn'.format(number / 1000)
    else:
        return '{:.0f}'.format(number)

if __name__ == "__main__":
    print(calculate("Theo mình thì bạn nên dành CALCULATE[income*55/100] cho các chi tiêu cần thiết", income=None))
    # print(calculate("OK. Theo mình thì bạn nên dành CALCULATE[income*55/100] cho các chi tiêu cần thiết, CALCULATE[income*10/100] cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành CALCULATE[income*5/100] cho việc từ thiện.", income=5000000))
#     print(get_income("""User is telling their income SET_INCOME[12000000], which still is in the scope of money management.
# Current stage: Stage 2
# - Assistant: OK. Theo mình thì bạn nên dành CALCULATE[income*55/100] cho các chi tiêu cần thiết, CALCULATE[income*10/100] cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành CALCULATE[income*5/100] cho việc từ thiện.
# """))