from typing import Literal, Dict, List, Tuple, Union, Any, Optional
import pandas as pd
import logging

def calculate_economical_table(
        income: float,
        target_money: Optional[float],
        target_time: Optional[int]
    ) -> Tuple[Dict[str, float], str]:
    """
    Calculate economical table.
    
    Args:
        income (float): Income.
        target_money (float): Target money.
        target_time (int): Target time.
        
    Returns:
        answer (Dict[str, float]): Answer.
        economical_table (str): Economical table in markdown format.
    """
    df = _calculate_economical_table(income, target_money, target_time)
    
    if target_money and target_time:
        logging.warning(f"Both target money and target time are extracted from model output")

    if target_money:
        # get last row
        last_row = df.iloc[-1]
        time = last_row["STT năm"]
        return {
            'time': time,
        }, df.to_markdown()
            
    
    if target_time:
        # get last row
        last_row = df.iloc[-1]
        money = last_row["Tổng lượng tiết kiệm"]
        return {
            'money': money,
        }, df.to_markdown()
        
    

def _calculate_economical_table(
        income: float,
        target_money: Optional[float],
        target_time: Optional[int]
    ) -> pd.DataFrame:
    """
    Calculate economical table.
    
    Args:
        income (float): Income.
        target_money (float): Target money.
        target_time (int): Target time.
        
    Returns:
        economical_table (pd.DataFrame): Economical table.
    """
    # STT năm | Thu nhập  | %  tiết kiệm mỗi tháng | Lượng tiết kiệm mỗi năm | Tổng lượng tiết kiệm  | Lãi suất tiết kiệm của ngân hàng
    # 1|    5,000,000.00|   10.00%  |  500,000.00|   6,000,000.00|  480,000.00
    # 2|    5,000,000.00|   10.00%  |  525,000.00|   12,780,000.00|  1,022,400.00
    # n|    5,000,000.00|   10.00%  |  Thu nhập * 10.00% |   Tổng lượng tiết kiệm + Lượng tiết kiệm mỗi năm * 12 + previous Lãi suất tiết kiệm của ngân hàng|  Tổng lượng tiết kiệm * 0.08

    rows = []
    if target_time:
        for i in range(1, target_time + 1):
            if i == 1:
                rows.append([i, income, 10, income * 0.1, income * 0.1, income * 0.1 * 0.08])
            else:
                rows.append([i, income, 10, income * 0.1, income * 0.1 + rows[i - 2][4] * 12, (income * 0.1 + rows[i - 2][4] * 12) * 0.08])

    if target_money:
        i = 1
        while True:
            if i == 1:
                rows.append([i, income, 10, income * 0.1, income * 0.1, income * 0.1 * 0.08])
            else:
                rows.append([i, income, 10, income * 0.1, income * 0.1 + rows[i - 2][4] * 12, (income * 0.1 + rows[i - 2][4] * 12) * 0.08])
            if rows[-1][4] >= target_money:
                break
            i += 1
    
    economical_table = pd.DataFrame(rows, columns=["Số năm", "Thu nhập", "% tiết kiệm mỗi tháng", "Lượng tiết kiệm mỗi năm", "Tổng lượng tiết kiệm", "Lãi suất tiết kiệm của ngân hàng"])
    return economical_table